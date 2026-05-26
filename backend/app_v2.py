"""
ExamSensei API.

FastAPI app for the Indian competitive-exam mentor. Auth is delegated to
Supabase Auth (see backend/auth.py) — there are no register/login/refresh
endpoints here; the frontend talks to Supabase directly.

Designed for low-to-moderate traffic (tens to hundreds of concurrent users)
on Supabase Postgres + Render.
"""
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ai_models import AdaptiveMentor, TopicPrioritizer
from auth import get_current_active_user
from chatbot import ExamSenseiChatbot
from config import settings
from database import create_tables, get_db
from exceptions import (
    ExamSenseiException, bad_request, internal_error, not_found,
)
from logger import log_api_request, log_error, log_user_activity, logger, request_id_ctx
from models import Exam, Gamification, StudyPlan, User


# ---------------------------------------------------------------------------
# App + lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ExamSensei API...")
    create_tables()
    logger.info("Database tables created/verified")

    if settings.sentry_dsn:
        try:
            import sentry_sdk
            sentry_sdk.init(
                dsn=settings.sentry_dsn,
                environment=settings.environment,
                traces_sample_rate=1.0 if settings.environment == "development" else 0.1,
            )
            logger.info("Sentry monitoring initialized")
        except ImportError:
            logger.warning("SENTRY_DSN is set but sentry-sdk is not installed; skipping")
        except Exception as exc:  # noqa: BLE001 — never let monitoring crash boot
            logger.warning(f"Sentry init failed: {exc}")

    yield
    logger.info("Shutting down ExamSensei API...")


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="ExamSensei API",
    description="AI-Powered Competitive Exam Mentor System",
    version="1.0.0",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    lifespan=lifespan,
)

app.state.limiter = limiter


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Generate a request id, set it on the context, log timing + status."""
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    token = request_id_ctx.set(request_id)
    try:
        response = await call_next(request)
    finally:
        request_id_ctx.reset(token)
    duration = time.time() - start_time
    log_api_request(method=request.method, path=request.url.path, status_code=response.status_code)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duration:.4f}"
    return response


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

def _error_response(status_code: int, message: str, details: Optional[dict] = None) -> JSONResponse:
    """One envelope for every error response, mirroring exceptions._envelope."""
    return JSONResponse(
        status_code=status_code,
        content={"detail": {"message": message, "details": details or {}}},
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return _error_response(
        status.HTTP_429_TOO_MANY_REQUESTS,
        "Rate limit exceeded. Please try again later.",
        {"limit": str(exc.detail)},
    )


@app.exception_handler(ExamSenseiException)
async def examsensei_exception_handler(request: Request, exc: ExamSenseiException):
    log_error(exc, {"path": request.url.path})
    return _error_response(status.HTTP_400_BAD_REQUEST, exc.message, exc.details)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # HTTPException already has its own handler (registered by FastAPI) with
    # higher priority, but if for any reason one slips through, surface it
    # cleanly instead of remapping to 500.
    if isinstance(exc, HTTPException):
        detail = exc.detail
        if isinstance(detail, dict) and "message" in detail:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": detail},
                headers=getattr(exc, "headers", None),
            )
        return _error_response(exc.status_code, str(detail))

    log_error(exc, {"path": request.url.path})
    return _error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Internal server error",
        {"error": str(exc)} if settings.environment == "development" else {},
    )


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: Optional[str] = None
    current_stage: str
    career_paths: Optional[List[str]] = None
    active_exams: Optional[List[str]] = None
    is_verified: bool


class ExamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    body: str
    exam_type: str
    important_dates: Optional[Dict] = None


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class StudyPlanRequest(BaseModel):
    exam_code: str
    days_available: int = 90


class ProfileUpdate(BaseModel):
    """
    Whitelist of fields a user is allowed to update on their own profile.

    - First group writes into `User.preparation_profile` (JSON blob).
    - Second group writes directly to top-level User columns.
    """
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    study_hours_per_day: Optional[int] = None
    study_consistency: Optional[float] = None
    interests: Optional[List[str]] = None

    career_paths: Optional[List[str]] = None
    active_exams: Optional[List[str]] = None


# ---------------------------------------------------------------------------
# Auth (Supabase-only)
# ---------------------------------------------------------------------------

@app.get(f"{settings.api_prefix}/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Return the user row matching the Supabase JWT in the Authorization header."""
    return current_user


# ---------------------------------------------------------------------------
# Ownership helper
# ---------------------------------------------------------------------------

def _require_self(current_user: User, user_id: UUID) -> None:
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Access forbidden", "details": {}},
        )


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------

_PROFILE_JSON_KEYS = {
    "strengths", "weaknesses", "study_hours_per_day",
    "study_consistency", "interests",
}


