from typing import Dict, Any
from app.graphs.state import AgentState
from app.utils.logger import app_logger

async def planner_agent_node(state: AgentState) -> Dict[str, Any]:
    """Planner Agent: Creates step-by-step execution plan."""
    query = state.get("user_query", "")
    app_logger.info(f"[PlannerAgent] Creating execution plan for query: '{query[:50]}'")

    plan = [
        "1. Deconstruct user objectives and dependencies",
        "2. Retrieve required context and tools",
        "3. Synthesize validated results into response"
    ]
    reasoning = state.get("intermediate_reasoning", []) + ["Planner generated 3-step execution plan"]

    return {
        "current_agent": "planner",
        "next_agent": "validator",
        "plan": plan,
        "intermediate_reasoning": reasoning
    }
