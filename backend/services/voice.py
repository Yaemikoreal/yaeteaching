"""Voice/TTS generation service using ChatTTS."""
import os
import tempfile
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from config.settings import settings
from models.lesson import LessonJSON


logger = logging.getLogger(__name__)

# Maximum duration per segment in seconds (2 minutes = 120 seconds)
MAX_SEGMENT_DURATION_SECONDS = 120


class VoiceGenerator:
    """Generate audio from lesson content using ChatTTS."""

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize voice generator.

        Args:
            storage_path: Directory to store generated audio files.
                         Defaults to /tmp/audio or settings.storage_path
        """
        self.storage_path = storage_path or getattr(
            settings, 'storage_path', '/tmp/audio'
        )
        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)

        # Initialize ChatTTS model (lazy loading)
        self._model = None
        self._initialized = False

    def _init_model(self):
        """Initialize ChatTTS model (lazy loading)."""
        if self._initialized:
            return self._model is not None

        try:
            import ChatTTS
            self._model = ChatTTS.Chat()
            # Use default sample rate and device
            self._model.load(compile=False)  # compile=False for faster loading
            self._initialized = True
            logger.info("ChatTTS model loaded successfully")
            return True
        except ImportError:
            logger.warning("ChatTTS not installed, using fallback")
            self._initialized = True
            self._model = None
            return False
        except Exception as e:
            logger.error(f"Failed to load ChatTTS model: {e}")
            self._initialized = True
            self._model = None
            return False

    def generate(self, lesson_json: Dict[str, Any]) -> List[str]:
        """Generate audio files for each section.

        Args:
            lesson_json: Lesson JSON dict

        Returns:
            List of audio file paths
        """
        audio_files = []
        meta = lesson_json.get("meta", {})
        topic = meta.get("topic", "lesson")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Extract sections to convert
        outline = lesson_json.get("outline", {})
        sections = []

        # Introduction
        intro = outline.get("introduction", {})
        if intro and intro.get("content"):
            sections.append(("导入", intro))

        # Main sections
        for i, section in enumerate(outline.get("main_sections", [])):
            if section and section.get("content"):
                sections.append((section.get("title", f"章节{i+1}"), section))

        # Conclusion
        conclusion = outline.get("conclusion", {})
        if conclusion and conclusion.get("content"):
            sections.append(("总结", conclusion))

        # Generate audio for each section
        for i, (title, section) in enumerate(sections):
            audio_path = self._generate_section_audio(
                title=title,
                content=section.get("content", ""),
                index=i,
                topic=topic,
                timestamp=timestamp,
                voice_style=section.get("media_hint", {}).get("voice_style", "teacher")
            )
            audio_files.append(audio_path)

        return audio_files

    def _generate_section_audio(
        self,
        title: str,
        content: str,
        index: int,
        topic: str,
        timestamp: str,
        voice_style: str = "teacher"
    ) -> str:
        """Generate audio for a single section.

        Args:
            title: Section title
            content: Section content text
            index: Section index
            topic: Lesson topic
            timestamp: Timestamp for filename
            voice_style: Voice style (teacher/student)

        Returns:
            Path to generated audio file
        """
        # Combine title and content for narration
        full_text = f"{title}。{content}"

        # Split into segments if text is too long
        segments = self._split_text_for_duration(full_text, MAX_SEGMENT_DURATION_SECONDS)

        # Generate filename
        filename = f"{topic}_{timestamp}_section_{index}.mp3"
        output_path = os.path.join(self.storage_path, filename)

        # Generate audio
        try:
            audio_data = self._call_chattts(segments, voice_style)
            if audio_data:
                # Save to file
                self._save_audio(audio_data, output_path)
                return output_path
        except Exception as e:
            logger.error(f"Failed to generate audio for section {index}: {e}")

        # Fallback: return placeholder path
        return self._generate_placeholder_audio(output_path, full_text)

    def _split_text_for_duration(self, text: str, max_duration_seconds: int) -> List[str]:
        """Split text into segments that fit within max duration.

        ChatTTS roughly generates 1 second of audio per 5-10 characters.
        We use conservative estimate: 1 second per 5 characters.

        Args:
            text: Full text to split
            max_duration_seconds: Maximum duration per segment

        Returns:
            List of text segments
        """
        # Conservative estimate: 5 chars per second
        max_chars_per_segment = max_duration_seconds * 5

        # If text is short enough, return as single segment
        if len(text) <= max_chars_per_segment:
            return [text]

        # Split by sentences (Chinese punctuation)
        import re
        sentences = re.split(r'([。！？；])', text)
        sentences = [''.join(pair) for pair in zip(sentences[::2], sentences[1::2] or [''])]

        # Combine sentences into segments within limit
        segments = []
        current_segment = ""

        for sentence in sentences:
            if len(current_segment) + len(sentence) <= max_chars_per_segment:
                current_segment += sentence
            else:
                if current_segment:
                    segments.append(current_segment)
                current_segment = sentence

        if current_segment:
            segments.append(current_segment)

        return segments

    def _call_chattts(self, text_segments: List[str], voice_style: str = "teacher") -> Optional[bytes]:
        """Call ChatTTS for text-to-speech.

        Args:
            text_segments: List of text segments to synthesize
            voice_style: Voice style (teacher/student)

        Returns:
            Combined audio data as bytes, or None if fallback needed
        """
        # Try to initialize model
        if not self._init_model():
            logger.warning("ChatTTS model not available, using placeholder")
            return None

        if self._model is None:
            return None

        try:
            import torchaudio

            # Generate audio for each segment
            audio_segments = []

            # Set voice parameters based on style
            # ChatTTS supports different voice styles through rand_spk_emb
            if voice_style == "teacher":
                # More formal, clear voice
                spk_emb = self._model.sample_random_speaker()
            else:
                # Student voice - slightly different
                spk_emb = self._model.sample_random_speaker()

            for segment in text_segments:
                if not segment.strip():
                    continue

                # Generate audio using ChatTTS
                wavs = self._model.infer(
                    [segment],
                    spk_emb=spk_emb,
                    temperature=0.3,  # Lower for more stable output
                    top_P=0.7,
                    top_K=20,
                )

                if wavs and len(wavs) > 0:
                    audio_segments.append(wavs[0])

            # Combine all segments
            if audio_segments:
                import torch
                combined = torch.cat(audio_segments, dim=1)
                # Convert to bytes
                buffer = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                torchaudio.save(buffer.name, combined, 24000, format='mp3')
                with open(buffer.name, 'rb') as f:
                    audio_bytes = f.read()
                os.unlink(buffer.name)
                return audio_bytes

        except ImportError as e:
            logger.warning(f"Missing dependency for ChatTTS audio: {e}")
        except Exception as e:
            logger.error(f"ChatTTS generation failed: {e}")

        return None

    def _save_audio(self, audio_data: bytes, output_path: str):
        """Save audio data to file.

        Args:
            audio_data: Audio bytes
            output_path: Output file path
        """
        with open(output_path, 'wb') as f:
            f.write(audio_data)
        logger.info(f"Audio saved to {output_path}")

    def _generate_placeholder_audio(self, output_path: str, text: str) -> str:
        """Generate placeholder audio metadata when ChatTTS unavailable.

        Args:
            output_path: Intended output path
            text: Text content for metadata

        Returns:
            Path to placeholder file
        """
        # Create a JSON metadata file as placeholder
        placeholder_path = output_path.replace('.mp3', '_meta.json')
        import json

        metadata = {
            "text": text,
            "status": "pending",
            "message": "ChatTTS integration pending - audio not generated",
            "generated_at": datetime.now().isoformat()
        }

        with open(placeholder_path, 'w') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        logger.warning(f"Placeholder audio metadata saved to {placeholder_path}")
        return placeholder_path