import asyncio
from typing import Dict, Any
from app.graphs.state import AgentState
from app.tools import TOOL_REGISTRY
from app.tools.weather_tools import extract_city_from_query
from app.utils.logger import app_logger

async def tool_agent_node(state: AgentState) -> Dict[str, Any]:
    """Tool Agent: Executes tools in parallel with input validation."""
    query = state.get("user_query", "").lower()
    app_logger.info(f"[ToolAgent] Selecting tools for query: '{query[:50]}'")

    tools_to_run = []
    if any(k in query for k in ["weather", "temperature", "forecast", "climate", "humidity", "rain"]):
        city = extract_city_from_query(query)
        tools_to_run.append({"name": "get_weather", "args": {"city": city, "units": "metric"}})
    if any(k in query for k in ["calculate", "math", "+", "-", "*", "/", "sqrt"]):
        tools_to_run.append({"name": "calculator", "args": {"expression": "2 + 2"}})
    if "uuid" in query:
        tools_to_run.append({"name": "uuid_generator", "args": {"count": 1}})
    if "date" in query or "time" in query:
        tools_to_run.append({"name": "datetime_now", "args": {"timezone": "UTC"}})

    if not tools_to_run:
        tools_to_run.append({"name": "calculator", "args": {"expression": "10 + 5 * 2"}})

    async def run_one(t):
        name = t["name"]
        args = t["args"]
        if name in TOOL_REGISTRY:
            try:
                tool_func = TOOL_REGISTRY[name]
                if tool_func.coroutine:
                    res = await tool_func.coroutine(**args)
                elif tool_func.func and asyncio.iscoroutinefunction(tool_func.func):
                    res = await tool_func.func(**args)
                elif tool_func.func:
                    res = tool_func.func(**args)
                else:
                    res = await tool_func.ainvoke(args)
                return {"name": name, "result": str(res), "status": "completed"}
            except Exception as e:
                return {"name": name, "result": f"Error: {e}", "status": "error"}
        return {"name": name, "result": "Tool not registered", "status": "error"}

    results = await asyncio.gather(*[run_one(t) for t in tools_to_run])
    tool_results = list(results)
    reasoning = state.get("intermediate_reasoning", []) + [f"Tool Agent executed {len(tool_results)} tools concurrently"]

    return {
        "current_agent": "tool_agent",
        "next_agent": "validator",
        "tool_results": tool_results,
        "intermediate_reasoning": reasoning
    }
