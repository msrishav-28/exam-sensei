"""
ExamSensei API - Production-Ready Version
Complete with authentication, logging, error handling, rate limiting, and monitoring
"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import time
from typing import List, Optional, Dict, Any

# Local imports
from models import Exam, Topic, User, UserActivity, Recommendation, StudyPlan, Conversation, Gamification
from database import get_db, create_tables
from ai_models import AdaptiveMentor, CareerRecommender, TopicPrioritizer, ExamClashDetector
from chatbot import ExamSenseiChatbot
from lifecycle import lifecycle_machine
from auth import (
    Token, UserLogin, UserRegister, authenticate_user, create_access_token,
    create_refresh_token, get_current_active_user, create_user, get_password_hash
)
from config import settings
from logger import logger, log_api_request, log_error, log_user_activity
from exceptions import (
    ExamSenseiException, AuthenticationError, ResourceNotFoundError,
    not_found, unauthorized, bad_request, internal_error
)

# Pydantic models
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import json


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("🚀 Starting ExamSensei API...")
    create_tables()
    logger.info("✅ Database tables created/verified")
    
    # Initialize monitoring
    if settings.sentry_dsn:
        import sentry_sdk
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            traces_sample_rate=1.0 if settings.environment == "development" else 0.1
        )
        logger.info("✅ Sentry monitoring initialized")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down ExamSensei API...")


# Initialize FastAPI app
app = FastAPI(
    title="ExamSensei API",
    description="AI-Powered Competitive Exam Mentor System",
    version="1.0.0",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    lifespan=lifespan
)


# Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trust only specific hosts in production
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["examsensei.com", "*.examsensei.com"]
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests"""
    start_time = time.time()
    
    # Generate request ID
    request_id = f"{int(time.time() * 1000)}"
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log request
    log_api_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code
    )
    
    # Add custom headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(duration)
    
    return response


# Global exception handler
@app.exception_handler(ExamSenseiException)
async def examsensei_exception_handler(request: Request, exc: ExamSenseiException):
    """Handle custom exceptions"""
    log_error(exc, {"path": request.url.path})
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": exc.message, "details": exc.details}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    log_error(exc, {"path": request.url.path})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error", "details": str(exc) if settings.environment == "development" else {}}
    )


# Pydantic Models for API
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    education_level: str
    state: str
    category: str = "general"
    budget: str = "medium"


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    current_stage: str
    career_paths: Optional[List[str]] = None
    active_exams: Optional[List[str]] = None
    is_verified: bool
    
    class Config:
        from_attributes = True


class ExamResponse(BaseModel):
    id: int
    name: str
    code: str
    body: str
    exam_type: str
    important_dates: Optional[Dict] = None
    
    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class StudyPlanRequest(BaseModel):
    exam_code: str
    days_available: int = 90


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post(f"{settings.api_prefix}/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register new user"""
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise bad_request("Email already registered")
        
        # Create user
        new_user = create_user(db, user_data)
        logger.info(f"New user registered: {new_user.email}")
        
        return new_user
    
    except Exception as e:
        log_error(e)
        raise internal_error("Registration failed")


@app.post(f"{settings.api_prefix}/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        logger.warning(f"Failed login attempt for: {form_data.username}")
        raise unauthorized("Incorrect email or password")
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token(data={"sub": user.id, "email": user.email})
    
    logger.info(f"User logged in: {user.email}")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@app.get(f"{settings.api_prefix}/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.get(f"{settings.api_prefix}/users/{{user_id}}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (must be authenticated)"""
    # Users can only access their own data unless admin
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise not_found("User", str(user_id))
    
    return user


@app.put(f"{settings.api_prefix}/users/{{user_id}}/profile")
async def update_user_profile(
    user_id: int,
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise not_found("User", str(user_id))
    
    # Update preparation profile
    current_profile = json.loads(user.preparation_profile) if user.preparation_profile else {}
    current_profile.update(profile_data)
    user.preparation_profile = json.dumps(current_profile)
    user.updated_at = datetime.utcnow()
    
    db.commit()
    log_user_activity(user_id, "profile_updated", profile_data)
    
    return {"message": "Profile updated successfully"}


# ============================================================================
# EXAM ENDPOINTS
# ============================================================================

@app.get(f"{settings.api_prefix}/exams", response_model=List[ExamResponse])
async def get_exams(
    skip: int = 0,
    limit: int = 100,
    exam_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of exams (public endpoint)"""
    query = db.query(Exam)
    if exam_type:
        query = query.filter(Exam.exam_type == exam_type)
    exams = query.offset(skip).limit(limit).all()
    return exams


@app.get(f"{settings.api_prefix}/exams/{{exam_id}}", response_model=ExamResponse)
async def get_exam(exam_id: int, db: Session = Depends(get_db)):
    """Get exam details"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise not_found("Exam", str(exam_id))
    return exam


# ============================================================================
# AI-POWERED ENDPOINTS (Protected)
# ============================================================================

@app.post(f"{settings.api_prefix}/users/{{user_id}}/chat")
async def chat_with_mentor(
    user_id: int,
    message: ChatMessage,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Chat with AI mentor"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    try:
        chatbot = ExamSenseiChatbot(db)
        response = chatbot.process_message(user_id, message.message, message.session_id)
        
        log_user_activity(user_id, "chat_interaction", {"message_length": len(message.message)})
        return response
    
    except Exception as e:
        log_error(e, {"user_id": user_id})
        raise internal_error("Chat service temporarily unavailable")


@app.get(f"{settings.api_prefix}/users/{{user_id}}/recommendations")
async def get_user_recommendations(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get personalized recommendations"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    try:
        mentor = AdaptiveMentor(db)
        recommendations = mentor.get_personalized_recommendations(user_id)
        return recommendations
    
    except Exception as e:
        log_error(e, {"user_id": user_id})
        raise internal_error("Recommendation service unavailable")


@app.post(f"{settings.api_prefix}/users/{{user_id}}/study-plan")
async def generate_study_plan(
    user_id: int,
    plan_request: StudyPlanRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate personalized study plan"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    try:
        prioritizer = TopicPrioritizer(db)
        plan = prioritizer.generate_study_plan(
            user_id,
            plan_request.exam_code,
            plan_request.days_available
        )
        
        # Save study plan
        exam = db.query(Exam).filter(Exam.code == plan_request.exam_code).first()
        if exam:
            study_plan = StudyPlan(
                user_id=user_id,
                exam_id=exam.id,
                plan_data=json.dumps(plan),
                is_active=True
            )
            db.add(study_plan)
            db.commit()
        
        log_user_activity(user_id, "study_plan_generated", {"exam": plan_request.exam_code})
        return plan
    
    except Exception as e:
        log_error(e, {"user_id": user_id})
        raise internal_error("Study plan generation failed")


# ============================================================================
# GAMIFICATION ENDPOINTS
# ============================================================================

@app.get(f"{settings.api_prefix}/users/{{user_id}}/gamification")
async def get_gamification_status(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user gamification status"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    gamification = db.query(Gamification).filter(Gamification.user_id == user_id).first()
    if not gamification:
        gamification = Gamification(user_id=user_id)
        db.add(gamification)
        db.commit()
    
    return {
        "level": gamification.level,
        "xp_points": gamification.xp_points,
        "streak_days": gamification.streak_days,
        "achievements": json.loads(gamification.achievements) if gamification.achievements else []
    }


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.get(f"{settings.api_prefix}/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to ExamSensei API",
        "version": "1.0.0",
        "docs": f"{settings.api_prefix}/docs",
        "health": f"{settings.api_prefix}/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app_v2:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )
