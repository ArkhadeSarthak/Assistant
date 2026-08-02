import os
import shutil
from pydantic import BaseModel, Field
from langchain.tools import tool
from app.utils.logger import app_logger

class ReadFileInput(BaseModel):
    file_path: str = Field(description="Relative or absolute path of file to read")

@tool("read_file", args_schema=ReadFileInput)
def read_file_tool(file_path: str) -> str:
    """Reads content of a local file."""
    app_logger.info(f"Reading file: {file_path}")
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist."
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content[:4000] # Truncated for safety
    except Exception as e:
        return f"Error reading file: {str(e)}"

class WriteFileInput(BaseModel):
    file_path: str = Field(description="Path of file to write")
    content: str = Field(description="Content to write into file")

@tool("write_file", args_schema=WriteFileInput)
def write_file_tool(file_path: str, content: str) -> str:
    """Writes content to a local file."""
    app_logger.info(f"Writing to file: {file_path}")
    try:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{file_path}'."
    except Exception as e:
        return f"Error writing file: {str(e)}"

class ListDirInput(BaseModel):
    dir_path: str = Field(default=".", description="Directory path to list")

@tool("list_dir", args_schema=ListDirInput)
def list_dir_tool(dir_path: str = ".") -> str:
    """Lists files and directories inside path."""
    app_logger.info(f"Listing directory: {dir_path}")
    try:
        items = os.listdir(dir_path)
        return "\n".join([f"- {item}" for item in items])
    except Exception as e:
        return f"Error listing directory: {str(e)}"
