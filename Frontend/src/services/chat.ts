import { apiFetch } from "./api";
import { ChatApiRequest, ChatApiResponse, SSEStreamEvent } from "@/types/api";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function sendChatMessage(request: ChatApiRequest): Promise<ChatApiResponse> {
  return apiFetch<ChatApiResponse>("/chat", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function clearChatSession(sessionId: string): Promise<void> {
  if (!sessionId) return;
  try {
    await apiFetch<{ status: string }>("/chat/clear", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId })
    });
  } catch (err) {
    console.warn("Failed to clear chat session on backend/Redis:", err);
  }
}

export interface StreamCallbacks {
  onThinking?: (text: string) => void;
  onToolStart?: (tool: { name: string; status: string }) => void;
  onToolEnd?: (toolResult: any) => void;
  onToken?: (token: string) => void;
  onDone?: (data: any) => void;
  onError?: (error: string) => void;
}

export async function streamChatMessage(
  request: ChatApiRequest,
  callbacks: StreamCallbacks,
  signal?: AbortSignal
): Promise<void> {
  const url = `${BASE_URL}/stream`;
  const token = typeof window !== "undefined" ? localStorage.getItem("aura_token") : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify(request),
      signal,
    });

    if (!response.ok || !response.body) {
      throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith("data:")) {
          const jsonStr = trimmed.slice(5).trim();
          if (!jsonStr) continue;

          try {
            const eventData: SSEStreamEvent = JSON.parse(jsonStr);

            switch (eventData.event_type) {
              case "thinking":
                callbacks.onThinking?.(eventData.data);
                break;
              case "tool_start":
                callbacks.onToolStart?.(eventData.data);
                break;
              case "tool_end":
                callbacks.onToolEnd?.(eventData.data);
                break;
              case "token":
                callbacks.onToken?.(eventData.data);
                break;
              case "done":
                callbacks.onDone?.(eventData.data);
                break;
              case "error":
                callbacks.onError?.(eventData.data);
                break;
            }
          } catch (e) {
            console.warn("Failed to parse SSE payload line:", jsonStr, e);
          }
        }
      }
    }
  } catch (error: any) {
    if (error.name === "AbortError") {
      console.log("Stream generation stopped by user.");
      return;
    }
    callbacks.onError?.(error.message || "Failed to establish SSE stream.");
  }
}
