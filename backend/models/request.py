"""Pydantic models for API requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional


class GenerateRequest(BaseModel):
    """Request model for lesson generation."""

    subject: str = Field(..., description="学科：数学、物理、语文等")
    grade: str = Field(..., description="年级：如 7年级、高一")
    duration: int = Field(..., ge=15, le=120, description="课程时长（分钟）")
    topic: str = Field(..., description="教学主题/知识点")
    style: Optional[str] = Field(None, description="教学风格")


class GenerateResponse(BaseModel):
    """Response model for generation request."""

    job_id: str = Field(..., description="任务ID")
    message: str = Field("任务已创建，正在处理")