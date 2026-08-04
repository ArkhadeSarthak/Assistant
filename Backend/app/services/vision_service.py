import base64
import os
import httpx
import requests
from typing import Union, Optional
from app.config.settings import settings
from app.utils.logger import app_logger

DEFAULT_PROMPT = """
Read everything in this image.
If it contains text, extract all text exactly.
If it contains objects, describe them.
Return plain text only.
"""

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".svg")

class VisionService:
    """Vision processing service using OpenRouter API."""

    def __init__(self):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    @property
    def api_key(self) -> str:
        key = settings.OPENROUTER_API_KEY or os.getenv("OPENROUTER_API_KEY")
        if not key:
            raise ValueError("OPENROUTER_API_KEY is not configured in .env file.")
        return key


    @property
    def model(self) -> str:
        return getattr(settings, "OPENROUTER_VISION_MODEL", "openrouter/free") or "openrouter/free"

    def is_image_file(self, filename: str) -> bool:
        """Check if filename has an image extension."""
        return filename.lower().endswith(IMAGE_EXTENSIONS)

    def encode_image(self, image_input: Union[bytes, str]) -> tuple[str, str]:
        """Encodes image bytes or file path to base64 string and mime type."""
        mime_type = "image/jpeg"
        if isinstance(image_input, str):
            lower_path = image_input.lower()
            if lower_path.endswith(".png"):
                mime_type = "image/png"
            elif lower_path.endswith(".webp"):
                mime_type = "image/webp"
            elif lower_path.endswith(".gif"):
                mime_type = "image/gif"
            elif lower_path.endswith(".bmp"):
                mime_type = "image/bmp"

            with open(image_input, "rb") as f:
                image_bytes = f.read()
        else:
            image_bytes = image_input

        base64_str = base64.b64encode(image_bytes).decode("utf-8")
        return base64_str, mime_type

    def analyze_image_sync(
        self,
        image_input: Union[bytes, str],
        prompt: Optional[str] = None,
        custom_mime: Optional[str] = None
    ) -> str:
        """Synchronous OpenRouter Vision analysis."""
        base64_img, default_mime = self.encode_image(image_input)
        mime_type = custom_mime or default_mime
        user_prompt = prompt.strip() if (prompt and prompt.strip()) else DEFAULT_PROMPT

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_img}"
                            }
                        }
                    ]
                }
            ]
        }

        app_logger.info(f"[VisionService] Sending OpenRouter Vision request (model: {self.model})")
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        result = response.json()
        content = result["choices"][0]["message"]["content"]
        return content

    async def analyze_image_async(
        self,
        image_input: Union[bytes, str],
        prompt: Optional[str] = None,
        custom_mime: Optional[str] = None
    ) -> str:
        """Asynchronous OpenRouter Vision analysis."""
        base64_img, default_mime = self.encode_image(image_input)
        mime_type = custom_mime or default_mime
        user_prompt = prompt.strip() if (prompt and prompt.strip()) else DEFAULT_PROMPT

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_img}"
                            }
                        }
                    ]
                }
            ]
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

vision_service = VisionService()
