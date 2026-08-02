from typing import Dict, Any
from app.graphs.state import AgentState
from app.utils.logger import app_logger

WEB_APP_KEYWORDS = [
    "linkedin", "youtube", "github", "chatgpt", "reddit",
    "twitter", "facebook", "instagram", "gmail", "google",
    "stackoverflow", "wikipedia"
]

SYSTEM_POWER_KEYWORDS = [
    "sleep", "suspend", "standby", "lock", "lock screen", "lock pc",
    "lock computer", "restart", "reboot", "shutdown", "turn off",
    "power off", "cpu", "ram", "battery", "screenshot", "system", "stats", "metrics"
]

MEDIA_KEYWORDS = [
    "volume", "sound", "audio", "mute", "unmute", "louder", "quieter",
    "play", "pause", "music", "song", "track", "next song", "previous song",
    "skip track", "media", "turn up", "turn down", "increase volume", "decrease volume"
]

WEATHER_KEYWORDS = [
    "weather", "temperature", "forecast", "climate", "humidity", "rain"
]

async def supervisor_agent_node(state: AgentState) -> Dict[str, Any]:
    """Master Supervisor Agent: Dynamically classifies intent across OS automation, browser, media, volume, system power, and desktop control."""
    user_query = state.get("user_query", "") or (state.get("messages", [{}])[-1].get("content", "") if state.get("messages") else "")
    query_lower = user_query.lower()
    
    app_logger.info(f"[SupervisorAgent] Classifying intent for query: '{user_query[:50]}'")

    # Priority 1: System Power & Metrics (sleep, lock, restart, shutdown, cpu, ram)
    if any(k in query_lower for k in SYSTEM_POWER_KEYWORDS):
        next_agent = "system"
        intent = "system_power_and_metrics"

    # Priority 2: Media & Audio Volume Control (increase volume, mute, pause, play, etc.)
    elif any(k in query_lower for k in MEDIA_KEYWORDS):
        next_agent = "media"
        intent = "media_control"

    # Priority 3: Weather & Live Temperature
    elif any(k in query_lower for k in WEATHER_KEYWORDS):
        next_agent = "tool_agent"
        intent = "weather_info"

    # Priority 3: Explicit Desktop Application Launching (open, launch, start local apps like LinkedIn, Spotify, VS Code, etc.)
    elif any(k in query_lower for k in ["open", "launch", "start app", "run app", "switch to", "start", "run"]) and not any(k in query_lower for k in ["search", "browse", "http", "www", "google for"]):
        next_agent = "desktop"
        intent = "desktop_automation"

    # Priority 3: Web Apps & Browser (LinkedIn, YouTube, GitHub, ChatGPT, etc.)
    elif any(k in query_lower for k in WEB_APP_KEYWORDS) or "search web" in query_lower or "browse" in query_lower:
        next_agent = "browser"
        intent = "web_and_social_browser"

    # Priority 6: Communication & Messaging
    elif any(k in query_lower for k in ["email", "whatsapp", "slack", "message", "telegram", "send message", "draft"]):
        next_agent = "communication"
        intent = "communication_draft"

    # Priority 7: Tools & Calculations
    elif any(k in query_lower for k in ["calculate", "math", "+", "-", "*", "/", "sqrt", "uuid", "date", "time"]):
        next_agent = "tool_agent"
        intent = "tool_execution"

    # Priority 8: Software & Code
    elif any(k in query_lower for k in ["code", "python", "typescript", "function", "script", "program"]):
        next_agent = "coding"
        intent = "software_development"

    # Priority 9: File Operations
    elif any(k in query_lower for k in ["file", "pdf", "csv", "read", "document", "parse"]):
        next_agent = "file"
        intent = "document_processing"

    # Priority 10: Multi-step Planning
    elif any(k in query_lower for k in ["plan", "strategy", "architecture", "steps"]):
        next_agent = "planner"
        intent = "multi_step_planning"
    else:
        next_agent = "formatter"
        intent = "direct_conversation"

    reasoning = state.get("intermediate_reasoning", []) + [f"Supervisor classified intent: '{intent}' -> Next: '{next_agent}'"]
    
    return {
        "current_agent": "supervisor",
        "next_agent": next_agent,
        "intent": intent,
        "user_query": user_query,
        "intermediate_reasoning": reasoning,
        "execution_status": "routing_complete"
    }
