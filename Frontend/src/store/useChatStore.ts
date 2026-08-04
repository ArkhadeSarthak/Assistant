import { create } from "zustand";
import { streamChatMessage, clearChatSession } from "@/services/chat";
import { uploadFileService } from "@/services/upload";
import { parseAndExecuteActionDirective } from "@/services/local_bridge";

export interface FileAttachment {
  id: string;
  name: string;
  type: string;
  size: string;
  url?: string;
  isUploading?: boolean;
}


export interface ToolExecution {
  id: string;
  name: "Thinking" | "Planning" | "Searching Web" | "Reading File" | "Calling API" | "Using Browser" | "Writing Code" | "Analyzing Data" | string;
  details?: string;
  status: "running" | "completed" | "error";
  iconName?: string;
}

export interface ReasoningData {
  summary: string;
  steps: string[];
  durationSeconds: number;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  files?: FileAttachment[];
  reasoning?: ReasoningData;
  tools?: ToolExecution[];
  isStreaming?: boolean;
}

interface ChatStore {
  sessionId: string;
  messages: Message[];
  inputValue: string;
  attachedFiles: FileAttachment[];
  isVoiceMode: boolean;
  voiceState: "listening" | "speaking" | "idle";
  voiceTimer: number;
  activeTool: ToolExecution | null;
  isGenerating: boolean;
  liveTranscript: string;
  abortController: AbortController | null;

  // Actions
  setInputValue: (val: string) => void;
  addAttachedFile: (file: FileAttachment) => void;
  uploadFileAndAttach: (file: File) => Promise<void>;
  removeAttachedFile: (id: string) => void;
  clearAttachedFiles: () => void;
  setVoiceMode: (enabled: boolean) => void;
  setVoiceState: (state: "listening" | "speaking" | "idle") => void;
  incrementVoiceTimer: () => void;
  resetVoiceTimer: () => void;
  sendMessage: (text?: string) => Promise<void>;
  stopGenerating: () => void;
  clearChat: () => void;
}

const INITIAL_MESSAGES: Message[] = [];

