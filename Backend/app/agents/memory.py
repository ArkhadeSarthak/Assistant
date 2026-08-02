from typing import Dict, Any
from app.graphs.state import AgentState
from app.services.memory_service import memory_service
from app.utils.logger import app_logger

async def memory_agent_node(state: AgentState) -> Dict[str, Any]:
    """Memory Agent: Loads short-term and long-term memory."""
    session_id = state.get("session_id", "default-session")
    app_logger.info(f"[MemoryAgent] Loading memory for session: {session_id}")

    mem_items = await memory_service.get_memory_items(session_id)
    history = await memory_service.get_session_history(session_id)

    reasoning = state.get("intermediate_reasoning", []) + ["Memory Agent loaded session context"]

    return {
        "current_agent": "memory",
        "next_agent": "supervisor",
        "memory": mem_items,
        "conversation_history": history,
        "intermediate_reasoning": reasoning
    }
