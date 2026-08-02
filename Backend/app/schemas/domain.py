from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime

class MessageSchema(BaseModel):
    id: Optional[str] = None
    role: str # 'user' | 'assistant' | 'system'
    content: str
    timestamp: Optional[str] = None
    reasoning: Optional[Dict[str, Any]] = None
    tools_used: Optional[List[Dict[str, Any]]] = None

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    files: Optional[List[str]] = []
    stream: bool = True

class ChatResponse(BaseModel):
    session_id: str
    message: MessageSchema
    execution_time_ms: float

class StreamEvent(BaseModel):
    event_type: str # 'token' | 'thinking' | 'tool_start' | 'tool_end' | 'error' | 'done'
    data: Any

class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

class ToolExecutionSchema(BaseModel):
    id: str
    tool_name: str
    status: str
    inputs: Dict[str, Any]
    outputs: Optional[Dict[str, Any]] = None
    execution_time_ms: float

class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_type: str
    file_size: int
    extracted_text_snippet: Optional[str] = None

class MemoryItemSchema(BaseModel):
    key: str
    value: str
    memory_type: str = "short_term"

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None
