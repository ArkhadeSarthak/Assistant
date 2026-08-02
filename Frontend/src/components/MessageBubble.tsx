"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Bot, User, Wrench } from "lucide-react";
import { Message } from "@/store/useChatStore";
import { CodeBlock } from "./CodeBlock";
import { ThinkingPanel } from "./ThinkingPanel";
import { UploadChip } from "./UploadChip";

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === "user";

  return (
    <div
      className={`w-full flex gap-3 sm:gap-4 my-4 ${
        isUser ? "justify-end" : "justify-start"
      } animate-in fade-in slide-in-from-bottom-2 duration-300`}
    >
      {/* Assistant Avatar */}
      {!isUser && (
        <div className="w-8 h-8 rounded-xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center shrink-0 shadow-lg shadow-purple-900/20 mt-1">
          <Bot className="w-4 h-4 text-purple-400" />
        </div>
      )}

      {/* Bubble Container */}
      <div className={`max-w-[85%] sm:max-w-[78%] flex flex-col ${isUser ? "items-end" : "items-start"}`}>
        {/* Timestamp / Role Label */}
        <div className="flex items-center gap-2 mb-1 px-1">
          <span className="text-[11px] font-medium text-zinc-400">
            {isUser ? "You" : "Aura AI"}
          </span>
          <span className="text-[10px] text-zinc-400">{message.timestamp}</span>
        </div>

        {/* User Attached Files */}
        {isUser && message.files && message.files.length > 0 && (
          <div className="flex flex-wrap gap-2 justify-end mb-2">
            {message.files.map((file) => (
              <UploadChip key={file.id} file={file} />
            ))}
          </div>
        )}

        {/* Assistant Reasoning Panel */}
        {!isUser && message.reasoning && (
          <ThinkingPanel reasoning={message.reasoning} isStreaming={message.isStreaming} />
        )}

        {/* Assistant Tools Badges */}
        {!isUser && message.tools && message.tools.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-2">
            {message.tools.map((tool) => (
              <div
                key={tool.id}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-purple-500/10 border border-purple-500/20 text-[11px] font-medium text-purple-300"
              >
                <Wrench className="w-3 h-3 text-purple-400" />
                <span>{tool.name}</span>
                {tool.details && <span className="text-purple-400/70">({tool.details})</span>}
              </div>
            ))}
          </div>
        )}

        {/* Message Content Body */}
        <div
          className={`rounded-2xl px-4 py-3 sm:px-5 sm:py-3.5 shadow-xl text-sm leading-relaxed ${
            isUser
              ? "user-bubble text-white rounded-tr-xs font-normal"
              : "glass-panel text-zinc-100 rounded-tl-xs border border-white/10"
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className={`prose prose-invert max-w-none ${message.isStreaming ? "streaming-cursor" : ""}`}>
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code({ node, inline, className, children, ...props }: any) {
                    const match = /language-(\w+)/.exec(className || "");
                    return !inline && match ? (
                      <CodeBlock
                        language={match[1]}
                        value={String(children).replace(/\n$/, "")}
                      />
                    ) : (
                      <code
                        className="bg-white/10 px-1.5 py-0.5 rounded text-purple-300 font-mono text-xs"
                        {...props}
                      >
                        {children}
                      </code>
                    );
                  },
                  ul({ children }) {
                    return <ul className="list-disc pl-5 my-2 space-y-1 text-zinc-200">{children}</ul>;
                  },
                  ol({ children }) {
                    return <ol className="list-decimal pl-5 my-2 space-y-1 text-zinc-200">{children}</ol>;
                  },
                  p({ children }) {
                    return <p className="mb-3 last:mb-0 text-zinc-100">{children}</p>;
                  },
                  h1({ children }) {
                    return <h1 className="text-xl font-bold text-white mt-4 mb-2">{children}</h1>;
                  },
                  h2({ children }) {
                    return <h2 className="text-lg font-semibold text-white mt-3 mb-2">{children}</h2>;
                  },
                  h3({ children }) {
                    return <h3 className="text-base font-medium text-purple-300 mt-3 mb-1">{children}</h3>;
                  }
                }}
              >
                {message.content || (message.isStreaming ? "" : "...")}
              </ReactMarkdown>
            </div>
          )}
        </div>
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="w-8 h-8 rounded-xl bg-purple-600/30 border border-purple-400/40 flex items-center justify-center shrink-0 shadow-lg shadow-purple-900/30 mt-1">
          <User className="w-4 h-4 text-purple-200" />
        </div>
      )}
    </div>
  );
};
