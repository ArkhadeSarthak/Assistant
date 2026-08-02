from typing import Dict, Any
from app.graphs.state import AgentState
from app.tools.communication_tools import draft_message_tool
from app.utils.logger import app_logger

async def communication_agent_node(state: AgentState) -> Dict[str, Any]:
    """Communication Agent: Drafts emails and messages with strict confirmation enforcement."""
    query = state.get("user_query", "")
    app_logger.info(f"[CommunicationAgent] Drafting communication for: '{query[:50]}'")

    # Extract recipient and platform
    platform = "email"
    if "whatsapp" in query.lower():
        platform = "whatsapp"
    elif "slack" in query.lower():
        platform = "slack"
    elif "telegram" in query.lower():
        platform = "telegram"

    res = draft_message_tool.invoke({
        "recipient": "Contact",
        "message": query,
        "platform": platform
    })

    reasoning = state.get("intermediate_reasoning", []) + ["Communication Agent prepared draft requiring user confirmation"]

    return {
        "current_agent": "communication",
        "next_agent": "validator",
        "requires_confirmation": True,
        "formatted_response": res,
        "intermediate_reasoning": reasoning
    }
