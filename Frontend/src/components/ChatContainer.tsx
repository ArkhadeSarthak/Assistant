"use client";

import React, { useEffect, useRef } from "react";
import { Sparkles } from "lucide-react";
import { useChatStore } from "@/store/useChatStore";
import { MessageBubble } from "./MessageBubble";

export const ChatContainer: React.FC = () => {
  const { messages } = useChatStore();
  const scrollEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll on new messages or streaming content
  useEffect(() => {
    scrollEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, messages[messages.length - 1]?.content]);

  return (
    <div className="w-full max-w-3xl mx-auto flex-1 overflow-y-auto px-4 py-2 scroll-smooth flex flex-col z-10">
      {messages.length === 0 ? (
        /* Minimal Empty State - No suggestion cards */
        <div className="my-auto flex flex-col items-center justify-center text-center py-10 px-4 animate-in fade-in zoom-in-95 duration-500">
          <div className="w-16 h-16 rounded-3xl bg-gradient-to-tr from-purple-600/30 to-blue-600/30 border border-purple-500/30 flex items-center justify-center shadow-2xl mb-4 backdrop-blur-xl">
            <Sparkles className="w-8 h-8 text-purple-400 animate-pulse" />
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white mb-2">
            How can I help you today?
          </h2>
          <p className="text-xs sm:text-sm text-zinc-400 max-w-md leading-relaxed">
            Ask any question, attach files, or switch to voice mode to begin.
          </p>
        </div>
      ) : (
        /* Conversation Message Feed */
        <div className="flex flex-col py-4">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
          <div ref={scrollEndRef} />
        </div>
      )}
    </div>
  );
};
