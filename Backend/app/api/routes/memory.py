from fastapi import APIRouter
from pydantic import BaseModel
from app.services.memory_service import memory_service

router = APIRouter(prefix="/memory", tags=["Memory"])

class MemoryStoreRequest(BaseModel):
    session_id: str
    key: str
    value: str

class MemorySearchRequest(BaseModel):
    session_id: str
    query: str

class MemoryClearRequest(BaseModel):
    session_id: str

@router.post("/store")
async def store_memory(request: MemoryStoreRequest):
    await memory_service.store_memory_item(request.session_id, request.key, request.value)
    return {"status": "success", "session_id": request.session_id, "stored_key": request.key}

@router.post("/search")
async def search_memory(request: MemorySearchRequest):
    items = await memory_service.get_memory_items(request.session_id)
    return {"session_id": request.session_id, "query": request.query, "results": items}

@router.post("/clear")
async def clear_memory(request: MemoryClearRequest):
    await memory_service.clear_session_data(request.session_id)
    return {"status": "success", "session_id": request.session_id}
