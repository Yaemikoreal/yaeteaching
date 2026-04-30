"""Lesson generation service using LLM."""
import json
import httpx
from typing import Dict, Any
from config.settings import settings


# Prompt template for lesson generation
LESSON_PROMPT_TEMPLATE = """你是一位专业的教案编写专家。请根据以下要求生成一份结构化的教案。

## 要求
- 学科: {subject}
- 年级: {grade}
- 教学主题: {topic}
- 课程时长: {duration} 分钟
- 教学风格: {style}

## 输出格式
请严格按照以下 JSON 格式输出教案，不要添加任何额外内容：

```json
{{"meta": {{...}}, "outline": {{...}}, "summary": "...", "resources": []}}
```

输出必须包含以下结构：
- meta: 学科、年级、主题、时长、风格等元信息
- outline: 包含 introduction（导入）、main_sections（2-3个核心知识点或例题）、conclusion（总结）
- 每个章节需包含 title、content、key_points、media_hint（slide_type）
- slide_type 可选值：title、knowledge、example、summary

## 要求说明
1. 根据学科特点设计教学内容
2. 内容要符合年级学生的认知水平
3. main_sections 至少包含2-3个核心知识点或例题
4. key_points 每个知识点列出2-3个关键要素
5. 确保输出是合法的 JSON 格式
"""


class LessonGenerator:
    """Generate structured lesson plan via LLM API."""

    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

    def __init__(self):
        self.deepseek_key = settings.deepseek_api_key
        self.openai_key = settings.openai_api_key
        self.client = httpx.Client(timeout=60.0)

    def generate(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate lesson JSON from request parameters.

        Args:
            request_data: GenerateRequest dict with subject, grade, topic, etc.

        Returns:
            Lesson JSON dict conforming to LessonJSON schema
        """
        # Try DeepSeek first, fallback to OpenAI, finally use template
        prompt = self._build_prompt(request_data)

        # Try DeepSeek API
        if self.deepseek_key:
            try:
                response_text = self._call_deepseek(prompt)
                return self._parse_llm_response(response_text)
            except Exception as e:
                print(f"DeepSeek API failed: {e}")

        # Fallback to OpenAI API
        if self.openai_key:
            try:
                response_text = self._call_openai(prompt)
                return self._parse_llm_response(response_text)
            except Exception as e:
                print(f"OpenAI API failed: {e}")

        # Final fallback to template
        return self._generate_template(request_data)

    def _build_prompt(self, request_data: Dict[str, Any]) -> str:
        """Build prompt from request parameters."""
        return LESSON_PROMPT_TEMPLATE.format(
            subject=request_data.get("subject", "数学"),
            grade=request_data.get("grade", "7年级"),
            topic=request_data.get("topic", "示例主题"),
            duration=request_data.get("duration", 45),
            style=request_data.get("style") or "启发式教学",
        )

    def _call_deepseek(self, prompt: str) -> str:
        """Call DeepSeek API with prompt."""
        headers = {
            "Authorization": f"Bearer {self.deepseek_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一位专业的教案编写专家，擅长生成结构化的教学方案。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000,
        }
        response = self.client.post(
            self.DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API with prompt."""
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "你是一位专业的教案编写专家，擅长生成结构化的教学方案。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000,
        }
        response = self.client.post(
            self.OPENAI_API_URL,
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response and extract JSON."""
        # Try to extract JSON from response
        # Remove markdown code block markers if present
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            lesson_json = json.loads(text)
            # Validate basic structure
            if "meta" in lesson_json and "outline" in lesson_json:
                return lesson_json
        except json.JSONDecodeError:
            pass

        # If parsing fails, raise error
        raise ValueError("Failed to parse valid lesson JSON from LLM response")

    def _generate_template(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a template lesson for testing/fallback."""
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