from typing import Dict, Any
from app.graphs.state import AgentState
from app.services.llm_service import get_llm
from app.utils.logger import app_logger

async def coding_agent_node(state: AgentState) -> Dict[str, Any]:
    """Coding Agent: Answers programming questions or writes software code snippets."""
    query = state.get("user_query", "")
    app_logger.info(f"[CodingAgent] Processing query: '{query[:50]}'")

    try:
        llm = get_llm(temperature=0.3)
        code_prompt = (
            f"User request: '{query}'\n\n"
            f"Provide a clear, direct, and well-explained natural language response. "
            f"Include code blocks only if the user explicitly asked for code snippets or program implementations."
        )
        res = await llm.ainvoke(code_prompt)
        content = res.content
    except Exception as e:
        app_logger.error(f"Coding LLM error: {e}")
        content = f"Error processing coding request for: {query}"

    reasoning = state.get("intermediate_reasoning", []) + ["Coding Agent generated response"]

    return {
        "current_agent": "coding",
        "next_agent": "validator",
        "formatted_response": content,
        "final_response": content,
        "intermediate_reasoning": reasoning
    }
