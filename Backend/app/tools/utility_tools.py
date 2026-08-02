import math
import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from langchain.tools import tool
from app.utils.logger import app_logger

class CalculatorInput(BaseModel):
    expression: str = Field(description="Mathematical expression to evaluate, e.g., '2 + 2' or 'sqrt(16)'")

@tool("calculator", args_schema=CalculatorInput)
def calculator_tool(expression: str) -> str:
    """Evaluates a mathematical expression safely."""
    app_logger.info(f"Executing calculator tool with expression: {expression}")
    try:
        allowed_names = {
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "pi": math.pi, "e": math.e,
            "log": math.log, "pow": math.pow, "abs": abs, "round": round
        }
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

class UUIDGeneratorInput(BaseModel):
    count: int = Field(default=1, description="Number of UUIDs to generate")

@tool("uuid_generator", args_schema=UUIDGeneratorInput)
def uuid_generator_tool(count: int = 1) -> str:
    """Generates one or multiple UUID v4 strings."""
    app_logger.info(f"Generating {count} UUIDs")
    uuids = [str(uuid.uuid4()) for _ in range(min(count, 10))]
    return "\n".join(uuids)

class DateTimeInput(BaseModel):
    timezone: str = Field(default="UTC", description="Timezone, e.g. UTC")

@tool("datetime_now", args_schema=DateTimeInput)
def datetime_now_tool(timezone: str = "UTC") -> str:
    """Returns current date and time."""
    now = datetime.utcnow()
    return f"Current Date and Time (UTC): {now.strftime('%Y-%m-%d %H:%M:%S')}"
