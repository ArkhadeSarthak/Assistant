import os
import uuid
from fastapi import APIRouter, UploadFile, File
from app.schemas.domain import FileUploadResponse
from app.config.settings import settings
from app.services.vision_service import vision_service
from app.utils.logger import app_logger

router = APIRouter(prefix="", tags=["Files"])

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file_endpoint(file: UploadFile = File(...)):
    file_id = f"file-{uuid.uuid4().hex[:8]}"
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)
    save_path = os.path.join(settings.STORAGE_DIR, f"{file_id}_{file.filename}")

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    snippet = None
    if vision_service.is_image_file(file.filename):
        try:
            snippet = await vision_service.analyze_image_async(content, custom_mime=file.content_type)
            app_logger.info(f"[UploadRoute] Successfully extracted vision analysis for image: {file.filename}")
        except Exception as e:
            app_logger.error(f"[UploadRoute] Vision analysis error for {file.filename}: {e}")
            snippet = f"Image file uploaded ({file.filename})."
    elif file.filename.lower().endswith((".txt", ".md", ".csv", ".json")):
        try:
            snippet = content.decode("utf-8")[:300]
        except Exception:
            snippet = "Binary content extracted."

    return FileUploadResponse(
        file_id=file_id,
        filename=file.filename,
        file_type=file.content_type or "unknown",
        file_size=len(content),
        extracted_text_snippet=snippet
    )

