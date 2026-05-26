"""
Security tests for the Supabase Auth integration + ownership guarantees.

We don't run a real Supabase instance in tests. Instead we mint JWTs with
the same secret + algorithm + audience that the production verifier expects
(matching exactly what Supabase Auth would emit), and assert that the
verifier accepts/rejects them correctly.
"""
import time
from uuid import uuid4

import pytest
from fastapi import status
from jose import jwt

from config import settings
from tests.conftest import make_supabase_jwt


# ---- JWT verifier semantics ----------------------------------------------

def test_missing_authorization_header_rejected(client):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_malformed_authorization_header_rejected(client, test_user):
    # No "Bearer " prefix
    token = make_supabase_jwt(test_user.id)
    r = client.get("/api/v1/auth/me", headers={"Authorization": token})
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_valid_supabase_jwt_accepted(client, test_user, auth_headers):
    r = client.get("/api/v1/auth/me", headers=auth_headers)
    assert r.status_code == status.HTTP_200_OK
    body = r.json()
    assert body["email"] == test_user.email
    assert body["id"] == str(test_user.id)


def test_expired_jwt_rejected(client, test_user):
    token = make_supabase_jwt(test_user.id, expires_in_seconds=-10)
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_wrong_audience_rejected(client, test_user):
    """Anonymous Supabase tokens (aud="anon") must NOT authenticate."""
    token = make_supabase_jwt(test_user.id, audience="anon")
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_wrong_secret_rejected(client, test_user):
    """A JWT signed with a different secret must NOT verify."""
    token = make_supabase_jwt(test_user.id, secret="some-other-secret")
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_missing_sub_rejected(client):
    """A JWT without a sub claim must NOT authenticate."""
    now = int(time.time())
    payload = {
        "aud": "authenticated",
        "iat": now,
        "exp": now + 3600,
    }
    token = jwt.encode(payload, settings.supabase_jwt_secret, algorithm="HS256")
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_unknown_user_uuid_rejected(client):
    """A valid JWT for a UUID with no matching profile row → 401."""
    token = make_supabase_jwt(uuid4())  # random UUID, no User row
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_inactive_user_rejected(client, db_session, test_user):
    test_user.is_active = False
    db_session.commit()
    token = make_supabase_jwt(test_user.id)
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == status.HTTP_400_BAD_REQUEST  # inactive user


# ---- IDOR ----------------------------------------------------------------

def test_user_cannot_access_other_user_data(client, db_session, test_user, auth_headers):
    """User A's token must not let them read/mutate user B's resources."""
    from models import User

    other = User(
        id=uuid4(),
        email="other@example.com",
        name="Other",
        education_level="class_12",
        state="KA",
        category="general",
        budget="medium",
        is_active=True,
        is_verified=True,
    )
    db_session.add(other)
    db_session.commit()
    db_session.refresh(other)

    assert client.get(f"/api/v1/users/{other.id}", headers=auth_headers).status_code == status.HTTP_403_FORBIDDEN
    assert client.get(f"/api/v1/users/{other.id}/gamification", headers=auth_headers).status_code == status.HTTP_403_FORBIDDEN
    assert client.get(f"/api/v1/users/{other.id}/recommendations", headers=auth_headers).status_code == status.HTTP_403_FORBIDDEN

    r = client.put(
        f"/api/v1/users/{other.id}/profile",
        headers=auth_headers,
        json={"strengths": ["physics"]},
    )
    assert r.status_code == status.HTTP_403_FORBIDDEN


# ---- ProfileUpdate extension --------------------------------------------

def test_profile_update_writes_career_paths_and_active_exams(client, auth_headers, test_user):
    """ProfileUpdate should accept top-level User fields too, not just JSON blob."""
    r = client.put(
        f"/api/v1/users/{test_user.id}/profile",
        headers=auth_headers,
        json={
            "strengths": ["mathematics"],
            "career_paths": ["engineering"],
            "active_exams": ["jee_main_2025"],
        },
    )
    assert r.status_code == status.HTTP_200_OK

    me = client.get("/api/v1/auth/me", headers=auth_headers)
    body = me.json()
    assert body["career_paths"] == ["engineering"]
    assert body["active_exams"] == ["jee_main_2025"]


# ---- Gamification: no duplicate-create on race --------------------------

def test_gamification_first_access_creates_row(client, auth_headers, test_user, db_session):
    """First GET creates exactly one row, subsequent GETs reuse it."""
    from models import Gamification

    r1 = client.get(f"/api/v1/users/{test_user.id}/gamification", headers=auth_headers)
    r2 = client.get(f"/api/v1/users/{test_user.id}/gamification", headers=auth_headers)

    assert r1.status_code == r2.status_code == status.HTTP_200_OK

    rows = db_session.query(Gamification).filter(Gamification.user_id == test_user.id).all()
    assert len(rows) == 1
