"""Unit tests for API endpoints."""
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health_check():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_endpoint():
    """Test lesson generation endpoint."""
    response = client.post(
        "/api/generate",
        json={
            "subject": "数学",
            "grade": "7年级",
            "duration": 45,
            "topic": "一元一次方程",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["message"] == "任务已创建，正在处理"


def test_job_status_not_found():
    """Test job status for non-existent job."""
    response = client.get("/api/job/nonexistent/status")
    assert response.status_code == 404


def test_job_status_exists():
    """Test job status after creation."""
    # First create a job
    create_response = client.post(
        "/api/generate",
        json={
            "subject": "物理",
            "grade": "高一",
            "duration": 30,
            "topic": "牛顿第一定律",
        },
    )
    job_id = create_response.json()["job_id"]

    # Then check status
    status_response = client.get(f"/api/job/{job_id}/status")
    assert status_response.status_code == 200
    data = status_response.json()
    assert data["job_id"] == job_id
    assert data["status"] == "pending"
    assert len(data["tasks"]) == 4  # lesson, tts, ppt, video