"""Lesson generation service using LLM."""
import json
from typing import dict
from config.settings import settings
from models.lesson import LessonJSON, LessonMeta, LessonOutline, LessonSection


class LessonGenerator:
    """Generate structured lesson plan via LLM API."""

    def __init__(self):
        self.api_key = settings.deepseek_api_key
        # TODO: Initialize LLM client

    def generate(self, request_data: dict) -> dict:
        """Generate lesson JSON from request parameters.

        Args:
            request_data: GenerateRequest dict with subject, grade, topic, etc.

        Returns:
            Lesson JSON dict conforming to LessonJSON schema
        """
        # TODO: Implement actual LLM call
        # For now, return a template response

        return self._generate_template(request_data)

    def _generate_template(self, request_data: dict) -> dict:
        """Generate a template lesson for testing."""
        return {
            "meta": {
                "subject": request_data.get("subject", "数学"),
                "grade": request_data.get("grade", "7年级"),
                "topic": request_data.get("topic", "示例主题"),
                "duration": request_data.get("duration", 45),
                "style": request_data.get("style"),
            },
            "outline": {
                "introduction": {
                    "title": "课程导入",
                    "content": "通过生活中的实例引入本次课程主题...",
                    "key_points": ["建立学习兴趣"],
                    "media_hint": {"slide_type": "title"},
                },
                "main_sections": [
                    {
                        "title": "核心概念讲解",
                        "content": "详细讲解本次课程的核心知识点...",
                        "key_points": ["概念理解", "原理掌握"],
                        "media_hint": {"slide_type": "knowledge"},
                    },
                    {
                        "title": "例题分析",
                        "content": "通过具体例题加深理解...",
                        "key_points": ["解题方法", "技巧总结"],
                        "media_hint": {"slide_type": "example"},
                    },
                ],
                "conclusion": {
                    "title": "课堂总结",
                    "content": "回顾本节课的重点内容...",
                    "key_points": ["知识回顾", "课后练习建议"],
                    "media_hint": {"slide_type": "summary"},
                },
            },
            "summary": "本节课系统讲解了核心知识点，通过例题分析加深理解...",
            "resources": [],
        }

    def _call_llm(self, prompt: str) -> str:
        """Call LLM API with prompt.

        TODO: Implement DeepSeek/OpenAI API integration
        """
        # Placeholder for actual implementation
        raise NotImplementedError("LLM integration pending")