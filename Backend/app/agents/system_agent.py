from typing import Dict, Any
from app.graphs.state import AgentState
from app.tools.system_tools import (
    get_system_stats_tool,
    take_screenshot_tool,
    lock_computer_tool,
    sleep_computer_tool,
    shutdown_computer_tool,
    restart_computer_tool,
)
from app.utils.logger import app_logger

async def system_agent_node(state: AgentState) -> Dict[str, Any]:
    """System Agent: Controls hardware metrics, screenshots, volume, computer sleep, lock, restart, and shutdown."""
    query = state.get("user_query", "").lower()
    app_logger.info(f"[SystemAgent] Executing system power/metric operation for: '{query[:50]}'")

    output_text = ""
    requires_conf = False

    if "sleep" in query or "suspend" in query or "standby" in query:
        output_text = sleep_computer_tool.invoke({})
    elif "restart" in query or "reboot" in query:
        output_text = restart_computer_tool.invoke({})
    elif "shutdown" in query or "turn off" in query or "power off" in query:
        output_text = shutdown_computer_tool.invoke({})
    elif "lock" in query or "lock screen" in query or "lock pc" in query:
        output_text = lock_computer_tool.invoke({})
    elif "screenshot" in query or "capture screen" in query or "snapshot" in query or "take screen" in query:
        output_text = take_screenshot_tool.invoke({"filename": "aura_screenshot.png"})
    elif "cpu" in query or "ram" in query or "battery" in query or "stats" in query or "metrics" in query or "health" in query:
        output_text = get_system_stats_tool.invoke({})
    else:
        output_text = get_system_stats_tool.invoke({})

    reasoning = state.get("intermediate_reasoning", []) + ["System Agent executed OS power/metric operation"]

    return {
        "current_agent": "system",
        "next_agent": "validator",
        "requires_confirmation": requires_conf,
        "formatted_response": output_text,
        "intermediate_reasoning": reasoning
    }
