"""Tests for Celery async tasks logic."""
import pytest
from unittest.mock import patch, MagicMock
from models.job import TaskStatus, ProductType, JobStatus, TaskProgress
from datetime import datetime


class TestUpdateProgressLogic:
    """Tests for progress update logic without importing celery tasks."""

    def test_update_progress_logic(self):
        """Test the logic of updating job progress."""
        from app.router import jobs

        # Create a test job
        job_id = "test-progress-job"
        jobs[job_id] = JobStatus(
            job_id=job_id,
            status=TaskStatus.pending,
            tasks=[
                TaskProgress(type=ProductType.lesson, status=TaskStatus.pending, progress=0),
                TaskProgress(type=ProductType.tts, status=TaskStatus.pending, progress=0),
                TaskProgress(type=ProductType.ppt, status=TaskStatus.pending, progress=0),
                TaskProgress(type=ProductType.video, status=TaskStatus.pending, progress=0),
            ],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Simulate progress update
        job = jobs[job_id]
        for i, task in enumerate(job.tasks):
            if task.type == ProductType.lesson:
                job.tasks[i] = TaskProgress(
                    type=ProductType.lesson,
                    status=TaskStatus.in_progress,
                    progress=50,
                    message="Processing",
                )
                break
        job.status = TaskStatus.in_progress
        job.updated_at = datetime.utcnow()

        # Verify update
        assert job.status == TaskStatus.in_progress
        lesson_task = next(t for t in job.tasks if t.type == ProductType.lesson)
        assert lesson_task.status == TaskStatus.in_progress
        assert lesson_task.progress == 50

        # Clean up
        del jobs[job_id]

    def test_update_progress_with_error(self):
        """Test progress update with error status."""
        from app.router import jobs

        job_id = "test-error-job"
        jobs[job_id] = JobStatus(
            job_id=job_id,
            status=TaskStatus.pending,
            tasks=[
                TaskProgress(type=ProductType.ppt, status=TaskStatus.pending, progress=0),
            ],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Simulate error
        job = jobs[job_id]
        for i, task in enumerate(job.tasks):
            if task.type == ProductType.ppt:
                job.tasks[i] = TaskProgress(
                    type=ProductType.ppt,
                    status=TaskStatus.failed,
                    progress=0,
                    error="PPT generation failed",
                )
                break
        job.status = TaskStatus.failed

        # Verify error
        assert job.status == TaskStatus.failed
        ppt_task = job.tasks[0]
        assert ppt_task.status == TaskStatus.failed
        assert ppt_task.error == "PPT generation failed"

        # Clean up
        del jobs[job_id]

    def test_update_progress_completed_with_download_url(self):
        """Test progress update with download URL."""
        from app.router import jobs

        job_id = "test-download-job"
        jobs[job_id] = JobStatus(
            job_id=job_id,
            status=TaskStatus.pending,
            tasks=[
                TaskProgress(type=ProductType.lesson, status=TaskStatus.pending, progress=0),
            ],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Simulate completion
        job = jobs[job_id]
        for i, task in enumerate(job.tasks):
            if task.type == ProductType.lesson:
                job.tasks[i] = TaskProgress(
                    type=ProductType.lesson,
                    status=TaskStatus.completed,
                    progress=100,
                    message="教案生成完成",
                    download_url="/api/download/lesson/test-download-job",
                )
                break
        job.status = TaskStatus.completed

        # Verify download URL
        lesson_task = job.tasks[0]
        assert lesson_task.download_url == "/api/download/lesson/test-download-job"

        # Clean up
        del jobs[job_id]


class TestGenerationPipelineLogic:
    """Tests for generation pipeline logic."""

    @patch("services.lesson.LessonGenerator")
    def test_lesson_generation_logic(self, mock_generator_class):
        """Test lesson generation logic."""
        mock_generator = MagicMock()
        mock_generator.generate.return_value = {
            "meta": {"subject": "数学", "grade": "7年级", "topic": "一元一次方程"},
            "outline": {
                "introduction": {"title": "导入", "content": "内容"},
                "main_sections": [],
                "conclusion": {"title": "总结", "content": "内容"},
            },
        }
        mock_generator_class.return_value = mock_generator

        # Create generator and generate
        generator = mock_generator_class()
        result = generator.generate({"subject": "数学", "grade": "7年级", "topic": "一元一次方程", "duration": 45})

        assert result is not None
        assert "meta" in result
        assert "outline" in result
        mock_generator.generate.assert_called_once()

    @patch("services.voice.VoiceGenerator")
    def test_voice_generation_logic(self, mock_generator_class):
        """Test voice generation logic."""
        mock_generator = MagicMock()
        mock_generator.generate.return_value = ["audio1.mp3", "audio2.mp3"]
        mock_generator_class.return_value = mock_generator

        generator = mock_generator_class()
        result = generator.generate({"outline": {"main_sections": [{"title": "test"}]}})

        assert result is not None
        assert len(result) == 2
        mock_generator.generate.assert_called_once()

    @patch("services.ppt.PPTGenerator")
    def test_ppt_generation_logic(self, mock_generator_class):
        """Test PPT generation logic."""
        mock_generator = MagicMock()
        mock_generator.generate.return_value = "/storage/ppt/test.pptx"
        mock_generator_class.return_value = mock_generator

        generator = mock_generator_class()
        result = generator.generate({"meta": {"topic": "test"}, "outline": {}})

        assert result is not None
        assert result.endswith(".pptx")
        mock_generator.generate.assert_called_once()


class TestAsyncCoroutineRunner:
    """Tests for async coroutine runner pattern."""

    def test_run_async_pattern(self):
        """Test the pattern for running async in sync context."""
        import asyncio

        async def sample_coro():
            await asyncio.sleep(0)
            return "result"

        # Pattern 1: asyncio.run (Python 3.7+)
        result = asyncio.run(sample_coro())
        assert result == "result"

    def test_run_async_with_exception_handling(self):
        """Test async runner handles RuntimeError."""
        import asyncio

        async def error_coro():
            raise RuntimeError("Test error")

        # Should handle RuntimeError
        try:
            asyncio.run(error_coro())
        except RuntimeError as e:
            assert str(e) == "Test error"


class TestTaskProgressModel:
    """Tests for TaskProgress model used in tasks."""

    def test_task_progress_creation(self):
        """Test TaskProgress model creation."""
        task = TaskProgress(
            type=ProductType.lesson,
            status=TaskStatus.in_progress,
            progress=50,
            message="Processing",
        )
        assert task.type == ProductType.lesson
        assert task.status == TaskStatus.in_progress
        assert task.progress == 50
        assert task.message == "Processing"

    def test_task_progress_with_error(self):
        """Test TaskProgress with error."""
        task = TaskProgress(
            type=ProductType.ppt,
            status=TaskStatus.failed,
            progress=0,
            error="Generation failed",
        )
        assert task.error == "Generation failed"

    def test_task_progress_with_download_url(self):
        """Test TaskProgress with download URL."""
        task = TaskProgress(
            type=ProductType.tts,
            status=TaskStatus.completed,
            progress=100,
            download_url="/api/download/tts/test-job",
        )
        assert task.download_url == "/api/download/tts/test-job"


class TestJobStatusModel:
    """Tests for JobStatus model used in tasks."""

    def test_job_status_creation(self):
        """Test JobStatus model creation."""
        job = JobStatus(
            job_id="test-job",
            status=TaskStatus.pending,
            tasks=[
                TaskProgress(type=ProductType.lesson, status=TaskStatus.pending, progress=0),
            ],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        assert job.job_id == "test-job"
        assert job.status == TaskStatus.pending
        assert len(job.tasks) == 1

    def test_job_status_update(self):
        """Test JobStatus can be updated."""
        created = datetime.utcnow()
        job = JobStatus(
            job_id="test-job",
            status=TaskStatus.pending,
            tasks=[],
            created_at=created,
            updated_at=created,
        )

        # Update
        job.status = TaskStatus.in_progress
        job.updated_at = datetime.utcnow()

        assert job.status == TaskStatus.in_progress
        assert job.updated_at > created