"""Optional transcription of local audio files."""
import mimetypes
from pathlib import Path
from google.genai import types
from .common import generate
import sounddevice as sd
import numpy as np
import io
import wave
from google.genai import types


def listen_microphone(duration=6, *, client=None):
    sample_rate = 16000

    print("Microphone activated. Speak now...")

    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(audio.tobytes())

    prompt = [
        types.Part.from_bytes(
            data=buffer.getvalue(),
            mime_type="audio/wav"
        ),
        "Transcribe the spoken words verbatim. "
        "Return only the transcript."
    ]

    text = generate(
        prompt,
        instruction="Transcribe accurately in the original language.",
        client=client
    )

    if not isinstance(text, str):
        raise ValueError("Invalid transcription response")

    return text.strip()

def transcribe_audio(audio_path, *, client=None):
    path = Path(audio_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.stat().st_size > 10 * 1024 * 1024:
        raise ValueError('Audio exceeds demo 10 MB limit')
    mime, _ = mimetypes.guess_type(path.name)
    supported = {'.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.flac': 'audio/flac', '.ogg': 'audio/ogg'}
    mime = supported.get(path.suffix.lower(), mime)
    if path.suffix.lower() not in supported:
        raise ValueError('Use WAV, MP3, FLAC or OGG')
    prompt = [types.Part.from_bytes(data=path.read_bytes(), mime_type=mime),
              'Transcribe the spoken words verbatim. Return only the transcript, in the original language.']
    return {'type': 'transcript', 'text': generate(prompt, instruction='Transcribe audio accurately; do not add imagined words.', client=client)}
