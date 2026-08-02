export interface ChatApiRequest {
  conversation_id?: string;
  session_id?: string;
  user_id?: string;
  message: string;
  attachments?: string[];
  files?: string[];
  voice?: boolean;
  stream?: boolean;
}

export interface MessageApiSchema {
  id?: string;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  timestamp?: string;
  reasoning?: {
    summary?: string;
    steps?: string[];
    durationSeconds?: number;
  };
  tools_used?: Array<{
    id?: string;
    name: string;
    details?: string;
    status: "running" | "completed" | "error";
  }>;
}

export interface ChatApiResponse {
  session_id: string;
  message: MessageApiSchema;
  execution_time_ms: float;
}

export interface SSEStreamEvent {
  event_type: "token" | "thinking" | "tool_start" | "tool_end" | "error" | "done";
  data: any;
}

export interface FileUploadApiResponse {
  file_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  extracted_text_snippet?: string;
}

export interface ToolInfoResponse {
  name: string;
  description: string;
  args_schema?: any;
}

export interface ToolExecutionApiRequest {
  tool_name: str;
  arguments: Record<string, any>;
}

export interface ToolExecutionApiResponse {
  id: string;
  tool_name: string;
  status: "running" | "completed" | "error";
  inputs: Record<string, any>;
  outputs?: Record<string, any>;
  execution_time_ms: number;
}

export type float = number;
export type str = string;
