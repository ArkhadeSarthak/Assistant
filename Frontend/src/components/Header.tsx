"use client";

import React from "react";
import { Sparkles, Bot, Trash2 } from "lucide-react";
import { useChatStore } from "@/store/useChatStore";

export const Header: React.FC = () => {
  const { clearChat, messages } = useChatStore();

  // Hide heading for new conversation; show only when conversation starts (messages exist)
  if (messages.length === 0) {
    return null;
  }

  return (
    <header className="w-full max-w-3xl mx-auto pt-5 pb-3 px-4 flex items-center justify-between relative z-20 shrink-0 select-none animate-in fade-in duration-300">
      {/* Left section: Icon on left, content on right */}
      <div className="flex items-center gap-3.5">
        {/* AI Logo Badge */}
        <div className="relative group cursor-pointer shrink-0">
          <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 via-blue-500 to-emerald-400 rounded-2xl blur-md opacity-75 group-hover:opacity-100 transition duration-500 group-hover:scale-105" />
          <div className="relative w-11 h-11 rounded-2xl bg-zinc-950/90 border border-white/15 flex items-center justify-center shadow-2xl backdrop-blur-xl">
            <Sparkles className="w-5.5 h-5.5 text-purple-400 animate-pulse" />
            <Bot className="w-3 h-3 text-blue-400 absolute bottom-1 right-1" />
          </div>
        </div>

        {/* Title & Subtitle on the right of icon */}
        <div className="flex flex-col justify-center">
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-extrabold tracking-tight bg-gradient-to-r from-white via-zinc-200 to-purple-300 bg-clip-text text-transparent">
              AURA AI
            </h1>
            <span className="px-2 py-0.5 text-[9px] font-semibold tracking-wider uppercase rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
              v1.0
            </span>
          </div>
          <p className="text-xs text-zinc-400 font-medium tracking-wide">
            Assistant
          </p>
        </div>
      </div>

      {/* Right section: Clear Chat Action */}
      <button
        onClick={clearChat}
        className="text-xs text-zinc-400 hover:text-red-400 flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 hover:border-red-500/30 transition-all duration-200 cursor-pointer"
        title="Clear conversation"
      >
        <Trash2 className="w-3.5 h-3.5" />
        <span className="hidden sm:inline">Clear Chat</span>
      </button>
    </header>
  );
};
