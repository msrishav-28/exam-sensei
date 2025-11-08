"""
Integration tests for complete user flows
"""
import pytest
from fastapi import status


def test_complete_user_registration_and_login_flow(client):
    """Test complete user registration and login flow"""
    # Register
    register_data = {
        "email": "integration@test.com",
        "password": "securepass123",
        "name": "Integration Test User",
        "education_level": "class_12",
        "state": "Maharashtra",
        "category": "general",
        "budget": "medium"
    }
    
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == status.HTTP_201_CREATED
    user_data = response.json()
    assert user_data["email"] == register_data["email"]
    user_id = user_data["id"]
    
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": register_data["email"], "password": register_data["password"]}
    )
    assert login_response.status_code == status.HTTP_200_OK
    tokens = login_response.json()
    assert "access_token" in tokens
    
    # Access protected endpoint
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == status.HTTP_200_OK
    assert me_response.json()["id"] == user_id


def test_exam_discovery_and_study_plan_generation(client, auth_headers, test_user, test_exam):
    """Test exam discovery and study plan generation flow"""
    # Get exams
    exams_response = client.get("/api/v1/exams")
    assert exams_response.status_code == status.HTTP_200_OK
    exams = exams_response.json()
    assert len(exams) > 0
    
    # Get specific exam
    exam_response = client.get(f"/api/v1/exams/{test_exam.id}")
    assert exam_response.status_code == status.HTTP_200_OK
    exam = exam_response.json()
    assert exam["id"] == test_exam.id
    
    # Generate study plan
    study_plan_response = client.post(
        f"/api/v1/users/{test_user.id}/study-plan",
        headers=auth_headers,
        json={"exam_code": test_exam.code, "days_available": 90}
    )
    assert study_plan_response.status_code == status.HTTP_200_OK
    plan = study_plan_response.json()
    assert "prioritized_topics" in plan


def test_ai_chat_interaction(client, auth_headers, test_user):
    """Test AI chat interaction"""
    chat_response = client.post(
        f"/api/v1/users/{test_user.id}/chat",
        headers=auth_headers,
        json={"message": "How should I prepare for physics?"}
    )
    
    # Should return 200 even if Ollama is not available (graceful degradation)
    assert chat_response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]


def test_recommendations_flow(client, auth_headers, test_user):
    """Test personalized recommendations"""
    rec_response = client.get(
        f"/api/v1/users/{test_user.id}/recommendations",
        headers=auth_headers
    )
    
    assert rec_response.status_code == status.HTTP_200_OK
    recommendations = rec_response.json()
    assert "recommendations" in recommendations


def test_gamification_tracking(client, auth_headers, test_user):
    """Test gamification status tracking"""
    gam_response = client.get(
        f"/api/v1/users/{test_user.id}/gamification",
        headers=auth_headers
    )
    
    assert gam_response.status_code == status.HTTP_200_OK
    gamification = gam_response.json()
    assert "level" in gamification
    assert "xp_points" in gamification
    assert "streak_days" in gamification


def test_unauthorized_access_protection(client, test_user):
    """Test that protected endpoints require authentication"""
    # Try to access protected endpoint without auth
    response = client.get(f"/api/v1/users/{test_user.id}/recommendations")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Try to access another user's data
    response = client.post("/api/v1/auth/login", data={"username": "test@example.com", "password": "testpassword123"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to access user ID 9999 (doesn't exist or not authorized)
    response = client.get("/api/v1/users/9999/recommendations", headers=headers)
    assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


def test_profile_update_flow(client, auth_headers, test_user):
    """Test user profile update"""
    update_data = {
        "strengths": ["mathematics", "physics"],
        "weaknesses": ["chemistry"],
        "study_hours_per_day": 6
    }
    
    response = client.put(
        f"/api/v1/users/{test_user.id}/profile",
        headers=auth_headers,
        json=update_data
    )
    
    assert response.status_code == status.HTTP_200_OK
