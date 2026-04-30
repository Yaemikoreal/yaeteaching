"""Celery async tasks for content generation."""
from celery import shared_task
from models.job import TaskStatus, ProductType
import asyncio


def _run_async(coro):
    """Run async coroutine in Celery worker context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, use nest_asyncio
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(coro)
        return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop, create new one
        return asyncio.run(coro)


def _update_progress_sync(job_id: str, task_type: ProductType, status: TaskStatus,
                          progress: int, message: str = None, error: str = None,
                          download_url: str = None):
    """Update progress synchronously by storing in job state.

    This is a sync wrapper that updates job status in memory.
    WebSocket clients will receive updates via polling or
    when they connect/reconnect.
    """
    from app.router import jobs
    if job_id in jobs:
        job = jobs[job_id]
        for i, task in enumerate(job.tasks):
            if task.type == task_type:
                job.tasks[i] = task.__class__(
                    type=task_type,
                    status=status,
                    progress=progress,
                    message=message,
                    error=error,
                    download_url=download_url,
                )
                break
        job.status = status
        from datetime import datetime
        job.updated_at = datetime.utcnow()


@shared_task(bind=True)
def start_generation_pipeline(self, job_id: str, request_data: dict):
    """Main pipeline: generate lesson -> tts -> ppt -> video."""
    # Step 1: Generate lesson plan
    lesson_json = generate_lesson_task(job_id, request_data)

    # Step 2: Generate TTS audio
    if lesson_json:
        generate_tts_task(job_id, lesson_json)

    # Step 3: Generate PPT
    if lesson_json:
        generate_ppt_task(job_id, lesson_json)

    # Step 4: Generate video (future)
    # generate_video_task(job_id, lesson_json)


@shared_task(bind=True)
def generate_lesson_task(self, job_id: str, request_data: dict) -> dict:
    """Generate lesson plan JSON via LLM."""
    _update_progress_sync(
        job_id, ProductType.lesson, TaskStatus.in_progress, 10,
        message="正在调用 LLM 生成教案..."
    )

    try:
        from services.lesson import LessonGenerator
        generator = LessonGenerator()
        lesson_json = generator.generate(request_data)

        _update_progress_sync(
            job_id, ProductType.lesson, TaskStatus.completed, 100,
            message="教案生成完成",
            download_url=f"/api/download/lesson/{job_id}"
        )

        return lesson_json

    except Exception as e:
        _update_progress_sync(
            job_id, ProductType.lesson, TaskStatus.failed, 0,
            error=str(e)
        )
        return None


@shared_task(bind=True)
def generate_tts_task(self, job_id: str, lesson_json: dict):
    """Generate TTS audio from lesson content."""
    _update_progress_sync(
        job_id, ProductType.tts, TaskStatus.in_progress, 10,
        message="正在合成语音..."
    )

    try:
        from services.voice import VoiceGenerator
        generator = VoiceGenerator()
        generator.generate(lesson_json)

        _update_progress_sync(
            job_id, ProductType.tts, TaskStatus.completed, 100,
            message="语音合成完成",
            download_url=f"/api/download/tts/{job_id}"
        )

    except Exception as e:
        _update_progress_sync(
            job_id, ProductType.tts, TaskStatus.failed, 0,
            error=str(e)
        )


@shared_task(bind=True)
def generate_ppt_task(self, job_id: str, lesson_json: dict):
    """Generate PPT from lesson content."""
    _update_progress_sync(
        job_id, ProductType.ppt, TaskStatus.in_progress, 10,
        message="正在生成 PPT..."
    )

    try:
        from services.ppt import PPTGenerator
        generator = PPTGenerator()
        generator.generate(lesson_json)

        _update_progress_sync(
            job_id, ProductType.ppt, TaskStatus.completed, 100,
            message="PPT生成完成",
            download_url=f"/api/download/ppt/{job_id}"
        )

    except Exception as e:
        _update_progress_sync(
            job_id, ProductType.ppt, TaskStatus.failed, 0,
            error=str(e)
        )