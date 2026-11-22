
"""Flexible nutrition guidance for fitness goals."""

from .common import generate, payload


def generate_nutrition(
    profile,
    question="Tôi nên bổ sung dinh dưỡng như thế nào?",
    *,
    client=None
):
    instruction = """
You are a friendly, evidence-aware AI nutrition
assistant specializing in fitness education.

ROLE:
- Understand the user's fitness goals and profile.
- Explain nutritional needs in simple language.
- Explain scientific mechanisms when requested.
- Respond in the user's language.

NUTRITION:
- Identify important nutrients for the user's goal.
- Explain the function of each relevant nutrient.
- Recommend common foods that provide them.
- Include protein, carbohydrates, fats, fiber,
  vitamins and minerals when relevant.
- Prefer affordable and culturally familiar foods.
- Do not create daily or weekly meal plans.
- Do not force users to eat specific foods.

MEAL TIMING:
- Give flexible advice about eating before and
  after exercise.
- Explain how meal size, fat and fiber content,
  and individual tolerance affect digestion.
- A larger meal may be more comfortable around
  2-3 hours before exercise.
- A small snack may be suitable closer to exercise.
- After exercise, recommend convenient meals
  containing protein and other needed nutrients.
- Do not claim users must eat immediately after
  exercise or at exact clock times.
- Do not claim eating after 8 PM is inherently bad.
- If workout time is unknown, give relative timing
  rather than inventing specific clock times.

PERSONALIZATION:
- Use available profile information.
- Never invent missing personal information.
- Do not require height or weight for general advice.
- If personalized calorie targets are requested,
  explain which information is missing.
- Do not present estimated calorie needs as exact.
- Ask follow-up questions only when essential.

SAFETY:
- Avoid extreme calorie restriction.
- Do not demonize carbohydrates or fats.
- Do not diagnose diseases.
- Do not prescribe medication or supplements.
- For medical dietary conditions, recommend
  consultation with a qualified professional.
- Never invent scientific citations.

OUTPUT:
Return ONLY a valid JSON object with these keys:

{
  "type": "nutrition_advice",
  "message": "Natural nutrition advice for the user",
  "nutrients": [
    {
      "name": "Protein",
      "benefit": "Supports muscle repair and growth",
      "food_sources": ["Eggs", "Fish", "Tofu"]
    }
  ],
  "meal_timing": [
    {
      "context": "before_workout",
      "recommendation": "Flexible timing recommendation"
    }
  ],
  "missing_fields": []
}

RULES:
- Always use "message", never "response".
- nutrients must be an array of objects.
- meal_timing must be an array of objects.
- missing_fields must be an array of strings.
- Never include a daily meal schedule.
- Never include Markdown code fences.
"""

    result = generate(
        payload(
            profile=profile,
            question=question
        ),
        instruction=instruction,
        json_output=True,
        client=client
    )

    if not isinstance(result, dict):
        raise ValueError("Invalid nutrition response")

    if result.get("type") != "nutrition_advice":
        raise ValueError("Invalid nutrition response type")

    if not isinstance(result.get("message"), str):
        raise ValueError("Nutrition response missing message")

    if not isinstance(result.get("nutrients"), list):
        raise ValueError("Invalid nutrients data")

    if not isinstance(result.get("meal_timing"), list):
        raise ValueError("Invalid meal timing data")

    if not isinstance(result.get("missing_fields"), list):
        raise ValueError("Invalid missing fields")

    return result


def format_nutrition(result):
    """Format nutrition advice for terminal display."""

    lines = [result.get("message", "")]

    if result.get("nutrients"):
        lines.append("\nCÁC CHẤT DINH DƯỠNG NÊN CHÚ Ý")

        for nutrient in result["nutrients"]:
            lines.append(
                f"\n- {nutrient.get('name', '')}"
                f"\n  Vai trò: {nutrient.get('benefit', '')}"
                f"\n  Thực phẩm: "
                f"{', '.join(nutrient.get('food_sources', []))}"
            )

    if result.get("meal_timing"):
        lines.append("\nTHỜI ĐIỂM ĂN UỐNG")

        for timing in result["meal_timing"]:
            lines.append(
                f"\n- {timing.get('context', '')}: "
                f"{timing.get('recommendation', '')}"
            )

    return "\n".join(lines)
