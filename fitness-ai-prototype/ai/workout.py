"""Structured workout proposal with deterministic basic checks."""
from .common import generate, payload
from .context import missing_fields

def validate_workout(plan, profile):
    errors = []
    sessions = plan.get('sessions') if isinstance(plan, dict) else None
    if not isinstance(sessions, list) or not sessions:
        return ['sessions must be a nonempty list']
    if len(sessions) != profile.get('days_per_week'):
        errors.append('session count differs from days_per_week')
    for i, session in enumerate(sessions):
        if not isinstance(session, dict) or not isinstance(session.get('exercises'), list) or not session['exercises']:
            errors.append(f'session {i}: missing exercises')
            continue
        for ex in session['exercises']:
            if not isinstance(ex, dict) or not isinstance(ex.get('name'), str) or not ex['name'].strip():
                errors.append(f'session {i}: missing exercise name')
                continue
            if not isinstance(ex.get('sets'), int) or not 1 <= ex['sets'] <= 6:
                errors.append(f'{ex["name"]}: invalid sets')
            if not isinstance(ex.get('reps'), str) or not ex['reps'].strip():
                errors.append(f'{ex["name"]}: missing reps')
            if not isinstance(ex.get('rest_seconds'), int) or not 0 <= ex['rest_seconds'] <= 300:
                errors.append(f'{ex["name"]}: invalid rest_seconds')
    return errors

def generate_workout(profile, history=None, *, client=None):
    missing = missing_fields(profile)
    if missing:
        return {'type': 'clarification', 'message': 'Cần bổ sung thông tin trước khi lập lịch tập.', 'missing_fields': missing}
    if profile.get('physical_limitations') is None:
        return {'type': 'clarification', 'message': 'Bạn có chấn thương hoặc hạn chế vận động nào cần lưu ý không?', 'missing_fields': ['physical_limitations']}
    instruction = '''You design conservative beginner-friendly educational resistance-training proposals, not medical treatment.
Only use equipment listed in the profile; do not assume a bench or machines. Respect training days, experience, session duration, and limitations.
Avoid exercises the user said they dislike in conversation history. Never invent a user's available clock time.
Return ONLY JSON object: {"type":"workout_plan","summary":"...","sessions":[{"day_label":"Buổi 1","duration_minutes":60,"exercises":[{"name":"...","sets":3,"reps":"8-12","rest_seconds":90,"equipment":["dumbbells"]}]}],"notes":["..."]}.
Each session should be realistic for duration, with warm-up and safe progression in notes.'''
    result = generate(payload(profile=profile, history=(history or [])[-12:]), instruction=instruction, json_output=True, max_tokens=4096, client=client)
    issues = validate_workout(result, profile)
    if issues:
        return {'type': 'validation_error', 'message': 'Workout proposal needs review', 'issues': issues, 'draft': result}
    return result

def format_workout(plan):
    lines = [plan.get("summary", "Kế hoạch tập luyện")]

    for session in plan.get("sessions", []):
        lines.append(f"\n{session['day_label']}")

        for exercise in session["exercises"]:
            lines.append(
                f"- {exercise['name']}: "
                f"{exercise['sets']} hiệp x {exercise['reps']}, "
                f"nghỉ {exercise['rest_seconds']} giây"
            )

    return "\n".join(lines)
