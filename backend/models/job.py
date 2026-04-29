"""Job status tracking models."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Status of individual tasks."""

    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class ProductType(str, Enum):
    """Types of generated products."""

    lesson = "lesson"
    tts = "tts"
    ppt = "ppt"
    video = "video"


class TaskProgress(BaseModel):
    """Progress of a single task."""

    type: ProductType
    status: TaskStatus = TaskStatus.pending
    progress: int = Field(0, ge=0, le=100)
    message: Optional[str] = None
    error: Optional[str] = None
    download_url: Optional[str] = None


class JobStatus(BaseModel):
    """Overall job status."""

    job_id: str
    status: TaskStatus = TaskStatus.pending
    tasks: List[TaskProgress] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProgressMessage(BaseModel):
    """WebSocket progress push message."""

    job_id: str
    task_type: ProductType
    status: TaskStatus
    progress: int = Field(0, ge=0, le=100)
    message: Optional[str] = None
    error: Optional[str] = None
    download_url: Optional[str] = None