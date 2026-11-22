"""Shared Gemini access and typed JSON parsing."""
import json
import os
import time
from google import genai
from google.genai import types, errors

MODEL = os.getenv('GEMINI_MODEL', 'gemini-3.5-flash-lite')

class AIServiceError(RuntimeError):
    pass

def generate(prompt, *, instruction, json_output=False, max_tokens=2048, client=None):
    owned = client is None
    if owned:
        if not os.getenv('GEMINI_API_KEY'):
            raise AIServiceError('GEMINI_API_KEY is not set')
        client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    try:
        config = types.GenerateContentConfig(
            system_instruction=instruction,
            max_output_tokens=max_tokens,
            **({'response_mime_type': 'application/json'} if json_output else {})
        )
        for attempt in range(3):
            try:
                response = client.models.generate_content(model=MODEL, contents=prompt, config=config)
                if not response.text:
                    raise AIServiceError('Gemini returned an empty response')
                if json_output:
                    try:
                        return json.loads(response.text)
                    except json.JSONDecodeError as exc:
                        raise AIServiceError('Gemini returned invalid JSON') from exc
                return response.text
            except errors.APIError as exc:
                if exc.code != 503 or attempt == 2:
                    raise AIServiceError(f'Gemini API error {exc.code}: {exc.message}') from exc
                time.sleep(2 ** attempt)
    finally:
        if owned:
            client.close()

def payload(**kwargs):
    return json.dumps(kwargs, ensure_ascii=False)
