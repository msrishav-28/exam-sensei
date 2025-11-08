"""
Tests for exam endpoints
"""
import pytest
from fastapi import status


def test_get_exams(client, test_exam):
    """Test getting list of exams"""
    response = client.get("/api/v1/exams")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["code"] == "jee_main_2025"


def test_get_exam_by_id(client, test_exam):
    """Test getting specific exam"""
    response = client.get(f"/api/v1/exams/{test_exam.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_exam.id
    assert data["name"] == "JEE Main 2025"


def test_get_nonexistent_exam(client):
    """Test getting non-existent exam"""
    response = client.get("/api/v1/exams/99999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_filter_exams_by_type(client, test_exam):
    """Test filtering exams by type"""
    response = client.get("/api/v1/exams?exam_type=engineering_entrance")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(exam["exam_type"] == "engineering_entrance" for exam in data)
