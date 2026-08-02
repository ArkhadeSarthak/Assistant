from typing import Dict, Any
from app.graphs.state import AgentState
from app.tools.desktop_tools import launch_app_tool, list_running_apps_tool
from app.utils.logger import app_logger

async def desktop_agent_node(state: AgentState) -> Dict[str, Any]:
    """Desktop Agent: Launches applications, manages windows, and lists running processes."""
    query = state.get("user_query", "").lower()
    app_logger.info(f"[DesktopAgent] Automating desktop task: '{query[:50]}'")

    desktop_actions = []
    output_text = ""

    if "launch" in query or "open" in query or "start" in query:
        # Extract target app name
        known_apps = [
            "vscode", "vs code", "visual studio code", "spotify", "calculator", "calc",
            "chrome", "notepad", "terminal", "cmd", "powershell", "linkedin", "whatsapp",
            "slack", "discord", "teams", "explorer", "youtube", "github", "chatgpt",
            "gmail", "google", "reddit", "twitter", "x", "facebook", "instagram",
            "camera", "photos", "paint", "settings", "clock"
        ]
        target_app = None
        for app in known_apps:
            if app in query:
                target_app = app
                break
        
        if not target_app:
            # Fallback launch target extraction using word boundary regex stripping
            import re
            target_app = re.sub(r'\b(?:launch|open|start|run|app|application|local|the)\b', '', query, flags=re.IGNORECASE).strip()
            target_app = target_app or "calculator"

        res = launch_app_tool.invoke({"app_name": target_app})
        desktop_actions.append({"action": "launch_app", "target": target_app, "result": res})
        output_text += f"\n- {res}"
    elif "list" in query or "process" in query or "running" in query:
        res = list_running_apps_tool.invoke({"limit": 8})
        desktop_actions.append({"action": "list_running_apps", "result": res})
        output_text += f"\n\nActive Running Processes:\n{res}"

    reasoning = state.get("intermediate_reasoning", []) + [f"Desktop Agent performed {len(desktop_actions)} automation actions"]

    return {
        "current_agent": "desktop",
        "next_agent": "validator",
        "desktop_actions": desktop_actions,
        "formatted_response": output_text.strip() if output_text else "Desktop automation task complete.",
        "intermediate_reasoning": reasoning
    }
