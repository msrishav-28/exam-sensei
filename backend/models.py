"""
SQLAlchemy models for ExamSensei.

User identity is owned by Supabase Auth — `User.id` is a UUID that matches
`auth.users.id` exactly. The `users` row is populated by the trigger in
`backend/migrations/001_supabase_profile_trigger.sql` whenever a new auth.user
is created via the Supabase Auth SDK. No password / reset-token columns here:
Supabase manages those.

JSON columns: assign native Python (dict/list) directly; SQLAlchemy serializes
for you. Do not call json.dumps/json.loads on these fields.
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.types import CHAR, TypeDecorator


Base = declarative_base()


class UUIDType(TypeDecorator):
    """
    Cross-dialect UUID column.

    - On Postgres: uses the native uuid type via psycopg2 (PG_UUID(as_uuid=True)).
    - On SQLite (tests): stores as 32-char string, converts to/from uuid.UUID
      transparently.

    This lets the same model code run under Supabase Postgres in prod and
    SQLite in-memory in tests without two model definitions.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
        # SQLite (and other dialects): store as canonical string
        return str(value) if isinstance(value, uuid.UUID) else str(uuid.UUID(str(value)))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


class User(Base):
    __tablename__ = "users"

    # UUID PK = auth.users.id. The trigger inserts this row on signup.
    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    email = Column(String(254), unique=True, index=True, nullable=False)
    name = Column(String(120))
    education_level = Column(String(60))
    state = Column(String(60))
    category = Column(String(20))          # SC/ST/OBC/General
    budget = Column(String(20))            # low/medium/high
    current_stage = Column(String(40), default="class_12")
    career_paths = Column(JSON)            # ["engineering", "medical"]
    active_exams = Column(JSON)            # ["jee_main", "neet"]
    preparation_profile = Column(JSON)
    milestone_triggers = Column(JSON)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    study_plans = relationship("StudyPlan", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    gamification = relationship("Gamification", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), index=True, nullable=False)
    code = Column(String(60), unique=True, nullable=False)
    body = Column(String(40))
    exam_type = Column(String(40), index=True)
    eligibility = Column(JSON)
    fees = Column(JSON)
    important_dates = Column(JSON)
    syllabus = Column(Text)
    pattern = Column(JSON)
    centers = Column(JSON)
    notification_url = Column(String(500))
    application_url = Column(String(500))
    result_url = Column(String(500))
    subjects = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    bookmarks = relationship("Bookmark", back_populates="exam")
    notifications = relationship("Notification", back_populates="exam")
    topics = relationship("Topic", back_populates="exam", cascade="all, delete-orphan")
    activities = relationship("UserActivity", back_populates="exam")
    study_plans = relationship("StudyPlan", back_populates="exam")
    recommendations = relationship("Recommendation", back_populates="exam")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), index=True, nullable=False)
    subject = Column(String(40))
    name = Column(String(80))
    weightage_history = Column(JSON)
    avg_questions = Column(Float)
    difficulty_distribution = Column(JSON)
    marks_per_hour = Column(Float)
    correlation_topics = Column(JSON)
    previous_patterns = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    exam = relationship("Exam", back_populates="topics")


class Bookmark(Base):
    __tablename__ = "bookmarks"
    __table_args__ = (
        UniqueConstraint("user_id", "exam_id", name="uq_bookmark_user_exam"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUIDType(), ForeignKey("users.id"), index=True, nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), index=True, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="bookmarks")
    exam = relationship("Exam", back_populates="bookmarks")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUIDType(), ForeignKey("users.id"), index=True, nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=True)
    # notification_type encodes both the category and the specific trigger
    # (e.g. "milestone_reminder:jee_exam_date") — see lifecycle.py.
    notification_type = Column(String(80), index=True)
    message = Column(Text)
    scheduled_at = Column(DateTime)
    sent = Column(Boolean, default=False, nullable=False)
    channel = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="notifications")
    exam = relationship("Exam", back_populates="notifications")


class UserActivity(Base):
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUIDType(), ForeignKey("users.id"), index=True, nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=True)
    activity_type = Column(String(60))
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="activities")
    exam = relationship("Exam", back_populates="activities")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUIDType(), ForeignKey("users.id"), index=True, nullable=False)
    # Clash alerts span multiple exams and don't belong to a single exam row.
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=True)
    recommendation_type = Column(String(40))
    score = Column(Float)
    reasoning = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime)

    user = relationship("User", back_populates="recommendations")
    exam = relationship("Exam", back_populates="recommendations")


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUIDType(), ForeignKey("users.id"), index=True, nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), index=True, nullable=False)
    plan_data = Column(JSON)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="study_plans")
    exam = relationship("Exam", back_populates="study_plans")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUIDType(), ForeignKey("users.id"), index=True, nullable=False)
    session_id = Column(String(80), index=True)
    message = Column(Text)
    response = Column(Text)
    intent = Column(String(40))
    context = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="conversations")


class Gamification(Base):
    __tablename__ = "gamification"

    id = Column(Integer, primary_key=True, index=True)
    # One row per user — enforces the invariant at the DB level so the
    # auto-create path in /users/{id}/gamification can't race-create
    # duplicate rows.
    user_id = Column(UUIDType(), ForeignKey("users.id"), unique=True, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    xp_points = Column(Integer, default=0, nullable=False)
    streak_days = Column(Integer, default=0, nullable=False)
    achievements = Column(JSON)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="gamification")
