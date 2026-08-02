"use client";

import React, { useState } from "react";
import { ChevronDown, BrainCircuit, CheckCircle2, Loader2 } from "lucide-react";
import { ReasoningData } from "@/store/useChatStore";
import { motion, AnimatePresence } from "framer-motion";

interface ThinkingPanelProps {
  reasoning: ReasoningData;
  isStreaming?: boolean;
}

export const ThinkingPanel: React.FC<ThinkingPanelProps> = ({ reasoning, isStreaming }) => {
  const [isOpen, setIsOpen] = useState<boolean>(!!isStreaming);

  return (
    <div className="w-full my-2 rounded-xl bg-white/[0.03] border border-white/10 overflow-hidden backdrop-blur-md transition-all">
      {/* Accordion Header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3.5 py-2.5 flex items-center justify-between text-left text-xs text-purple-300/90 hover:text-purple-200 hover:bg-white/[0.04] transition-colors"
      >
        <div className="flex items-center gap-2">
          <BrainCircuit className={`w-4 h-4 text-purple-400 ${isStreaming ? "animate-pulse" : ""}`} />
          <span className="font-semibold tracking-wide">
            {isStreaming ? "Thinking and Reasoning..." : `Thought for ${reasoning.durationSeconds}s`}
          </span>
          {isStreaming && (
            <span className="flex items-center gap-1 ml-1 text-purple-400">
              <Loader2 className="w-3 h-3 animate-spin" />
            </span>
          )}
        </div>
        <ChevronDown
          className={`w-4 h-4 text-zinc-400 transition-transform duration-300 ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>

      {/* Accordion Content */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: "easeInOut" }}
            className="border-t border-white/5 px-4 py-3 bg-black/20 text-xs text-zinc-300 space-y-2"
          >
            <p className="text-zinc-400 italic text-[11px] leading-relaxed mb-2">
              "{reasoning.summary}"
            </p>
            <div className="space-y-1.5 pl-1">
              {reasoning.steps.map((step, idx) => (
                <div key={idx} className="flex items-start gap-2 text-zinc-300">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                  <span className="leading-snug">{step}</span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
