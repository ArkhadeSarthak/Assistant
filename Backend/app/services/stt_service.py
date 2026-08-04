import asyncio
import os
from typing import Union
from deepgram import DeepgramClient
from app.config.settings import settings
from app.utils.logger import app_logger

class STTService:
    """Speech-to-Text service powered by Deepgram SDK (Nova-3)."""

    def __init__(self):
        self._client = None

    @property
    def client(self) -> DeepgramClient:
        if self._client is None:
            api_key = settings.DEEPGRAM_API_KEY or os.getenv("DEEPGRAM_API_KEY")
            if not api_key:
                raise ValueError("DEEPGRAM_API_KEY is not configured in .env file.")
            try:
                self._client = DeepgramClient(api_key=api_key)
            except Exception:
                self._client = DeepgramClient(api_key)
        return self._client


    def speech_to_text_sync(self, audio_data: Union[bytes, str]) -> str:
        """Synchronous speech to text using Deepgram API with Nova-3 model.
        
        Args:
            audio_data: Raw audio bytes or file path string.
        """
        if isinstance(audio_data, str):
            with open(audio_data, "rb") as f:
                buffer_data = f.read()
        else:
            buffer_data = audio_data

        client = self.client

        # Deepgram SDK v7+ syntax
        if hasattr(client, "listen") and hasattr(client.listen, "v1") and hasattr(client.listen.v1, "media"):
            response = client.listen.v1.media.transcribe_file(
                request=buffer_data,
                model="nova-3",
                smart_format=True,
                punctuate=True,
                diarize=False
            )
        # Deepgram SDK v3 legacy fallback
        elif hasattr(client, "listen") and hasattr(client.listen, "rest"):
            from deepgram import PrerecordedOptions
            payload = {"buffer": buffer_data}
            options = PrerecordedOptions(
                model="nova-3",
                smart_format=True,
                punctuate=True,
                diarize=False,
            )
            response = client.listen.rest.v("1").transcribe_file(payload, options)
        else:
            raise RuntimeError("Unsupported Deepgram SDK version structure")

        # Extract transcript string safely
        if hasattr(response, "results") and response.results and response.results.channels:
            channel = response.results.channels[0]
            if channel.alternatives and len(channel.alternatives) > 0:
                return channel.alternatives[0].transcript or ""
        
        return ""

    async def transcribe_audio(self, audio_data: Union[bytes, str]) -> str:
        """Asynchronous wrapper for speech to text transcription."""
        try:
            return await asyncio.to_thread(self.speech_to_text_sync, audio_data)
        except Exception as e:
            app_logger.error(f"Deepgram STT transcription error: {e}")
            raise e

stt_service = STTService()
