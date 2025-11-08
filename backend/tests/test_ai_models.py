"""
Tests for AI models and algorithms
"""
import pytest
from ai_models import CareerRecommender, TopicPrioritizer, ExamClashDetector


def test_career_recommender_engineering():
    """Test career recommendation for engineering"""
    user_profile = {
        "interests": ["engineering"],
        "budget": "medium",
        "location": "Tamil Nadu"
    }
    exam_scores = {"jee_main": 180}  # Good score
    
    result = CareerRecommender.recommend_career_path(user_profile, exam_scores)
    
    assert "primary_recommendation" in result
    assert result["primary_recommendation"]["career_path"] == "engineering"
    assert result["primary_recommendation"]["jee_percentile"] == 60.0


def test_career_recommender_medical():
    """Test career recommendation for medical"""
    user_profile = {
        "interests": ["medical"],
        "budget": "high",
        "location": "Delhi"
    }
    exam_scores = {"neet": 600}  # High score
    
    result = CareerRecommender.recommend_career_path(user_profile, exam_scores)
    
    assert result["primary_recommendation"]["career_path"] == "medical"
    assert result["primary_recommendation"]["neet_percentile"] > 80


def test_topic_prioritizer_calculation(db_session, test_user, test_exam):
    """Test topic prioritization algorithm"""
    from models import Topic
    import json
    
    # Create test topics
    topic = Topic(
        exam_id=test_exam.id,
        subject="physics",
        name="mechanics",
        weightage_history=json.dumps([25, 24, 26, 23, 25]),
        avg_questions=8,
        difficulty_distribution=json.dumps({"easy": 40, "medium": 45, "hard": 15}),
        marks_per_hour=1.8
    )
    db_session.add(topic)
    db_session.commit()
    
    prioritizer = TopicPrioritizer(db_session)
    
    # Test priority score calculation
    score = prioritizer._calculate_priority_score(topic, [], ["mechanics"], 90)
    
    assert score > 0
    assert isinstance(score, float)


def test_exam_clash_detector(db_session):
    """Test exam clash detection"""
    from models import Exam
    import json
    
    # Create overlapping exams
    exam1 = Exam(
        name="Exam 1",
        code="exam1",
        body="NTA",
        exam_type="entrance",
        important_dates=json.dumps({"exam_dates": ["2025-01-15", "2025-01-16"]})
    )
    exam2 = Exam(
        name="Exam 2",
        code="exam2",
        body="UPSC",
        exam_type="entrance",
        important_dates=json.dumps({"exam_dates": ["2025-01-15", "2025-01-17"]})
    )
    
    db_session.add_all([exam1, exam2])
    db_session.commit()
    
    detector = ExamClashDetector()
    clashes = detector.detect_clashes(["exam1", "exam2"], db_session)
    
    assert clashes["has_clashes"] is True
    assert len(clashes["clashes"]) > 0
    assert "2025-01-15" in clashes["clashes"][0]["conflicting_dates"]
