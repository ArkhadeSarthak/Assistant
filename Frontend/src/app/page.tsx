"use client";

import React from "react";
import { Header } from "@/components/Header";
import { ChatContainer } from "@/components/ChatContainer";
import { InputArea } from "@/components/InputArea";
import { VoicePanel } from "@/components/VoicePanel";
import { ToolStatusCard } from "@/components/ToolStatusCard";
import { useChatStore } from "@/store/useChatStore";

export default function Home() {
  const { isVoiceMode, activeTool } = useChatStore();

  return (
    <main className="relative w-screen h-screen overflow-hidden flex flex-col justify-between bg-[#09090B] text-zinc-100 selection:bg-purple-500/30">
      {/* Background Animated Glowing Blobs */}
      <div className="bg-ambient-blob blob-purple" />
      <div className="bg-ambient-blob blob-blue" />
      <div className="bg-ambient-blob blob-green" />

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 bg-grid-pattern pointer-events-none z-0 opacity-60" />

      {/* Header Bar */}
      <Header />

      {/* Main Viewport Area: Voice Mode or Chat Area */}
      {isVoiceMode ? (
        <div className="flex-1 flex items-center justify-center p-4 z-20">
          <VoicePanel />
        </div>
      ) : (
        <>
          <ChatContainer />
          <InputArea />
        </>
      )}

      {/* Floating Tool Execution Status Card */}
      <ToolStatusCard tool={activeTool} />
    </main>
  );
}