export const useChatStore = create<ChatStore>((set, get) => ({
  sessionId: `sess-${Date.now()}`,
  messages: INITIAL_MESSAGES,
  inputValue: "",
  attachedFiles: [],
  isVoiceMode: false,
  voiceState: "idle",
  voiceTimer: 0,
  activeTool: null,
  isGenerating: false,
  liveTranscript: "Listening...",
  abortController: null,

  setInputValue: (val) => set({ inputValue: val }),

  addAttachedFile: (file) =>
    set((state) => ({ attachedFiles: [...state.attachedFiles, file] })),

  uploadFileAndAttach: async (file: File) => {
    const isImage = file.type.startsWith("image/") || /\.(jpg|jpeg|png|webp|gif|bmp)$/i.test(file.name);
    const objectUrl = isImage ? URL.createObjectURL(file) : undefined;
    const tempId = `file-temp-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`;
    const sizeMB = (file.size / (1024 * 1024)).toFixed(1);

    const tempAttachment: FileAttachment = {
      id: tempId,
      name: file.name,
      type: file.name.split(".").pop() || "file",
      size: `${sizeMB} MB`,
      url: objectUrl,
      isUploading: true
    };

    // Immediately add file to UI with loader spinner
    set((state) => ({ attachedFiles: [...state.attachedFiles, tempAttachment] }));

    try {
      const result = await uploadFileService(file);
      set((state) => ({
        attachedFiles: state.attachedFiles.map((f) =>
          f.id === tempId
            ? {
                id: result.file_id,
                name: result.filename,
                type: result.file_type.split("/").pop() || "file",
                size: `${(result.file_size / (1024 * 1024)).toFixed(1)} MB`,
                url: objectUrl,
                isUploading: false
              }
            : f
        )
      }));
    } catch (e) {
      console.warn("Upload service error, keeping local attachment fallback:", e);
      set((state) => ({
        attachedFiles: state.attachedFiles.map((f) =>
          f.id === tempId ? { ...f, isUploading: false } : f
        )
      }));
    }
  },



  removeAttachedFile: (id) =>
    set((state) => ({ attachedFiles: state.attachedFiles.filter((f) => f.id !== id) })),

  clearAttachedFiles: () => set({ attachedFiles: [] }),

  setVoiceMode: (enabled) =>
    set(() => ({
      isVoiceMode: enabled,
      voiceState: enabled ? "listening" : "idle",
      voiceTimer: 0,
      liveTranscript: enabled ? "Listening..." : ""
    })),

  setVoiceState: (vState) => set({ voiceState: vState }),
  incrementVoiceTimer: () => set((state) => ({ voiceTimer: state.voiceTimer + 1 })),
  resetVoiceTimer: () => set({ voiceTimer: 0 }),

  clearChat: () => {
    const currentSessionId = get().sessionId;
    if (currentSessionId) {
      clearChatSession(currentSessionId);
    }
    set({ messages: [], sessionId: `sess-${Date.now()}` });
  },

  stopGenerating: () => {
    const { abortController, messages } = get();
    if (abortController) {
      abortController.abort();
    }
    set({
      isGenerating: false,
      activeTool: null,
      abortController: null,
      messages: messages.map((m) =>
        m.isStreaming ? { ...m, isStreaming: false } : m
      )
    });
  },

  sendMessage: async (textToSend) => {
    const state = get();
    const text = textToSend || state.inputValue.trim();
    if (!text && state.attachedFiles.length === 0) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      files: state.attachedFiles.length > 0 ? [...state.attachedFiles] : undefined
    };

    const assistantMsgId = `msg-assistant-${Date.now()}`;
    const assistantMessage: Message = {
      id: assistantMsgId,
      role: "assistant",
      content: "",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      isStreaming: true
    };

    const controller = new AbortController();

    set((s) => ({
      messages: [...s.messages, userMessage, assistantMessage],
      inputValue: "",
      attachedFiles: [],
      isGenerating: true,
      abortController: controller,
      activeTool: {
        id: `t-init`,
        name: "Thinking",
        details: "Connecting to AURA AI Backend...",
        status: "running"
      }
    }));

    let hasReceivedTokens = false;

    // Invoke SSE stream backend service
    await streamChatMessage(
      {
        session_id: state.sessionId,
        message: text,
        files: userMessage.files ? userMessage.files.map((f) => f.name) : []
      },
      {
        onThinking: (data) => {
          set({
            activeTool: {
              id: `t-think`,
              name: "Thinking",
              details: typeof data === "string" ? data : "Analyzing request...",
              status: "running"
            }
          });
        },
        onToolStart: (tool) => {
          set({
            activeTool: {
              id: `t-${tool.name}`,
              name: tool.name as any,
              details: `Executing ${tool.name}...`,
              status: "running"
            }
          });
        },
        onToolEnd: (toolResult) => {
          set({
            activeTool: {
              id: `t-${toolResult.name}`,
              name: toolResult.name as any,
              details: toolResult.result ? toolResult.result.slice(0, 40) : "Completed",
              status: toolResult.status === "error" ? "error" : "completed"
            }
          });
        },
        onToken: (token) => {
          hasReceivedTokens = true;
          set((s) => ({
            activeTool: null,
            messages: s.messages.map((m) =>
              m.id === assistantMsgId ? { ...m, content: m.content + token } : m
            )
          }));
        },
        onDone: () => {
          const currentStore = get();
          const assistantMsg = currentStore.messages.find((m) => m.id === assistantMsgId);
          let cleanedContent = assistantMsg ? assistantMsg.content : "";

          if (assistantMsg && assistantMsg.content) {
            // Trigger local desktop OS action via local companion bridge
            cleanedContent = parseAndExecuteActionDirective(assistantMsg.content);

            const queryLower = text.toLowerCase().trim();
            if (queryLower.startsWith("open ") || queryLower.startsWith("launch ") || queryLower.startsWith("search ")) {
              const urlMatch = assistantMsg.content.match(/https?:\/\/[^\s\)\>\]]+/);
              if (urlMatch && typeof window !== "undefined") {
                try {
                  window.open(urlMatch[0], "_blank");
                } catch (e) {
                  console.warn("Popup blocked or failed to open:", e);
                }
              }
            }
          }

          set((s) => ({
            activeTool: null,
            isGenerating: false,
            abortController: null,
            messages: s.messages.map((m) =>
              m.id === assistantMsgId ? { ...m, content: cleanedContent, isStreaming: false } : m
            )
          }));
        },
        onError: (errMessage) => {
          console.warn("Backend streaming error:", errMessage);
          if (!hasReceivedTokens) {
            // Provide clean fallback message if server is offline or fails
            const fallbackText = `I have received your request: **"${text}"**.

FastAPI + LangGraph backend engine is connecting. How else can I assist you today?`;
            set((s) => ({
              activeTool: null,
              isGenerating: false,
              abortController: null,
              messages: s.messages.map((m) =>
                m.id === assistantMsgId
                  ? { ...m, content: fallbackText, isStreaming: false }
                  : m
              )
            }));
          } else {
            set((s) => ({
              activeTool: null,
              isGenerating: false,
              abortController: null,
              messages: s.messages.map((m) =>
                m.id === assistantMsgId ? { ...m, isStreaming: false } : m
              )
            }));
          }
        }
      },
      controller.signal
    );
  }
}));
