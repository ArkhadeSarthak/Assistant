from typing import Literal
from app.graphs.state import AgentState

def route_next_agent(state: AgentState) -> Literal["supervisor", "planner", "browser", "file", "research", "coding", "tool_agent", "desktop", "system", "media", "communication", "automation", "validator", "reflection", "formatter", "__end__"]:
    """Conditional edge router determining next StateGraph node from state['next_agent']."""
    next_node = state.get("next_agent", "formatter")
    
    if next_node == "supervisor":
        return "supervisor"
    elif next_node == "planner":
        return "planner"
    elif next_node == "browser":
        return "browser"
    elif next_node == "file":
        return "file"
    elif next_node == "research":
        return "research"
    elif next_node == "coding":
        return "coding"
    elif next_node == "tool_agent":
        return "tool_agent"
    elif next_node == "desktop":
        return "desktop"
    elif next_node == "system":
        return "system"
    elif next_node == "media":
        return "media"
    elif next_node == "communication":
        return "communication"
    elif next_node == "automation":
        return "automation"
    elif next_node == "validator":
        return "validator"
    elif next_node == "reflection":
        return "reflection"
    elif next_node == "formatter":
        return "formatter"
    else:
        return "__end__"
