import time
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.domain import ChatRequest, ChatResponse, MessageSchema
from app.graphs.executor import run_aura_agent, stream_aura_agent_events
from app.security.prompt_injection import detect_prompt_injection

router = APIRouter(prefix="", tags=["Chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    start_time = time.time()
    session_id = request.session_id or f"sess-{uuid.uuid4().hex[:8]}"

    # Security check
    is_inj, conf, reason = detect_prompt_injection(request.message)
    if is_inj:
        raise HTTPException(status_code=400, detail=f"Prompt injection detected: {reason}")

    final_state = await run_aura_agent(session_id, request.message)
    elapsed_ms = (time.time() - start_time) * 1000

    return ChatResponse(
        session_id=session_id,
        message=MessageSchema(
            role="assistant",
            content=final_state.get("final_response", ""),
            tools_used=final_state.get("tool_results", [])
        ),
        execution_time_ms=elapsed_ms
    )

@router.post("/stream")
async def stream_endpoint(request: ChatRequest):
    session_id = request.session_id or f"sess-{uuid.uuid4().hex[:8]}"

    is_inj, conf, reason = detect_prompt_injection(request.message)
    if is_inj:
        raise HTTPException(status_code=400, detail=f"Prompt injection detected: {reason}")

    return StreamingResponse(
        stream_aura_agent_events(session_id, request.message),
        media_type="text/event-stream"
    )
