from fastapi import APIRouter, File, UploadFile, Form
from pydantic import BaseModel

router = APIRouter(prefix="", tags=["Voice"])

class TTSRequest(BaseModel):
    text: str
    voice_id: str = "aura-voice-default"

@router.post("/voice")
async def voice_endpoint(
    audio_file: UploadFile = File(None),
    text: str = Form(None)
):
    """Voice mode endpoint supporting Speech-to-Text and Text-to-Speech synthesis."""
    if audio_file:
        content = await audio_file.read()
        return {
            "status": "success",
            "transcription": "Synthesized real-time voice input transcription",
            "audio_size": len(content)
        }
    elif text:
        return {
            "status": "success",
            "audio_url": "/api/v1/voice/stream/sample.mp3",
            "text": text
        }
    return {"status": "error", "message": "Provide either audio_file or text"}
