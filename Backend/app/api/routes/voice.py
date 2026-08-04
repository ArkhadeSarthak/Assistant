from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.tts_service import tts_service
from app.services.stt_service import stt_service
from app.utils.logger import app_logger

router = APIRouter(prefix="", tags=["Voice"])

class TTSRequest(BaseModel):
    text: str
    voice_id: str = "Aarav"

@router.post("/tts")
@router.post("/voice/tts")
async def tts_endpoint(req: TTSRequest):
    """Streaming Text-to-Speech endpoint powered by Inworld AI."""
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text parameter cannot be empty.")

    try:
        return StreamingResponse(
            tts_service.stream_speech(req.text, voice_id=req.voice_id),
            media_type="audio/mpeg"
        )
    except Exception as e:
        app_logger.error(f"TTS synthesis error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {str(e)}")

@router.post("/stt")
@router.post("/voice/stt")
async def stt_endpoint(audio_file: UploadFile = File(...)):
    """Speech-to-Text endpoint powered by Deepgram Nova-3."""
    if not audio_file:
        raise HTTPException(status_code=400, detail="Audio file required")
    try:
        content = await audio_file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Audio file content is empty")
        transcript = await stt_service.transcribe_audio(content)
        return {
            "status": "success",
            "transcription": transcript,
            "audio_size": len(content)
        }
    except Exception as e:
        app_logger.error(f"STT endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Speech-to-text failed: {str(e)}")

@router.post("/voice")
async def voice_endpoint(
    audio_file: UploadFile = File(None),
    text: str = Form(None)
):
    """Voice mode endpoint supporting Speech-to-Text and Text-to-Speech synthesis."""
    if audio_file:
        try:
            content = await audio_file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Audio file content is empty")
            transcript = await stt_service.transcribe_audio(content)
            return {
                "status": "success",
                "transcription": transcript,
                "audio_size": len(content)
            }
        except Exception as e:
            app_logger.error(f"Voice endpoint STT error: {e}")
            raise HTTPException(status_code=500, detail=f"STT processing failed: {str(e)}")
    elif text:
        return {
            "status": "success",
            "audio_url": "/tts",
            "text": text
        }
    return {"status": "error", "message": "Provide either audio_file or text"}

