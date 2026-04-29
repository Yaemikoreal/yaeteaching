"""API routes for generation endpoints."""
from fastapi import APIRouter, HTTPException
from uuid import uuid4
from models.request import GenerateRequest, GenerateResponse
from models.job import JobStatus, TaskProgress, TaskStatus, ProductType
from datetime import datetime

api_router = APIRouter()

# In-memory job storage (replace with Redis/Postgres later)
jobs: dict[str, JobStatus] = {}


def create_initial_tasks() -> list[TaskProgress]:
    """Create initial task progress list."""
    return [
        TaskProgress(type=ProductType.lesson, status=TaskStatus.pending, progress=0),
        TaskProgress(type=ProductType.tts, status=TaskStatus.pending, progress=0),
        TaskProgress(type=ProductType.ppt, status=TaskStatus.pending, progress=0),
        TaskProgress(type=ProductType.video, status=TaskStatus.pending, progress=0),
    ]


@api_router.post("/generate", response_model=GenerateResponse)
async def generate_lesson_plan(request: GenerateRequest):
    """Create a new lesson generation job."""
    job_id = str(uuid4())

    job = JobStatus(
        job_id=job_id,
        status=TaskStatus.pending,
        tasks=create_initial_tasks(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    jobs[job_id] = job

    # TODO: Trigger Celery task for async processing
    # from celery.tasks import start_generation_pipeline
    # start_generation_pipeline.delay(job_id, request.dict())

    return GenerateResponse(job_id=job_id, message="任务已创建，正在处理")


@api_router.get("/job/{job_id}/status", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get current status of a generation job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return jobs[job_id]


@api_router.get("/download/{product_type}/{job_id}")
async def get_download_url(product_type: str, job_id: str):
    """Get download URL for a generated product."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    task = next((t for t in job.tasks if t.type == product_type), None)

    if not task or task.status != TaskStatus.completed:
        raise HTTPException(
            status_code=400, detail="Product not ready for download"
        )

    return {"download_url": task.download_url}