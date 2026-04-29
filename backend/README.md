# YaeTeaching Backend

FastAPI backend for AI-powered teaching content generation.

## Structure

```
backend/
├── app/              # FastAPI application
│   ├── main.py       # Entry point
│   ├── router.py     # API routes
│   └── websocket.py  # WebSocket handlers
├── celery/           # Async task workers
│   ├── tasks.py      # Task definitions
│   └── config.py     # Celery config
├── models/           # Pydantic data models
│   ├── lesson.py     # Lesson schema
│   ├── job.py        # Job status schema
│   └── request.py    # API request models
├── services/         # Business logic
│   ├── lesson.py     # Lesson generation
│   ├── voice.py      # TTS service
│   └── ppt.py        # PPT generation
├── config/           # Configuration
│   └── settings.py   # Environment settings
└── tests/            # Unit tests
```

## Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Environment

Required environment variables:
- `DEEPSEEK_API_KEY`: DeepSeek LLM API key
- `REDIS_URL`: Redis connection URL
- `MINIO_ENDPOINT`: MinIO storage endpoint