import json
import asyncio
from datetime import datetime
from typing import AsyncGenerator
from app.graphs.workflow import aura_agent_graph
from app.graphs.state import AgentState
from app.services.memory_service import memory_service
from app.utils.logger import app_logger

async def run_aura_agent(session_id: str, message: str, user_id: str = None) -> dict:
    # Handle "execute last query" from Redis memory history
    if any(k in message.lower() for k in ["execute last query", "repeat last query", "run last query", "do last query"]):
        history = await memory_service.get_session_history(session_id)
        user_msgs = [m["content"] for m in history if m["role"] == "user" and m["content"] not in message]
        if user_msgs:
            message = user_msgs[-1]
            app_logger.info(f"Resolved 'execute last query' from Redis to previous prompt: '{message}'")

    # Persist user message to Redis memory
    await memory_service.add_message(session_id, "user", message)

    initial_state: AgentState = {
        "session_id": session_id,
        "user_id": user_id,
        "messages": [{"role": "user", "content": message}],
        "conversation_history": [],
        "user_query": message,
        "intent": "",
        "task": message,
        "plan": [],
        "retrieved_documents": [],
        "memory": {},
        "browser_results": [],
        "file_results": [],
        "tool_results": [],
        "intermediate_reasoning": [],
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

async def stream_aura_agent_events(session_id: str, message: str, user_id: str = None) -> AsyncGenerator[str, None]:
    """Generates Server-Sent Events (SSE) emitting thinking, agent switches, tool calls, and final tokens."""
    if any(k in message.lower() for k in ["execute last query", "repeat last query", "run last query", "do last query"]):
        history = await memory_service.get_session_history(session_id)
        user_msgs = [m["content"] for m in history if m["role"] == "user" and m["content"] not in message]
        if user_msgs:
            message = user_msgs[-1]
            app_logger.info(f"Resolved 'execute last query' from Redis to previous prompt: '{message}'")

    # Persist user message to Redis memory
    await memory_service.add_message(session_id, "user", message)

    initial_state: AgentState = {
        "session_id": session_id,
        "user_id": user_id,
        "messages": [{"role": "user", "content": message}],
        "conversation_history": [],
        "user_query": message,
        "intent": "",
        "task": message,
        "plan": [],
        "retrieved_documents": [],
        "memory": {},
        "browser_results": [],
        "file_results": [],
        "tool_results": [],
        "intermediate_reasoning": [],
        "current_agent": "START",
        "next_agent": "",
        "retry_count": 0,
        "execution_status": "starting",
        "validation_result": {},
        "formatted_response": "",
        "metadata": {},
        "timestamps": {"start": datetime.utcnow().isoformat()}
    }

    yield f"data: {json.dumps({'event_type': 'thinking', 'data': f'Executing prompt: {message[:40]}...'})}\n\n"
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