@app.get(f"{settings.api_prefix}/users/{{user_id}}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _require_self(current_user, user_id)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise not_found("User", str(user_id))
    return user


@app.put(f"{settings.api_prefix}/users/{{user_id}}/profile")
async def update_user_profile(
    user_id: UUID,
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Merge whitelisted fields into preparation_profile + top-level User columns."""
    _require_self(current_user, user_id)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise not_found("User", str(user_id))

    incoming = profile_update.model_dump(exclude_unset=True)

    # 1) JSON fields → merge into preparation_profile (preserve existing keys).
    profile_patch = {k: v for k, v in incoming.items() if k in _PROFILE_JSON_KEYS}
    if profile_patch:
        current_profile: Dict[str, Any] = dict(user.preparation_profile or {})
        current_profile.update(profile_patch)
        user.preparation_profile = current_profile

    # 2) Top-level columns
    if "career_paths" in incoming:
        user.career_paths = incoming["career_paths"]
    if "active_exams" in incoming:
        user.active_exams = incoming["active_exams"]

    user.updated_at = datetime.utcnow()
    db.commit()

    log_user_activity(user_id, "profile_updated", incoming)
    return {"message": "Profile updated successfully"}


# ---------------------------------------------------------------------------
# Exams
# ---------------------------------------------------------------------------

@app.get(f"{settings.api_prefix}/exams", response_model=List[ExamResponse])
async def get_exams(
    skip: int = 0,
    limit: int = 100,
    exam_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    skip = max(skip, 0)
    limit = max(min(limit, 200), 1)

    query = db.query(Exam)
    if exam_type:
        query = query.filter(Exam.exam_type == exam_type)
    return query.offset(skip).limit(limit).all()


@app.get(f"{settings.api_prefix}/exams/{{exam_id}}", response_model=ExamResponse)
async def get_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise not_found("Exam", str(exam_id))
    return exam


# ---------------------------------------------------------------------------
# AI-powered (protected)
# ---------------------------------------------------------------------------

@app.post(f"{settings.api_prefix}/users/{{user_id}}/chat")
@limiter.limit(settings.chat_rate_limit)
async def chat_with_mentor(
    request: Request,
    user_id: UUID,
    message: ChatMessage,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _require_self(current_user, user_id)

    chatbot = ExamSenseiChatbot(db)
    try:
        response = await chatbot.process_message(user_id, message.message, message.session_id)
    except Exception as exc:  # noqa: BLE001
        log_error(exc, {"user_id": str(user_id), "endpoint": "chat"})
        raise internal_error("Chat service temporarily unavailable")

    log_user_activity(user_id, "chat_interaction", {"message_length": len(message.message)})
    return response


@app.get(f"{settings.api_prefix}/users/{{user_id}}/recommendations")
async def get_user_recommendations(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _require_self(current_user, user_id)

    mentor = AdaptiveMentor(db)
    try:
        return mentor.get_personalized_recommendations(user_id)
    except Exception as exc:  # noqa: BLE001
        log_error(exc, {"user_id": str(user_id), "endpoint": "recommendations"})
        raise internal_error("Recommendation service unavailable")


@app.post(f"{settings.api_prefix}/users/{{user_id}}/study-plan")
async def generate_study_plan(
    user_id: UUID,
    plan_request: StudyPlanRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _require_self(current_user, user_id)

    prioritizer = TopicPrioritizer(db)
    try:
        plan = prioritizer.generate_study_plan(
            user_id, plan_request.exam_code, plan_request.days_available
        )
    except Exception as exc:  # noqa: BLE001
        log_error(exc, {"user_id": str(user_id), "endpoint": "study-plan"})
        raise internal_error("Study plan generation failed")

    # Persist the plan when the exam exists. Deactivate any prior active plan
    # for the same (user, exam) pair so "is_active" is a real invariant.
    exam = db.query(Exam).filter(Exam.code == plan_request.exam_code).first()
    if exam:
        try:
            db.query(StudyPlan).filter(
                StudyPlan.user_id == user_id,
                StudyPlan.exam_id == exam.id,
                StudyPlan.is_active.is_(True),
            ).update({"is_active": False})

            db.add(StudyPlan(
                user_id=user_id,
                exam_id=exam.id,
                plan_data=plan,
                is_active=True,
            ))
            db.commit()
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            log_error(exc, {"user_id": str(user_id), "endpoint": "study-plan", "stage": "persist"})

    log_user_activity(user_id, "study_plan_generated", {"exam": plan_request.exam_code})
    return plan


# ---------------------------------------------------------------------------
# Gamification
# ---------------------------------------------------------------------------

def _get_or_create_gamification(db: Session, user_id: UUID) -> Gamification:
    """Get the user's Gamification row, creating it atomically on first access."""
    row = db.query(Gamification).filter(Gamification.user_id == user_id).first()
    if row is not None:
        return row

    row = Gamification(user_id=user_id)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        # Concurrent request beat us to the insert. Re-fetch.
        db.rollback()
        row = db.query(Gamification).filter(Gamification.user_id == user_id).first()
        if row is None:
            raise
        return row
    db.refresh(row)
    return row


@app.get(f"{settings.api_prefix}/users/{{user_id}}/gamification")
async def get_gamification_status(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _require_self(current_user, user_id)

    gamification = _get_or_create_gamification(db, user_id)
    return {
        "level": gamification.level,
        "xp_points": gamification.xp_points,
        "streak_days": gamification.streak_days,
        "achievements": gamification.achievements or [],
    }


# ---------------------------------------------------------------------------
# Health / root
# ---------------------------------------------------------------------------

@app.get(f"{settings.api_prefix}/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/")
async def root():
    return {
        "message": "Welcome to ExamSensei API",
        "version": "1.0.0",
        "docs": f"{settings.api_prefix}/docs",
        "health": f"{settings.api_prefix}/health",
    }


if __name__ == "__main__":
    import os
    import uvicorn

    uvicorn.run(
        "app_v2:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )
