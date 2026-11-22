# Fitness AI — standalone Python prototype

This is a **prototype**, not a clinically validated health application or production multiuser service. It does not diagnose disease. No account management, database, scheduler or frontend is included.

## Setup (Windows PowerShell)

```powershell
cd fitness-ai-prototype
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:GEMINI_API_KEY="YOUR_KEY"
python chatbot.py
```

Default model: `gemini-3.5-flash-lite`. Override with `$env:GEMINI_MODEL="MODEL_NAME"`. Model availability, multimodal capabilities and free quotas depend on your Google account and can change.

Commands: ordinary chat, `/workout`, `/nutrition`, `/rag your question`, `/image C:\path\food.jpg`, `/audio C:\path\speech.wav`, `/quit`.

To test without API credentials (mocked API calls):

```powershell
python -m unittest discover -s tests -v
```

## Module contracts

- `fitness_ai(message: str, profile: dict, history: list, current_schedule=None) -> dict`
- `generate_workout(profile: dict, history: list | None) -> dict`
- `generate_nutrition(profile: dict, question: str) -> dict`
- `answer_with_sources(question: str, directory: str) -> dict`
- `analyze_food_image(image_path: str) -> dict`
- `transcribe_audio(audio_path: str) -> dict`

All functions receive their data as arguments; the terminal demo alone reads `data/profile.txt`. It holds chat history in RAM only. It does not persist profiles or histories.

## Limitations and next steps

- The context model proposes profile updates but does not apply them; backend/UI must obtain confirmation.
- Workout validation checks basic JSON shape and session count, **not** medical safety, exercise-to-equipment mapping, total duration, or physiological efficacy. A qualified human should review plans before relying on them.
- Nutrition advice is general, not an individualized medical or calorie prescription.
- RAG searches only local `.txt` documents using simple word overlap. You must curate sources, evaluate retrieval and verify citations against source text. Do not present it as evidence-based until this is done.
- Food-image and audio endpoints need supported multimodal model access. Image portion/calorie estimates are unreliable.
- Real deployment requires server-side secrets, authentication, user-specific access controls, storage, data retention/deletion, privacy consent and integration testing.
- A shared backend must never use global mutable history across users. Backend should provide only the authenticated user's profile/history.
- JSON model responses are checked only partially; use stronger schemas and semantic validators before production.
- API errors can occur (notably 429/503); retry only temporary overload errors, not exhausted quota.

## Integration rule

Keep module inputs/outputs stable. Backend can load a profile from a database and call the same functions; no AI module should read a hard-coded profile file.
