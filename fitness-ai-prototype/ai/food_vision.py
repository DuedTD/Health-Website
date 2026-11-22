"""General image understanding using Gemini."""

import mimetypes
from pathlib import Path
from google.genai import types
from .common import generate


def analyze_food_image(image_path, question=None, *, client=None):
    path = Path(image_path)

    if not path.is_file():
        raise FileNotFoundError(path)

    if path.stat().st_size > 10 * 1024 * 1024:
        raise ValueError("Image exceeds demo 10 MB limit")

    mime, _ = mimetypes.guess_type(path.name)

    if mime not in ("image/jpeg", "image/png", "image/webp"):
        raise ValueError("Use JPG, PNG or WebP")

    if not question:
        question = "Hãy mô tả và giải thích nội dung hình ảnh này."

    prompt = [
        types.Part.from_bytes(
            data=path.read_bytes(),
            mime_type=mime
        ),
        question
    ]

    instruction = """
You are a helpful AI image understanding assistant.

CAPABILITIES:
- Understand and describe images.
- Identify visible objects and activities.
- Recognize food, fitness equipment and exercises.
- Explain diagrams and educational illustrations.
- Answer questions about image content.
- Respond in the user's language.

FITNESS:
- Identify visible exercise equipment.
- Explain which muscles an exercise may target.
- Describe observable exercise posture.
- Do not claim that a single image proves
  correct or incorrect exercise technique.

NUTRITION:
- Identify visible foods and ingredients.
- Explain their general nutritional roles.
- Do not calculate calories unless explicitly
  requested and sufficient information exists.
- Acknowledge uncertainty about ingredients
  and portion sizes.

SAFETY:
- Do not diagnose medical conditions from images.
- Do not infer hidden health conditions.
- Do not invent details that are not visible.
- Explain uncertainty when necessary.

OUTPUT:
- Return natural-language text.
- Do not return JSON.
"""

    answer = generate(
        prompt,
        instruction=instruction,
        client=client
    )

    if not isinstance(answer, str):
        raise ValueError("Invalid image response")

    return {
        "type": "image_analysis",
        "message": answer
    }
