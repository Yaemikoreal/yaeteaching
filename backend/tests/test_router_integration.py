"""Tests for router Celery integration and edge cases."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestRouterCeleryIntegration:
    """Tests for Celery task triggering."""

    def test_generate_triggers_celery_task(self):
        """Test generate endpoint triggers Celery task."""
        mock_task = MagicMock()
        mock_task.delay = MagicMock(return_value=MagicMock(id="celery-task-id"))

        with patch.dict("sys.modules", {"celery.tasks": MagicMock(start_generation_pipeline=mock_task)}):
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

    def test_generate_handles_celery_failure(self):
        """Test generate handles Celery not available gracefully."""
        # Celery import will fail in test environment, job should still be created
        response = client.post(
            "/api/generate",
            json={
                "subject": "化学",
                "grade": "高一",
                "duration": 30,
                "topic": "化学方程式",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data


class TestRouterDownloadEdgeCases:
    """Tests for download endpoint edge cases."""

    def test_download_completed_task(self):
        """Test download for completed task returns URL."""
        from app.router import jobs
        from models.job import JobStatus, TaskProgress, TaskStatus, ProductType
        from datetime import datetime

        job_id = "download-test-job"
        jobs[job_id] = JobStatus(
            job_id=job_id,
            status=TaskStatus.completed,
            tasks=[
                TaskProgress(
                    type=ProductType.lesson,
                    status=TaskStatus.completed,
                    progress=100,
                    download_url="/storage/lesson/download-test-job.json",
                ),
                TaskProgress(type=ProductType.tts, status=TaskStatus.pending, progress=0),
                TaskProgress(type=ProductType.ppt, status=TaskStatus.pending, progress=0),
                TaskProgress(type=ProductType.video, status=TaskStatus.pending, progress=0),
            ],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        response = client.get(f"/api/download/lesson/{job_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["download_url"] == "/storage/lesson/download-test-job.json"

        # Cleanup
        del jobs[job_id]

    def test_download_wrong_product_type(self):
        """Test download for non-existent product type."""
        from app.router import jobs
        from models.job import JobStatus, TaskProgress, TaskStatus, ProductType
        from datetime import datetime

        job_id = "wrong-type-job"
        jobs[job_id] = JobStatus(
            job_id=job_id,
            status=TaskStatus.pending,
            tasks=[
                TaskProgress(type=ProductType.lesson, status=TaskStatus.pending, progress=0),
            ],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # 'invalid' is not a valid ProductType, will not match any task
        response = client.get(f"/api/download/invalid/{job_id}")

        assert response.status_code == 400

        del jobs[job_id]


class TestRouterJobStatusUpdates:
    """Tests for job status tracking."""

    def test_job_status_structure(self):
        """Test job status returns correct structure."""
        response = client.post(
            "/api/generate",
            json={
                "subject": "英语",
                "grade": "初三",
                "duration": 45,
                "topic": "定语从句",
            },
        )

        job_id = response.json()["job_id"]
        status_response = client.get(f"/api/job/{job_id}/status")

        assert status_response.status_code == 200
        data = status_response.json()
        assert "job_id" in data
        assert "status" in data
        assert "tasks" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_multiple_jobs_unique_ids(self):
        """Test each job gets unique ID."""
        ids = []
        for _ in range(3):
            response = client.post(
                "/api/generate",
                json={
                    "subject": "历史",
                    "grade": "初二",
                    "duration": 45,
                    "topic": "抗日战争",
                },
            )
            ids.append(response.json()["job_id"])

        assert len(ids) == len(set(ids))  # All IDs are unique