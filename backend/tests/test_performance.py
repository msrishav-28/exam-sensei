"""
Performance tests for ExamSensei
"""
import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def test_api_response_time(client):
    """Test that API responses are fast enough"""
    start = time.time()
    response = client.get("/api/v1/health")
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 0.5  # Should respond in less than 500ms


def test_exam_list_performance(client, test_exam):
    """Test exam list endpoint performance"""
    start = time.time()
    response = client.get("/api/v1/exams")
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 1.0  # Should respond in less than 1 second


def test_concurrent_requests(client, test_user, auth_headers):
    """Test handling of concurrent requests"""
    def make_request():
        return client.get("/api/v1/health")
    
    # Make 10 concurrent requests
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        results = [future.result() for future in as_completed(futures)]
    
    # All should succeed
    assert all(r.status_code == 200 for r in results)


def test_large_dataset_handling(client, db_session):
    """Test handling of large datasets"""
    from models import Exam
    import json
    
    # Create multiple exams
    exams = []
    for i in range(50):
        exam = Exam(
            name=f"Test Exam {i}",
            code=f"test_exam_{i}",
            body="Test Body",
            exam_type="test",
            important_dates=json.dumps({"exam_dates": ["2025-01-01"]})
        )
        exams.append(exam)
    
    db_session.add_all(exams)
    db_session.commit()
    
    # Query all exams
    start = time.time()
    response = client.get("/api/v1/exams?limit=100")
    duration = time.time() - start
    
    assert response.status_code == 200
    assert len(response.json()) >= 50
    assert duration < 2.0  # Should handle large datasets efficiently


@pytest.mark.skip(reason="Requires Redis")
def test_caching_performance(client, test_exam):
    """Test that caching improves performance"""
    # First request (cache miss)
    start1 = time.time()
    response1 = client.get(f"/api/v1/exams/{test_exam.id}")
    duration1 = time.time() - start1
    
    # Second request (cache hit)
    start2 = time.time()
    response2 = client.get(f"/api/v1/exams/{test_exam.id}")
    duration2 = time.time() - start2
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    # Cached request should be faster
    assert duration2 < duration1
