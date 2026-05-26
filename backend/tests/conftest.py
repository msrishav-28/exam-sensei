"""
Pytest fixtures for ExamSensei tests.

Auth is Supabase-only in production. In tests we don't have a real Supabase
instance, so we mint JWTs locally using the same secret + algorithm + audience
that the production verifier expects. This is exactly what Supabase Auth
itself produces, so the verifier code path is exercised end-to-end.
"""
import time
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app_v2 import app, limiter
from config import settings
from database import get_db
from models import Base


# Test slowapi limiter is disabled (test client reuses the same IP for every
# request — the limiter would trip after a handful of calls otherwise).
limiter.enabled = False


# Test database: in-memory SQLite, single shared connection so every fixture
# sees the same data.
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Fresh schema for every test; dropped at teardown."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient with DB dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def make_supabase_jwt(
    sub,
    *,
    audience: str = "authenticated",
    expires_in_seconds: int = 3600,
    secret: str | None = None,
    extra_claims: dict | None = None,
) -> str:
    """Mint a Supabase-shaped JWT for tests.

    Uses `time.time()` for the UTC Unix epoch directly — `datetime.utcnow()`
    on Windows is naive and `.timestamp()` reinterprets it as local time,
    silently subtracting the local UTC offset (e.g. 5.5h in IST) and making
    short-lived tokens "expired" the moment they're minted.
    """
    now = int(time.time())
    payload = {
        "sub": str(sub),
        "aud": audience,
        "iat": now,
        "exp": now + expires_in_seconds,
        "role": "authenticated",
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(
        payload,
        secret if secret is not None else settings.supabase_jwt_secret,
        algorithm="HS256",
    )


@pytest.fixture
def test_user(db_session):
    """Create a test user — UUID-keyed, no password (Supabase owns that)."""
    from models import User

    user = User(
        id=uuid4(),
        email="test@example.com",
        name="Test User",
        education_level="class_12",
        state="Tamil Nadu",
        category="general",
        budget="medium",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Authorization header carrying a Supabase-shaped JWT for `test_user`."""
    token = make_supabase_jwt(test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_exam(db_session):
    from models import Exam

    exam = Exam(
        name="JEE Main 2025",
        code="jee_main_2025",
        body="NTA",
        exam_type="engineering_entrance",
        important_dates={
            "exam_dates": ["2025-01-24", "2025-01-25"],
            "result": "2025-02-12",
        },
        subjects=["physics", "chemistry", "mathematics"],
    )
    db_session.add(exam)
    db_session.commit()
    db_session.refresh(exam)
    return exam
