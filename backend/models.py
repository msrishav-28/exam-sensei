from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON, Float, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)  # Authentication
    name = Column(String)
    education_level = Column(String)  # e.g., class_12, undergraduate
    state = Column(String)
    category = Column(String)  # SC/ST/OBC/General
    budget = Column(String)  # low/medium/high
    current_stage = Column(String, default="class_12")  # lifecycle stage
    career_paths = Column(JSON)  # ["engineering", "medical"]
    active_exams = Column(JSON)  # ["jee_main", "neet"]
    preparation_profile = Column(JSON)  # strengths, weaknesses, study_hours
    milestone_triggers = Column(JSON)  # next important dates
    is_active = Column(Boolean, default=True)  # Account status
    is_verified = Column(Boolean, default=False)  # Email verification
    reset_token = Column(String, nullable=True)  # Password reset
    reset_token_expires = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bookmarks = relationship("Bookmark", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    activities = relationship("UserActivity", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")
    study_plans = relationship("StudyPlan", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    gamification = relationship("Gamification", back_populates="user")

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    code = Column(String, unique=True)
    body = Column(String)  # NTA, UPSC, etc.
    exam_type = Column(String)  # entrance, government, etc.
    eligibility = Column(JSON)  # JSON with eligibility criteria
    fees = Column(JSON)  # JSON with fee structure
    important_dates = Column(JSON)  # JSON with dates
    syllabus = Column(Text)
    pattern = Column(JSON)  # JSON with exam pattern
    centers = Column(JSON)  # JSON with exam centers
    notification_url = Column(String)
    application_url = Column(String)
    result_url = Column(String)
    subjects = Column(JSON)  # ["physics", "chemistry", "maths"]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bookmarks = relationship("Bookmark", back_populates="exam")
    notifications = relationship("Notification", back_populates="exam")
    topics = relationship("Topic", back_populates="exam")
    activities = relationship("UserActivity", back_populates="exam")
    study_plans = relationship("StudyPlan", back_populates="exam")

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    subject = Column(String)  # physics, chemistry, maths
    name = Column(String)  # kinematics, organic_chemistry
    weightage_history = Column(JSON)  # [25, 24, 26, 23, 25] last 5 years
    avg_questions = Column(Float)
    difficulty_distribution = Column(JSON)  # {easy: 40, medium: 45, hard: 15}
    marks_per_hour = Column(Float)  # ROI metric
    correlation_topics = Column(JSON)  # ["calculus", "vectors"]
    previous_patterns = Column(JSON)  # recurring question types
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    exam = relationship("Exam", back_populates="topics")

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exam_id = Column(Integer, ForeignKey("exams.id"))
    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="bookmarks")
    exam = relationship("Exam", back_populates="bookmarks")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exam_id = Column(Integer, ForeignKey("exams.id"))
    notification_type = Column(String)  # application_deadline, admit_card, result
    message = Column(Text)
    scheduled_at = Column(DateTime)
    sent = Column(Boolean, default=False)
    channel = Column(String)  # email, push, telegram
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")
    exam = relationship("Exam", back_populates="notifications")

class UserActivity(Base):
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=True)
    activity_type = Column(String)  # viewed_exam, bookmarked, took_quiz
    details = Column(JSON)  # additional data
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="activities")
    exam = relationship("Exam", back_populates="activities")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exam_id = Column(Integer, ForeignKey("exams.id"))
    recommendation_type = Column(String)  # career_path, study_topic, clash_alert
    score = Column(Float)  # confidence score
    reasoning = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="recommendations")
    exam = relationship("Exam", back_populates="recommendations")

class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exam_id = Column(Integer, ForeignKey("exams.id"))
    plan_data = Column(JSON)  # structured plan with topics, timeline
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="study_plans")
    exam = relationship("Exam", back_populates="study_plans")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String)  # conversation session
    message = Column(Text)
    response = Column(Text)
    intent = Column(String)  # query type
    context = Column(JSON)  # user state, exam context
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="conversations")

class Gamification(Base):
    __tablename__ = "gamification"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    level = Column(Integer, default=1)
    xp_points = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    achievements = Column(JSON)  # unlocked achievements
    last_activity = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="gamification")

# Add missing relationships to Exam
Exam.recommendations = relationship("Recommendation", back_populates="exam")
