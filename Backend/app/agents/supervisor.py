from typing import Dict, Any
from app.graphs.state import AgentState
from app.utils.logger import app_logger

WEB_APP_KEYWORDS = [
    "linkedin", "youtube", "github", "chatgpt", "reddit",
    "twitter", "facebook", "instagram", "gmail", "google",
    "stackoverflow", "wikipedia"
]

SYSTEM_POWER_KEYWORDS = [
    "sleep", "suspend", "standby", "lock", "lock screen", "lock pc", "lock computer", 
    "lock workstation", "lock desktop", "lock system", "restart", "reboot", 
    "shutdown", "turn off", "power off"
]


MEDIA_KEYWORDS = [
    "volume", "sound", "audio", "mute", "unmute", "louder", "quieter",
    "play music", "pause music", "next song", "previous song",
    "skip track", "turn up volume", "turn down volume", "increase volume", "decrease volume"
]

WEATHER_KEYWORDS = [
    "weather in", "temperature in", "forecast for", "current weather", "humidity in", "rain in"
]

NEWS_KEYWORDS = [
    "news", "headline", "headlines", "latest news", "breaking news",
    "gnews", "news about", "news on", "today's news", "current news", "articles on"
]

async def supervisor_agent_node(state: AgentState) -> Dict[str, Any]:
    """Master Supervisor Agent: Dynamically classifies intent across OS automation, browser, media, volume, system power, desktop control, and direct conversation."""
    user_query = state.get("user_query", "") or (state.get("messages", [{}])[-1].get("content", "") if state.get("messages") else "")
    query_lower = user_query.lower().strip()
    
    app_logger.info(f"[SupervisorAgent] Classifying intent for query: '{user_query[:50]}'")

    # Check if query is an informational/explanatory question
    is_informational = any(query_lower.startswith(p) for p in [
        "what is", "what are", "what does", "why is", "why do", "explain", 
        "tell me about", "who is", "definition of", "meaning of", "how does", "describe"
    ]) or ("?" in query_lower and not any(act in query_lower for act in ["write", "create", "generate", "open", "launch", "mute", "turn up", "shutdown", "send", "calculate"]))

    # Priority 1: Informational/general conversation queries route to direct conversation (unless requesting live tools like news/search/weather)
    if is_informational and not any(k in query_lower for k in ["search web", "browse", "latest news", "open", "launch", "news", "headline"]):
        next_agent = "formatter"
        intent = "direct_conversation"

    # Priority 2: System Power & Metrics
    elif any(k in query_lower for k in SYSTEM_POWER_KEYWORDS):
        next_agent = "system"
        intent = "system_power_and_metrics"

    # Priority 3: Media & Audio Volume Control
    elif any(k in query_lower for k in MEDIA_KEYWORDS):
        next_agent = "media"
        intent = "media_control"

    # Priority 4: Weather & Live Temperature
    elif any(k in query_lower for k in WEATHER_KEYWORDS):
        next_agent = "tool_agent"
        intent = "weather_info"

    # Priority 4b: Live News & Headlines
    elif any(k in query_lower for k in NEWS_KEYWORDS):
        next_agent = "tool_agent"
        intent = "news_info"

    # Priority 5: Desktop Application Launching (Local App first, Web fallback)
    elif any(k in query_lower for k in ["open ", "launch ", "start ", "run ", "switch to "]) and not any(k in query_lower for k in ["search web", "browse web", "http://", "https://"]):
        next_agent = "desktop"
        intent = "desktop_automation"

    # Priority 6: Web Search & Browser Navigation
    elif any(k in query_lower for k in WEB_APP_KEYWORDS) or "search web" in query_lower or "browse" in query_lower:
        next_agent = "browser"
        intent = "web_and_social_browser"


    # Priority 7: Communication & Messaging
    elif any(k in query_lower for k in ["send email", "send whatsapp", "send message", "draft email"]):
        next_agent = "communication"
        intent = "communication_draft"

    # Priority 8: Tools & Calculations
    elif any(k in query_lower for k in ["calculate", "math ", "sqrt(", "uuid generator"]):
        next_agent = "tool_agent"
        intent = "tool_execution"

    # Priority 9: Software & Code Generation
    elif any(k in query_lower for k in ["write code", "generate code", "create script", "write script", "write function", "refactor code", "fix code", "debug code"]):
        next_agent = "coding"
        intent = "software_development"

    # Priority 10: File Operations & Vision Image Analysis
    elif any(k in query_lower for k in [
        "read file", "parse pdf", "read csv", "parse document",
        "image", "photo", "picture", "screenshot", "extract text",
        "describe image", "what is in this image", "what's in this image",
        "read image", "see image", "analyze image"
    ]):
        next_agent = "file"
        intent = "document_and_vision_processing"

    # Priority 11: Multi-step Planning
    elif any(k in query_lower for k in ["create plan", "multi-step strategy"]):
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
