from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.graphs.state import AgentState
from app.graphs.router import route_next_agent
from app.graphs.nodes import (
    supervisor_agent_node,
    planner_agent_node,
    memory_agent_node,
    browser_agent_node,
    file_agent_node,
    research_agent_node,
    tool_agent_node,
    coding_agent_node,
    validation_agent_node,
    reflection_agent_node,
    formatter_agent_node,
    desktop_agent_node,
    system_agent_node,
    media_agent_node,
    communication_agent_node,
    automation_agent_node,
)

def build_aura_multi_agent_graph():
    workflow = StateGraph(AgentState)

    # Register Nodes
    workflow.add_node("memory", memory_agent_node)
    workflow.add_node("supervisor", supervisor_agent_node)
    workflow.add_node("planner", planner_agent_node)
    workflow.add_node("browser", browser_agent_node)
    workflow.add_node("file", file_agent_node)
    workflow.add_node("research", research_agent_node)
    workflow.add_node("coding", coding_agent_node)
    workflow.add_node("tool_agent", tool_agent_node)
    workflow.add_node("desktop", desktop_agent_node)
    workflow.add_node("system", system_agent_node)
    workflow.add_node("media", media_agent_node)
    workflow.add_node("communication", communication_agent_node)
    workflow.add_node("automation", automation_agent_node)
    workflow.add_node("validator", validation_agent_node)
    workflow.add_node("reflection", reflection_agent_node)
    workflow.add_node("formatter", formatter_agent_node)

    # Wire Edges
    workflow.add_edge(START, "memory")
    workflow.add_edge("memory", "supervisor")

    # Conditional Routing from Supervisor
    workflow.add_conditional_edges("supervisor", route_next_agent)

    # Specialized agent outputs pipeline into validator -> reflection -> formatter -> END
    workflow.add_edge("planner", "validator")
    workflow.add_edge("browser", "validator")
    workflow.add_edge("file", "validator")
    workflow.add_edge("research", "validator")
    workflow.add_edge("coding", "validator")
    workflow.add_edge("tool_agent", "validator")
    workflow.add_edge("desktop", "validator")
    workflow.add_edge("system", "validator")
    workflow.add_edge("media", "validator")
    workflow.add_edge("communication", "validator")
    workflow.add_edge("automation", "validator")

    workflow.add_edge("validator", "reflection")
    workflow.add_edge("reflection", "formatter")
    workflow.add_edge("formatter", END)

    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)
    return app

aura_agent_graph = build_aura_multi_agent_graph()
