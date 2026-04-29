"""Celery async tasks for content generation."""
from celery import shared_task
from celery.config import celery_app
from models.job import TaskStatus, ProductType
from app.websocket import push_progress
import asyncio


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
    asyncio.run(push_progress(
        job_id, ProductType.lesson, TaskStatus.in_progress, 10,
        "正在调用 LLM 生成教案..."
    ))

    try:
        from services.lesson import LessonGenerator
        generator = LessonGenerator()
        lesson_json = generator.generate(request_data)

        asyncio.run(push_progress(
            job_id, ProductType.lesson, TaskStatus.completed, 100,
            "教案生成完成",
            download_url=f"/api/download/lesson/{job_id}"
        ))

        return lesson_json

    except Exception as e:
        asyncio.run(push_progress(
            job_id, ProductType.lesson, TaskStatus.failed, 0,
            error=str(e)
        ))
        return None


@shared_task(bind=True)
def generate_tts_task(self, job_id: str, lesson_json: dict):
    """Generate TTS audio from lesson content."""
    asyncio.run(push_progress(
        job_id, ProductType.tts, TaskStatus.in_progress, 10,
        "正在合成语音..."
    ))

    try:
        from services.voice import VoiceGenerator
        generator = VoiceGenerator()
        generator.generate(lesson_json)

        asyncio.run(push_progress(
            job_id, ProductType.tts, TaskStatus.completed, 100,
            "语音合成完成",
            download_url=f"/api/download/tts/{job_id}"
        ))

    except Exception as e:
        asyncio.run(push_progress(
            job_id, ProductType.tts, TaskStatus.failed, 0,
            error=str(e)
        ))


@shared_task(bind=True)
def generate_ppt_task(self, job_id: str, lesson_json: dict):
    """Generate PPT from lesson content."""
    asyncio.run(push_progress(
        job_id, ProductType.ppt, TaskStatus.in_progress, 10,
        "正在生成 PPT..."
    ))

    try:
        from services.ppt import PPTGenerator
        generator = PPTGenerator()
        generator.generate(lesson_json)

        asyncio.run(push_progress(
            job_id, ProductType.ppt, TaskStatus.completed, 100,
            "PPT生成完成",
            download_url=f"/api/download/ppt/{job_id}"
        ))

    except Exception as e:
        asyncio.run(push_progress(
            job_id, ProductType.ppt, TaskStatus.failed, 0,
            error=str(e)
        ))