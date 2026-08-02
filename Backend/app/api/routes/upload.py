import os
import uuid
from fastapi import APIRouter, UploadFile, File
from app.schemas.domain import FileUploadResponse
from app.config.settings import settings

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
    if file.filename.endswith((".txt", ".md", ".csv", ".json")):
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
