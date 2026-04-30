"""PPT generation service using python-pptx."""
from pptx import Presentation
from config.settings import settings
from models.lesson import SlideType


class PPTGenerator:
    """Generate PowerPoint from lesson content."""

    def __init__(self):
        self.template_path = settings.minio_bucket  # TODO: actual template storage

    def generate(self, lesson_json: dict) -> str:
        """Generate PPT file from lesson JSON.

        Args:
            lesson_json: Lesson JSON dict

        Returns:
            Path to generated PPT file
        """
        prs = Presentation()
        outline = lesson_json.get("outline", {})
        meta = lesson_json.get("meta", {})

        # Title slide
        self._add_title_slide(prs, meta)

        # Introduction
        intro = outline.get("introduction", {})
        if intro:
            self._add_content_slide(prs, intro, SlideType.title)

        # Main sections
        for section in outline.get("main_sections", []):
            slide_type = section.get("media_hint", {}).get("slide_type", "knowledge")
            self._add_content_slide(prs, section, SlideType(slide_type) if slide_type else SlideType.knowledge)

        # Conclusion
        conclusion = outline.get("conclusion", {})
        if conclusion:
            self._add_content_slide(prs, conclusion, SlideType.summary)

        # Save to storage
        output_path = f"/storage/ppt/{meta.get('topic', 'lesson')}.pptx"
        prs.save(output_path)

        return output_path

    def _add_title_slide(self, prs: Presentation, meta: dict):
        """Add title slide with lesson metadata."""
        slide_layout = prs.slide_layouts[0]  # Title slide layout
        slide = prs.slides.add_slide(slide_layout)

        title = slide.shapes.title
        title.text = meta.get("topic", "课程")

        subtitle = slide.placeholders[1]
        subtitle.text = f"{meta.get('subject', '')} - {meta.get('grade', '')}"

    def _add_content_slide(self, prs: Presentation, section: dict, slide_type: SlideType):
        """Add content slide based on section and type."""
        slide_layout = prs.slide_layouts[1]  # Title and Content layout
        slide = prs.slides.add_slide(slide_layout)

        title = slide.shapes.title
        title.text = section.get("title", "")

        body = slide.placeholders[1]
        tf = body.text_frame
        tf.text = section.get("content", "")

        # Add key points as bullet list
        for point in section.get("key_points", []):
            p = tf.add_paragraph()
            p.text = point
            p.level = 1