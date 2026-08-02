from typing import Dict, Any
from app.graphs.state import AgentState
from app.tools.desktop_tools import launch_app_tool
from app.tools.search_tools import web_search_tool
from app.utils.logger import app_logger

async def automation_agent_node(state: AgentState) -> Dict[str, Any]:
    """Automation Agent: Executes chained multi-step desktop & web automation workflows."""
    query = state.get("user_query", "")
    app_logger.info(f"[AutomationAgent] Executing chained workflow: '{query[:50]}'")

    steps_log = []

    # Step 1: Launch App
    res1 = launch_app_tool.invoke({"app_name": "chrome"})
    steps_log.append(f"Step 1: {res1}")

    # Step 2: Web Search
    res2 = await web_search_tool.ainvoke({"query": query})
    steps_log.append(f"Step 2: Web Search completed for '{query}'")

    # Step 3: Launch Editor
    res3 = launch_app_tool.invoke({"app_name": "vscode"})
    steps_log.append(f"Step 3: {res3}")

    formatted_output = "### ⚡ Chained Workflow Execution Complete\n\n" + "\n".join([f"- {s}" for s in steps_log])
    reasoning = state.get("intermediate_reasoning", []) + [f"Automation Agent executed 3-step chained workflow for '{query}'"]

    return {
        "current_agent": "automation",
        "next_agent": "validator",
        "formatted_response": formatted_output,
        "intermediate_reasoning": reasoning
    }
