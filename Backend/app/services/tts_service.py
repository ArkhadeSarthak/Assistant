import requests
import json
import base64
from typing import Generator
from app.config.settings import settings
from app.utils.logger import app_logger

class TTSService:
    def __init__(self):
        self.url = "https://api.inworld.ai/tts/v1/voice:stream"

    def stream_speech(self, text: str, voice_id: str = "Sarah") -> Generator[bytes, None, None]:
        api_key = settings.INWORLD_TTS_KEY
        if not api_key:
            raise ValueError("INWORLD_TTS_KEY is not configured in .env file.")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "voice_id": voice_id,
            "audio_config": {
                "audio_encoding": "MP3",
                "speaking_rate": 1
            },
            "delivery_mode": "BALANCED",
            "model_id": "inworld-tts-2",
            "language": "AUTO"
        }

        app_logger.info(f"Streaming Inworld TTS audio for text (length {len(text)})")
        response = requests.post(self.url, json=payload, headers=headers, stream=True, timeout=30)
        response.raise_for_status()

        for line in response.iter_lines():
            if not line:
                continue
            try:
                obj = json.loads(line)
                result = obj.get("result", {})
                audio_content = result.get("audioContent")
                if audio_content:
                    yield base64.b64decode(audio_content)
            except Exception as e:
                app_logger.warning(f"Error parsing TTS stream line: {e}")
                continue

    def generate_speech(self, text: str, voice_id: str = "Aarav") -> bytes:
        audio_data = bytearray()
        for chunk in self.stream_speech(text, voice_id):
            audio_data.extend(chunk)

        if not audio_data:
            raise ValueError("No audio content returned from Inworld TTS service")

        return bytes(audio_data)

tts_service = TTSService()
