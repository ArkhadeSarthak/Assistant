import os
import json
import asyncio
from datetime import datetime
from typing import AsyncGenerator, List, Optional
from app.graphs.workflow import aura_agent_graph
from app.graphs.state import AgentState
from app.services.memory_service import memory_service
from app.services.vision_service import vision_service
from app.config.settings import settings
from app.utils.logger import app_logger

async def resolve_image_vision_context(message: str, files: Optional[List[str]] = None) -> tuple[str, list]:
    """Helper to check attached/uploaded image files and generate OpenRouter Vision analysis."""
    vision_results = []
    augmented_message = message

    storage_dir = settings.STORAGE_DIR
    if not os.path.exists(storage_dir):
        return augmented_message, vision_results

    saved_files = os.listdir(storage_dir)
    target_image_paths = []

    # 1. Match specified files if provided
    if files:
        for f_name in files:
            for s_file in saved_files:
                if s_file.lower().endswith(f_name.lower()) or f_name.lower() in s_file.lower():
                    if vision_service.is_image_file(s_file):
                        target_image_paths.append((s_file, os.path.join(storage_dir, s_file)))
                        break

    # 2. Fallback to latest uploaded image if query asks about an image/background/visual
    if not target_image_paths:
        query_lower = message.lower()
        if any(k in query_lower for k in ["image", "photo", "picture", "background", "this", "that", "look"]):
            image_files = [f for f in sorted(saved_files, key=lambda x: os.path.getmtime(os.path.join(storage_dir, x)), reverse=True) if vision_service.is_image_file(f)]
            if image_files:
                target_image_paths.append((image_files[0], os.path.join(storage_dir, image_files[0])))

    # Run OpenRouter Vision API for target images
    for fname, fpath in target_image_paths:
        try:
            app_logger.info(f"[Executor] Analyzing image '{fname}' with OpenRouter Vision API...")
            analysis = await vision_service.analyze_image_async(fpath, prompt=message)
            vision_results.append({"file": fname, "analysis": analysis})
            augmented_message = f"[Attached Image Context ({fname}): OpenRouter Vision Analysis Output:\n{analysis}]\n\nUser Question: {message}"
        except Exception as e:
            app_logger.error(f"[Executor] Error running vision analysis on {fname}: {e}")

    return augmented_message, vision_results

async def run_aura_agent(session_id: str, message: str, user_id: str = None, files: Optional[List[str]] = None) -> dict:
    if any(k in message.lower() for k in ["execute last query", "repeat last query", "run last query", "do last query"]):
        history = await memory_service.get_session_history(session_id)
        user_msgs = [m["content"] for m in history if m["role"] == "user" and m["content"] not in message]
        if user_msgs:
            message = user_msgs[-1]
            app_logger.info(f"Resolved 'execute last query' from Redis to previous prompt: '{message}'")

    augmented_msg, vision_results = await resolve_image_vision_context(message, files)

    # Persist user message to Redis memory
    await memory_service.add_message(session_id, "user", message)

    initial_state: AgentState = {
        "session_id": session_id,
        "user_id": user_id,
        "messages": [{"role": "user", "content": augmented_msg}],
        "conversation_history": [],
        "user_query": augmented_msg,
        "intent": "",
        "task": augmented_msg,
        "plan": [],
        "retrieved_documents": [],
        "memory": {},
        "browser_results": [],
        "file_results": vision_results,
        "tool_results": [],
        "intermediate_reasoning": [f"Vision analysis completed for {len(vision_results)} images"] if vision_results else [],
        "current_agent": "START",
        "next_agent": "",
        "retry_count": 0,
        "execution_status": "starting",
        "validation_result": {},
        "formatted_response": "",
        "metadata": {},
        "timestamps": {"start": datetime.utcnow().isoformat()}
    }

    config = {"configurable": {"thread_id": session_id}}
    final_state = await aura_agent_graph.ainvoke(initial_state, config=config)

    final_text = final_state.get("formatted_response") or final_state.get("final_response") or ""
    if final_text:
        await memory_service.add_message(session_id, "assistant", final_text)

    return final_state

async def stream_aura_agent_events(session_id: str, message: str, user_id: str = None, files: Optional[List[str]] = None) -> AsyncGenerator[str, None]:
    """Generates Server-Sent Events (SSE) emitting thinking, agent switches, tool calls, and final tokens."""
    if any(k in message.lower() for k in ["execute last query", "repeat last query", "run last query", "do last query"]):
        history = await memory_service.get_session_history(session_id)
        user_msgs = [m["content"] for m in history if m["role"] == "user" and m["content"] not in message]
        if user_msgs:
            message = user_msgs[-1]
            app_logger.info(f"Resolved 'execute last query' from Redis to previous prompt: '{message}'")

    augmented_msg, vision_results = await resolve_image_vision_context(message, files)

    # Persist user message to Redis memory
    await memory_service.add_message(session_id, "user", message)

    initial_state: AgentState = {
        "session_id": session_id,
        "user_id": user_id,
        "messages": [{"role": "user", "content": augmented_msg}],
        "conversation_history": [],
        "user_query": augmented_msg,
        "intent": "",
        "task": augmented_msg,
        "plan": [],
        "retrieved_documents": [],
        "memory": {},
        "browser_results": [],
        "file_results": vision_results,
        "tool_results": [],
        "intermediate_reasoning": [f"Vision analysis completed for {len(vision_results)} images"] if vision_results else [],
        "current_agent": "START",
        "next_agent": "",
        "retry_count": 0,
        "execution_status": "starting",
        "validation_result": {},
        "formatted_response": "",
        "metadata": {},
        "timestamps": {"start": datetime.utcnow().isoformat()}
    }

    yield f"data: {json.dumps({'event_type': 'thinking', 'data': f'Analyzing image & executing prompt: {message[:40]}...'})}\n\n"
    await asyncio.sleep(0.2)

    config = {"configurable": {"thread_id": session_id}}
    final_state = await aura_agent_graph.ainvoke(initial_state, config=config)

    # Emit tool execution events
    for tool in final_state.get("tool_results", []):
        yield f"data: {json.dumps({'event_type': 'tool_start', 'data': {'name': tool['name'], 'status': 'running'}})}\n\n"
        await asyncio.sleep(0.15)
        yield f"data: {json.dumps({'event_type': 'tool_end', 'data': tool})}\n\n"
        await asyncio.sleep(0.15)

    # Stream final response tokens
    final_text = final_state.get("formatted_response") or final_state.get("final_response") or ""
    if final_text:
        await memory_service.add_message(session_id, "assistant", final_text)

    words = final_text.split(" ")
    for word in words:
        yield f"data: {json.dumps({'event_type': 'token', 'data': word + ' '})}\n\n"
        await asyncio.sleep(0.03)

    yield f"data: {json.dumps({'event_type': 'done', 'data': {'session_id': session_id, 'reasoning': final_state.get('intermediate_reasoning', [])}})}\n\n"
