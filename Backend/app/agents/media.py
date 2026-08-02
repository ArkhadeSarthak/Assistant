from typing import Dict, Any
from app.graphs.state import AgentState
from app.tools.media_tools import media_control_tool
from app.utils.logger import app_logger

async def media_agent_node(state: AgentState) -> Dict[str, Any]:
    """Media Agent: Controls music playback and system audio volume."""
    query = state.get("user_query", "").lower()
    app_logger.info(f"[MediaAgent] Controlling media session for query: '{query[:50]}'")

    if any(k in query for k in ["volume", "increase", "decrease", "louder", "quieter", "sound", "audio", "turn up", "turn down", "up", "down"]):
        res = media_control_tool.invoke({"action": "volume", "query": query})
    elif "pause" in query or "stop" in query:
        res = media_control_tool.invoke({"action": "pause", "query": query})
    elif "next" in query or "skip" in query:
        res = media_control_tool.invoke({"action": "next", "query": query})
    elif "previous" in query or "prev" in query or "back" in query:
        res = media_control_tool.invoke({"action": "previous", "query": query})
    elif "mute" in query or "unmute" in query:
        res = media_control_tool.invoke({"action": "mute", "query": query})
    else:
        res = media_control_tool.invoke({"action": "play", "query": query})

    reasoning = state.get("intermediate_reasoning", []) + [f"Media Agent processed volume/media command"]

    return {
        "current_agent": "media",
        "next_agent": "validator",
        "formatted_response": f"🔊 **Media & Volume Control**: {res}",
        "intermediate_reasoning": reasoning
    }
