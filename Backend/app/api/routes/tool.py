import time
from fastapi import APIRouter, HTTPException
from app.schemas.domain import ToolCallRequest, ToolExecutionSchema
from app.tools import TOOL_REGISTRY, ALL_TOOLS
import asyncio

router = APIRouter(prefix="", tags=["Tools"])

@router.get("/tools")
async def get_tools():
    """Returns list of registered tools with metadata."""
    return [
        {
            "name": t.name,
            "description": t.description,
            "args_schema": t.args_schema.model_json_schema() if t.args_schema else None
        }
        for t in ALL_TOOLS
    ]

@router.post("/tool", response_model=ToolExecutionSchema)
async def execute_tool_endpoint(request: ToolCallRequest):
    if request.tool_name not in TOOL_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Tool '{request.tool_name}' not found")

    tool_obj = TOOL_REGISTRY[request.tool_name]
    start_time = time.time()
    
    try:
        if tool_obj.coroutine:
            res = await tool_obj.coroutine(**request.arguments)
        elif tool_obj.func and asyncio.iscoroutinefunction(tool_obj.func):
            res = await tool_obj.func(**request.arguments)
        elif tool_obj.func:
            res = tool_obj.func(**request.arguments)
        else:
            res = await tool_obj.ainvoke(request.arguments)
        elapsed_ms = (time.time() - start_time) * 1000
        return ToolExecutionSchema(
            id=f"exec-{int(start_time)}",
            tool_name=request.tool_name,
            status="completed",
            inputs=request.arguments,
            outputs={"result": str(res)},
            execution_time_ms=elapsed_ms
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return ToolExecutionSchema(
            id=f"exec-{int(start_time)}",
            tool_name=request.tool_name,
            status="error",
            inputs=request.arguments,
            outputs={"error": str(e)},
            execution_time_ms=elapsed_ms
        )
