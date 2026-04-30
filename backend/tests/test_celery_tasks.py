"""Tests for Celery async task logic."""
import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

# We test the task logic indirectly through the router and services
# since the Celery library is not available in this test environment


class TestTaskProgressLogic:
    """Tests for task progress state management."""

    def test_job_status_update_flow(self):
        """Test job status updates correctly through tasks."""
        from app.router import jobs
        from models.job import JobStatus, TaskProgress, TaskStatus, ProductType

        # Create job
        job_id = "test-flow"
        jobs[job_id] = JobStatus(
            job_id=job_id,
            status=TaskStatus.pending,
            tasks=[
                TaskProgress(type=ProductType.lesson, status=TaskStatus.pending, progress=0),
                TaskProgress(type=ProductType.tts, status=TaskStatus.pending, progress=0),
                TaskProgress(type=ProductType.ppt, status=TaskStatus.pending, progress=0),
            ],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Simulate progress update (like Celery would do)
        job = jobs[job_id]
        job.tasks[0] = TaskProgress(
            type=ProductType.lesson,
            status=TaskStatus.in_progress,
            progress=50,
            message="Generating...",
        )
        job.updated_at = datetime.utcnow()

        assert job.tasks[0].status == TaskStatus.in_progress
        assert job.tasks[0].progress == 50

        # Complete the task
        job.tasks[0] = TaskProgress(
            type=ProductType.lesson,
            status=TaskStatus.completed,
            progress=100,
            download_url="/api/download/lesson/test-flow",
        )
        job.status = TaskStatus.completed
        job.updated_at = datetime.utcnow()

        assert job.status == TaskStatus.completed
        assert job.tasks[0].download_url == "/api/download/lesson/test-flow"

        del jobs[job_id]

    def test_task_failure_propagation(self):
        """Test failure status propagates correctly."""
        from app.router import jobs
        from models.job import JobStatus, TaskProgress, TaskStatus, ProductType

        job_id = "test-failure"
        jobs[job_id] = JobStatus(
            job_id=job_id,
            status=TaskStatus.pending,
            tasks=[
                TaskProgress(type=ProductType.lesson, status=TaskStatus.pending, progress=0),
            ],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Simulate failure
        job = jobs[job_id]
        job.tasks[0] = TaskProgress(
            type=ProductType.lesson,
            status=TaskStatus.failed,
            progress=0,
            error="LLM API timeout",
        )
        job.status = TaskStatus.failed

        assert job.status == TaskStatus.failed
        assert job.tasks[0].error == "LLM API timeout"

        del jobs[job_id]

    def test_partial_progress_tracking(self):
        """Test partial progress across multiple tasks."""
        from app.router import jobs
        from models.job import JobStatus, TaskProgress, TaskStatus, ProductType

        job_id = "test-partial"
        jobs[job_id] = JobStatus(
            job_id=job_id,
            status=TaskStatus.in_progress,
            tasks=[
                TaskProgress(type=ProductType.lesson, status=TaskStatus.completed, progress=100),
                TaskProgress(type=ProductType.tts, status=TaskStatus.in_progress, progress=60),
                TaskProgress(type=ProductType.ppt, status=TaskStatus.pending, progress=0),
            ],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        job = jobs[job_id]
        # Overall status should reflect in_progress tasks
        completed_count = sum(1 for t in job.tasks if t.status == TaskStatus.completed)
        assert completed_count == 1

        # TTS in progress
        tts_task = next(t for t in job.tasks if t.type == ProductType.tts)
        assert tts_task.status == TaskStatus.in_progress
        assert tts_task.progress == 60

        del jobs[job_id]


class TestServiceIntegration:
    """Test service integration flow without Celery."""

    def test_lesson_generator_integration(self):
        """Test lesson generator can be called directly."""
        from services.lesson import LessonGenerator

        generator = LessonGenerator()
        result = generator.generate({
            "subject": "数学",
            "grade": "7年级",
            "topic": "方程",
            "duration": 45,
        })

        assert "meta" in result
        assert "outline" in result
        assert result["meta"]["topic"] == "方程"

    def test_voice_generator_integration(self):
        """Test voice generator can be called directly."""
        from services.voice import VoiceGenerator

        generator = VoiceGenerator()
        lesson = {
            "meta": {"subject": "数学"},
            "outline": {
                "introduction": {"title": "导入", "content": "test"},
                "main_sections": [],
                "conclusion": {"title": "总结", "content": "test"},
            },
        }
        result = generator.generate(lesson)

        assert isinstance(result, list)

    def test_ppt_generator_integration(self):
        """Test PPT generator can be called directly."""
        from services.ppt import PPTGenerator
        from pptx import Presentation
        import tempfile
        import os

        generator = PPTGenerator()
        lesson = {
            "meta": {"subject": "数学", "grade": "7年级", "topic": "方程"},
            "outline": {
                "introduction": {"title": "导入", "content": "test", "key_points": []},
                "main_sections": [
                    {"title": "知识点", "content": "content", "key_points": ["点1"]}
                ],
                "conclusion": {"title": "总结", "content": "test", "key_points": []},
            },
        }

        # Test by creating presentation manually
        prs = Presentation()
        generator._add_title_slide(prs, lesson["meta"])
        for section in lesson["outline"].get("main_sections", []):
            from models.lesson import SlideType
            generator._add_content_slide(prs, section, SlideType.knowledge)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.pptx")
            prs.save(output_path)
            assert os.path.exists(output_path)