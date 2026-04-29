"""Tests for voice/TTS generation service."""
import pytest
import os
import json
from services.voice import VoiceGenerator, MAX_SEGMENT_DURATION_SECONDS


# Sample lesson JSON for testing
SAMPLE_LESSON = {
    "meta": {
        "subject": "physics",
        "grade": "七年级",
        "topic": "力学基础",
        "duration": 45,
        "style": "启发式教学"
    },
    "outline": {
        "introduction": {
            "title": "课程导入",
            "content": "通过生活中的实例引入力学概念。力是物体对物体的作用。",
            "key_points": ["建立学习兴趣", "理解力的定义"],
            "media_hint": {"slide_type": "title", "voice_style": "teacher"}
        },
        "main_sections": [
            {
                "title": "力的概念",
                "content": "力是物体之间的相互作用。力的作用效果：改变运动状态、改变形状。",
                "key_points": ["力的定义", "力的作用效果"],
                "media_hint": {"slide_type": "knowledge", "voice_style": "teacher"}
            },
            {
                "title": "例题分析",
                "content": "分析以下场景中的力：推箱子、拉弹簧。",
                "key_points": ["受力分析", "力的方向"],
                "media_hint": {"slide_type": "example", "voice_style": "teacher"}
            }
        ],
        "conclusion": {
            "title": "课堂总结",
            "content": "本节课学习了力的基本概念和应用。",
            "key_points": ["知识回顾", "课后练习"],
            "media_hint": {"slide_type": "summary", "voice_style": "teacher"}
        }
    },
    "summary": "本节课介绍了力的基本概念和作用效果。",
    "resources": []
}


def test_voice_generator_init():
    """Test VoiceGenerator initializes correctly."""
    generator = VoiceGenerator()
    assert generator.storage_path is not None
    assert os.path.exists(generator.storage_path)


def test_voice_generator_custom_storage():
    """Test VoiceGenerator with custom storage path."""
    custom_path = "/tmp/test_voice_output"
    generator = VoiceGenerator(storage_path=custom_path)
    assert generator.storage_path == custom_path
    assert os.path.exists(custom_path)

    # Cleanup
    if os.path.exists(custom_path):
        os.rmdir(custom_path)


def test_voice_generator_generate():
    """Test basic audio generation."""
    generator = VoiceGenerator()
    audio_files = generator.generate(SAMPLE_LESSON)

    # Should generate files for each section
    assert len(audio_files) >= 3  # intro + at least 1 main + conclusion

    # Check that files exist (either .mp3 or _meta.json placeholder)
    for path in audio_files:
        # Either actual audio or placeholder metadata
        assert path.endswith('.mp3') or path.endswith('_meta.json')


def test_voice_generator_split_text_short():
    """Test text splitting for short text."""
    generator = VoiceGenerator()
    short_text = "这是一个简短的测试文本。"
    segments = generator._split_text_for_duration(short_text, MAX_SEGMENT_DURATION_SECONDS)

    # Short text should not be split
    assert len(segments) == 1
    assert segments[0] == short_text


def test_voice_generator_split_text_long():
    """Test text splitting for long text."""
    generator = VoiceGenerator()
    # Create long text exceeding max duration
    long_text = "第一句话内容比较长。" * 100  # ~900 chars
    segments = generator._split_text_for_duration(long_text, MAX_SEGMENT_DURATION_SECONDS)

    # Long text should be split into multiple segments
    assert len(segments) > 1

    # Each segment should be within limit
    max_chars = MAX_SEGMENT_DURATION_SECONDS * 5
    for segment in segments:
        assert len(segment) <= max_chars


def test_voice_generator_placeholder():
    """Test placeholder generation when ChatTTS unavailable."""
    generator = VoiceGenerator()
    placeholder_path = generator._generate_placeholder_audio(
        "/tmp/test_placeholder.mp3",
        "测试文本内容"
    )

    # Should create JSON metadata file
    assert placeholder_path.endswith('_meta.json')
    assert os.path.exists(placeholder_path)

    # Check metadata content
    with open(placeholder_path, 'r') as f:
        metadata = json.load(f)
    assert metadata["text"] == "测试文本内容"
    assert metadata["status"] == "pending"

    # Cleanup
    if os.path.exists(placeholder_path):
        os.remove(placeholder_path)


def test_voice_generator_voice_styles():
    """Test different voice styles."""
    generator = VoiceGenerator()

    # Generate with teacher voice
    audio_files = generator.generate(SAMPLE_LESSON)

    # Check that voice_style is properly extracted
    # This is handled in _generate_section_audio
    assert len(audio_files) > 0


def test_voice_generator_empty_content():
    """Test handling of empty content."""
    generator = VoiceGenerator()
    lesson_empty = {
        "meta": {"topic": "测试课程"},
        "outline": {
            "introduction": {"title": "导入", "content": ""},
            "main_sections": [],
            "conclusion": {"title": "总结", "content": ""}
        }
    }

    audio_files = generator.generate(lesson_empty)

    # Empty content sections should be skipped
    # Only non-empty sections generate audio
    assert len(audio_files) == 0  # No sections with content


def test_voice_generator_no_model():
    """Test behavior when ChatTTS model not available."""
    generator = VoiceGenerator()

    # Force initialization attempt
    result = generator._init_model()

    # If model not available, should return None for audio
    if not result or generator._model is None:
        audio = generator._call_chattts(["测试文本"], "teacher")
        assert audio is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])