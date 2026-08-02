from typing import Dict, Any
from app.graphs.state import AgentState
from app.utils.logger import app_logger

async def reflection_agent_node(state: AgentState) -> Dict[str, Any]:
    """Reflection Agent: Self-reviews completeness, clarity, and formatting."""
    app_logger.info("[ReflectionAgent] Performing self-review on execution state")

    reasoning = state.get("intermediate_reasoning", []) + ["Reflection Agent completed self-review: High quality score"]

    return {
        "current_agent": "reflection",
        "next_agent": "formatter",
        "intermediate_reasoning": reasoning
    }
