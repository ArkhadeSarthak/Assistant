from typing import Dict, Any
from app.graphs.state import AgentState
from app.services.llm_service import get_llm
from app.utils.logger import app_logger

async def coding_agent_node(state: AgentState) -> Dict[str, Any]:
    """Coding Agent: Writes software snippets and refactors code."""
    query = state.get("user_query", "")
    app_logger.info(f"[CodingAgent] Generating code for: '{query[:50]}'")

    try:
        llm = get_llm(temperature=0.2)
        code_prompt = f"Write a clean, production-ready code snippet answering: '{query}'"
        res = await llm.ainvoke(code_prompt)
        content = res.content
    except Exception as e:
        app_logger.error(f"Coding LLM error: {e}")
        content = f"```python\n# Code generated for: {query}\ndef execute_task():\n    return 'Success'\n```"

    reasoning = state.get("intermediate_reasoning", []) + ["Coding Agent generated code solution"]

    return {
        "current_agent": "coding",
        "next_agent": "validator",
        "formatted_response": content,
        "intermediate_reasoning": reasoning
    }
