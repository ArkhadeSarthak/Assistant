from typing import Dict, Any
from app.graphs.state import AgentState
from app.services.llm_service import get_llm
from app.utils.logger import app_logger

async def formatter_agent_node(state: AgentState) -> Dict[str, Any]:
    """Formatter Agent: Formats final response in clean Markdown with context memory, tables, and code blocks."""
    query = state.get("user_query", "")
    tool_results = state.get("tool_results", [])
    browser_results = state.get("browser_results", [])
    existing_format = state.get("formatted_response", "")
    history = state.get("conversation_history", [])
    memory = state.get("memory", {})
    
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
            
            context_parts = []
            if memory:
                mem_str = "\n".join([f"- {k}: {v}" for k, v in memory.items()])
                context_parts.append(f"Known User Memory Facts:\n{mem_str}")

            if history:
                hist_entries = [m for m in history if m.get("content") != query]
                if hist_entries:
                    hist_str = "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in hist_entries[-6:]])
                    context_parts.append(f"Recent Conversation History:\n{hist_str}")

            prompt = (
                "You are AURA AI, a smart assistant. Provide a direct, natural language answer. "
                "Respect any query constraints such as 'in short', 'briefly', or 'bullet points'. "
                "Do NOT wrap standard conceptual definitions inside dummy code blocks or function definitions.\n\n"
            )

            if context_parts:
                prompt += "Context Information:\n" + "\n\n".join(context_parts) + "\n\n"

            prompt += f"User Query: '{query}'"
            if obs:
                prompt += "\n\nObservations from executed tools:\n" + "\n".join(obs)

            res = await llm.ainvoke(prompt)
            final_text = res.content
        except Exception as e:
            err_str = str(e)
            app_logger.error(f"Formatter LLM error: {err_str}")
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                final_text = "⚠️ **Gemini API Rate Limit Reached (429 Quota Exhausted)**\n\nThe free tier request limit for Gemini API has been reached. Please wait ~30 seconds and try again."
            else:
                obs_text = ("\n\n" + "\n".join(obs)) if obs else ""
                final_text = f"I have processed your query: **'{query}'**.{obs_text}"

    reasoning = state.get("intermediate_reasoning", []) + ["Formatter Agent finalized Markdown presentation"]

    return {
        "current_agent": "formatter",
        "next_agent": "END",
        "formatted_response": final_text,
        "final_response": final_text,
        "intermediate_reasoning": reasoning,
        "execution_status": "completed"
    }
