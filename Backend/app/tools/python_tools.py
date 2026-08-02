import sys
import io
from pydantic import BaseModel, Field
from langchain.tools import tool
from app.utils.logger import app_logger

class PythonExecutionInput(BaseModel):
    code: str = Field(description="Python code snippet to execute")

@tool("execute_python", args_schema=PythonExecutionInput)
def execute_python_tool(code: str) -> str:
    """Executes a Python code snippet and captures stdout output."""
    app_logger.info(f"Executing Python code:\n{code}")
    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output

    try:
        local_scope = {}
        exec(code, {"__builtins__": __builtins__}, local_scope)
        sys.stdout = old_stdout
        output = redirected_output.getvalue()
        if not output and local_scope:
            output = f"Execution finished. Scope variables: {list(local_scope.keys())}"
        return output if output else "Code executed successfully with no stdout output."
    except Exception as e:
        sys.stdout = old_stdout
        return f"Python Execution Error: {str(e)}"
