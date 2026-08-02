from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    messages: List[Dict[str, Any]]
    conversation_history: List[Dict[str, Any]]
    user_query: str
    intent: str
    task: str
    plan: List[str]
    retrieved_documents: List[Dict[str, Any]]
    memory: Dict[str, Any]
    browser_results: List[Dict[str, Any]]
    file_results: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    intermediate_reasoning: List[str]
    current_agent: str
    next_agent: str
    retry_count: int
    execution_status: str
    validation_result: Dict[str, Any]
    formatted_response: str
    metadata: Dict[str, Any]
    session_id: str
    user_id: Optional[str]
    timestamps: Dict[str, str]
