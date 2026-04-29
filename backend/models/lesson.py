"""Lesson JSON Schema definition."""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class SlideType(str, Enum):
    """PPT slide types."""

    title = "title"
    knowledge = "knowledge"
    example = "example"
    summary = "summary"
    exercise = "exercise"


class MediaHint(BaseModel):
    """Media generation hints for a section."""

    slide_type: Optional[SlideType] = None
    voice_style: Optional[str] = None  # 教师音/学生音
    duration_hint: Optional[int] = None  # 预估时长


class LessonSection(BaseModel):
    """Single section/chapter of lesson."""

    title: str
    content: str
    key_points: List[str] = Field(default_factory=list)
    media_hint: Optional[MediaHint] = None


class LessonMeta(BaseModel):
    """Lesson metadata."""

    subject: str
    grade: str
    topic: str
    duration: int
    style: Optional[str] = None
    author: Optional[str] = None


class LessonOutline(BaseModel):
    """Lesson outline structure."""

    introduction: LessonSection
    main_sections: List[LessonSection] = Field(default_factory=list)
    conclusion: LessonSection


class LessonResource(BaseModel):
    """External resource reference."""

    type: str  # video, image, document
    url: Optional[str] = None
    description: str


class LessonJSON(BaseModel):
    """Complete lesson plan JSON schema."""

    meta: LessonMeta
    outline: LessonOutline
    summary: str
    resources: List[LessonResource] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "meta": {
                    "subject": "数学",
                    "grade": "7年级",
                    "topic": "一元一次方程",
                    "duration": 45,
                    "style": "启发式教学"
                },
                "outline": {
                    "introduction": {
                        "title": "导入",
                        "content": "通过生活中的例子引入方程概念...",
                        "key_points": ["方程的定义"],
                        "media_hint": {"slide_type": "title"}
                    },
                    "main_sections": [
                        {
                            "title": "方程的基本概念",
                            "content": "详细讲解...",
                            "key_points": ["未知数", "等式"],
                            "media_hint": {"slide_type": "knowledge"}
                        }
                    ],
                    "conclusion": {
                        "title": "总结",
                        "content": "回顾本节课重点...",
                        "key_points": [],
                        "media_hint": {"slide_type": "summary"}
                    }
                },
                "summary": "本节课学习了方程的基本概念...",
                "resources": []
            }
        }