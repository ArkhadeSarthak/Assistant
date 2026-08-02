from fastapi import APIRouter
from pydantic import BaseModel
from app.graphs.executor import run_aura_agent

router = APIRouter(prefix="", tags=["Agents"])

class AgentRunRequest(BaseModel):
    agent_name: str = "coordinator"
    task: str
    session_id: str = "default-session"

@router.get("/agents")
async def list_agents():
    return {
        "agents": [
            {"name": "Coordinator Agent", "role": "Orchestrates multi-agent routing"},
            {"name": "Planner Agent", "role": "Generates step-by-step task breakdown"},
            {"name": "Reasoning Agent", "role": "Evaluates logical consistency & synthesis"},
            {"name": "Chat Agent", "role": "Direct conversational assistant"},
            {"name": "Coding Agent", "role": "Generates, reviews, and executes code"},
            {"name": "File Agent", "role": "Parses and extracts content from documents"},
            {"name": "Browser Agent", "role": "Navigates and extracts web information"},
            {"name": "Search Agent", "role": "Queries real-time web search engines"},
            {"name": "Memory Agent", "role": "Manages session and vector memory"},
            {"name": "Voice Agent", "role": "Handles speech synthesis and recognition"}
        ]
    }

@router.post("/agent/run")
async def run_agent_endpoint(request: AgentRunRequest):
    final_state = await run_aura_agent(request.session_id, request.task)
    return {
        "agent": request.agent_name,
        "session_id": request.session_id,
        "task": request.task,
        "response": final_state.get("final_response", ""),
        "execution_logs": final_state.get("execution_logs", [])
    }
