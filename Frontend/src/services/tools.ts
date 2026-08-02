import { apiFetch } from "./api";
import { ToolInfoResponse, ToolExecutionApiResponse } from "@/types/api";

export async function fetchToolsService(): Promise<ToolInfoResponse[]> {
  return apiFetch<ToolInfoResponse[]>("/tools");
}

export async function executeToolService(
  toolName: string,
  args: Record<string, any>
): Promise<ToolExecutionApiResponse> {
  return apiFetch<ToolExecutionApiResponse>("/tool", {
    method: "POST",
    body: JSON.stringify({
      tool_name: toolName,
      arguments: args,
    }),
  });
}
