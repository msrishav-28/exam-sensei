"""
Integration tests for end-to-end flows under Supabase Auth.
"""
import pytest
from fastapi import status


def test_auth_me_returns_user(client, auth_headers, test_user):
    r = client.get("/api/v1/auth/me", headers=auth_headers)
    assert r.status_code == status.HTTP_200_OK
    body = r.json()
    assert body["id"] == str(test_user.id)
    assert body["email"] == test_user.email


def test_exam_discovery_and_study_plan_generation(client, auth_headers, test_user, test_exam):
    """Exam list → exam detail → personalized study plan."""
    exams_response = client.get("/api/v1/exams")
    assert exams_response.status_code == status.HTTP_200_OK
    assert len(exams_response.json()) > 0

    exam_response = client.get(f"/api/v1/exams/{test_exam.id}")
    assert exam_response.status_code == status.HTTP_200_OK
    assert exam_response.json()["id"] == test_exam.id

    study_plan_response = client.post(
        f"/api/v1/users/{test_user.id}/study-plan",
        headers=auth_headers,
        json={"exam_code": test_exam.code, "days_available": 90},
    )
    assert study_plan_response.status_code == status.HTTP_200_OK
    plan = study_plan_response.json()
    assert "prioritized_topics" in plan


def test_ai_chat_interaction(client, auth_headers, test_user):
    """Chat must degrade gracefully and always return 200 when no LLM key is configured."""
    chat_response = client.post(
        f"/api/v1/users/{test_user.id}/chat",
        headers=auth_headers,
        json={"message": "How should I prepare for physics?"},
    )

    assert chat_response.status_code == status.HTTP_200_OK
    payload = chat_response.json()
    assert "response" in payload and payload["response"]
    assert "intent" in payload
    assert "session_id" in payload


def test_recommendations_flow(client, auth_headers, test_user):
    rec_response = client.get(
        f"/api/v1/users/{test_user.id}/recommendations",
        headers=auth_headers,
    )
    assert rec_response.status_code == status.HTTP_200_OK
    assert "recommendations" in rec_response.json()


def test_gamification_tracking(client, auth_headers, test_user):
    gam_response = client.get(
        f"/api/v1/users/{test_user.id}/gamification",
        headers=auth_headers,
    )
    assert gam_response.status_code == status.HTTP_200_OK
    gamification = gam_response.json()
    assert "level" in gamification
    assert "xp_points" in gamification
    assert "streak_days" in gamification


def test_unauthorized_access_protection(client, test_user, auth_headers):
    """Protected endpoints require auth; another user's data is forbidden."""
    # Try to access protected endpoint without auth
    response = client.get(f"/api/v1/users/{test_user.id}/recommendations")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Authenticated but accessing a different user's data → 403
    from uuid import uuid4
    other_id = uuid4()
    response = client.get(f"/api/v1/users/{other_id}/recommendations", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_profile_update_flow(client, auth_headers, test_user):
    update_data = {
        "strengths": ["mathematics", "physics"],
        "weaknesses": ["chemistry"],
        "study_hours_per_day": 6,
    }
    response = client.put(
        f"/api/v1/users/{test_user.id}/profile",
        headers=auth_headers,
        json=update_data,
    )
    assert response.status_code == status.HTTP_200_OK
