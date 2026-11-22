"""Standalone one-person terminal demo. Not a multiuser server."""
import json
from pathlib import Path
from unittest import result
from ai.context import fitness_ai
from ai.workout import generate_workout, format_workout
from ai.nutrition import generate_nutrition, format_nutrition
from ai.rag import answer_with_sources
from ai.food_vision import analyze_food_image
from ai.speech import transcribe_audio, listen_microphone

ROOT = Path(__file__).resolve().parent


def main():
    profile = json.loads((ROOT / 'data/profile.txt').read_text(encoding='utf-8'))
    history = []

    print('Fitness AI demo. Commands: /workout, /nutrition, /rag QUESTION, /image PATH, /audio PATH, /quit')
    print('Demo profile. Confirmed changes are saved locally.')

    while True:
        text = input('\nYou: ').strip()
        if text == "/audio":
            try:
                text = listen_microphone()
        

                if not text:
                    print("Không nhận diện được lời nói.")
                    continue

                print("\nRecognized:", text)

            except Exception as exc:
                print("Speech recognition error:", exc)
                continue

        if text in ('/quit', 'exit'):
            break

        if not text:
            continue

        try:
            if text == '/workout':
                result = generate_workout(profile, history)
                if result.get("type") == "workout_plan":
                    print("\nAI:\n" + format_workout(result))

                    workout_path = ROOT / "data/workoutplan.txt"

                    workout_path.write_text(
                    json.dumps(result, ensure_ascii=False, indent=2),
                    encoding="utf-8"
        )

                    print("\nĐã lưu kế hoạch vào workoutplan.txt")

                else:
                    print("\nAI:", result.get("message", "Không thể tạo kế hoạch."))

                continue

            elif text == '/nutrition' or text.startswith('/nutrition '):
                question = text[len('/nutrition'):].strip()

                if not question:
                    question = "Tôi nên bổ sung dinh dưỡng như thế nào?"

                result = generate_nutrition(profile, question)

                print("\nAI:\n" + format_nutrition(result))

                nutrition_path = ROOT / "data/nutrition.txt"

                nutrition_path.write_text(
                    json.dumps(result, ensure_ascii=False, indent=2),
                    encoding="utf-8"
    )
                

                continue
            elif text.startswith('/rag '):
                question = text[5:].strip()
                result = answer_with_sources(
                    question,
                    ROOT / 'knowledge/documents'
    )
                answer = result["message"]
                print("\nAI:", answer)

                if result.get("sources"):
                    print("\nNguồn tham khảo:")

                    for source in result["sources"]:
                        print(
                            f"- {source['source']} "
                            f"(đoạn {source['chunk']})"
            )
                history.extend([
                    {"role": "user", "content": question},
                    {"role": "model", "content": answer}
    ])
                continue

            elif text.startswith('/image '):
                result = analyze_food_image(text[7:].strip(' "'))

            elif text.startswith('/audio '):
                result = transcribe_audio(text[7:].strip(' "'))

            else:
                result = fitness_ai(text, profile, history)

                updates = result.get("proposed_profile_updates", {})

                if isinstance(updates, dict) and updates:
                    allowed_fields = {
                        "goal",
                        "experience",
                        "days_per_week",
                        "minutes_per_session",
                        "equipment",
                        "physical_limitations",
                        "height_cm",
                        "weight_kg"
                    }

                    valid_updates = {
                        key: value
                        for key, value in updates.items()
                        if key in allowed_fields and profile.get(key) != value
                    }

                    if "days_per_week" in valid_updates:
                        days = valid_updates["days_per_week"]

                        if type(days) is not int or not 1 <= days <= 7:
                            print("Số buổi tập không hợp lệ.")
                            valid_updates.pop("days_per_week")

                    if valid_updates:
                        print("\nAI đề xuất cập nhật hồ sơ:", valid_updates)

                        confirm = input(
                            "Bạn có muốn lưu thay đổi? (y/n): "
                        ).strip().lower()

                        if confirm == "y":
                            new_profile = profile.copy()
                            new_profile.update(valid_updates)

                            profile_path = ROOT / "data/profile.txt"
                            temp_path = profile_path.with_suffix(".tmp")

                            temp_path.write_text(
                                json.dumps(
                                    new_profile,
                                    ensure_ascii=False,
                                    indent=2
                                ),
                                encoding="utf-8"
                            )

                            temp_path.replace(profile_path)
                            profile.update(valid_updates)

                            print("Đã lưu hồ sơ!")
                            result["proposed_profile_updates"] = {}

                if isinstance(result, dict):
                    answer = result.get("message")

                    if isinstance(answer, str) and answer:
                        history.extend([
                            {"role": "user", "content": text},
                            {"role": "model", "content": answer}
        ])

            if isinstance(result, dict) and "message" in result:
                print("\nAI:", result["message"])
            else:
                print(
                    "\nAI:",
                    json.dumps(result, ensure_ascii=False, indent=2)
                )

        except Exception as exc:
            print(f'Unable to complete request: {exc}')


if __name__ == '__main__':
    main()
