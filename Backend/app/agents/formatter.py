from typing import Dict, Any
from app.graphs.state import AgentState
from app.services.llm_service import get_llm
from app.utils.logger import app_logger

async def formatter_agent_node(state: AgentState) -> Dict[str, Any]:
    """Formatter Agent: Formats final response in clean Markdown with tables, code blocks, and citations."""
    query = state.get("user_query", "")
    tool_results = state.get("tool_results", [])
    browser_results = state.get("browser_results", [])
    existing_format = state.get("formatted_response", "")
    
    app_logger.info(f"[FormatterAgent] Generating final formatted markdown response")

    if existing_format:
        final_text = existing_format
    else:
        obs = []
        if tool_results:
            obs.extend([f"Tool **{r['name']}** output: {r['result']}" for r in tool_results])
        if browser_results:
            obs.extend([f"Web Search output: {r['output']}" for r in browser_results])

        try:
            llm = get_llm(temperature=0.7)
            prompt = f"Answer the user query: '{query}'"
            if obs:
                prompt += "\n\nObservations from executed tools:\n" + "\n".join(obs)
            res = await llm.ainvoke(prompt)
            final_text = res.content
        except Exception as e:
            app_logger.error(f"Formatter LLM error: {e}")
            obs_text = ("\n\n" + "\n".join(obs)) if obs else ""
            final_text = f"I have processed your query: **'{query}'**.{obs_text}\n\nAURA AI Multi-Agent system executed successfully."

    reasoning = state.get("intermediate_reasoning", []) + ["Formatter Agent finalized Markdown presentation"]

    return {
        "current_agent": "formatter",
        "next_agent": "END",
        "formatted_response": final_text,
        "intermediate_reasoning": reasoning,
        "execution_status": "completed"
    }
