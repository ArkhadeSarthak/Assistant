"use client";

import React from "react";
import {
  Brain,
  ListOrdered,
  Search,
  FileText,
  Globe,
  Code,
  LineChart,
  CheckCircle,
  Loader2,
  Cpu
} from "lucide-react";
import { ToolExecution } from "@/store/useChatStore";
import { motion, AnimatePresence } from "framer-motion";

interface ToolStatusCardProps {
  tool: ToolExecution | null;
}

export const ToolStatusCard: React.FC<ToolStatusCardProps> = ({ tool }) => {
  if (!tool) return null;

  const getToolIcon = () => {
    switch (tool.name) {
      case "Thinking":
        return <Brain className="w-4 h-4 text-purple-400 animate-pulse" />;
      case "Planning":
        return <ListOrdered className="w-4 h-4 text-blue-400" />;
      case "Searching Web":
        return <Search className="w-4 h-4 text-emerald-400" />;
      case "Reading File":
        return <FileText className="w-4 h-4 text-amber-400" />;
      case "Calling API":
        return <Cpu className="w-4 h-4 text-indigo-400" />;
      case "Using Browser":
        return <Globe className="w-4 h-4 text-cyan-400" />;
      case "Writing Code":
        return <Code className="w-4 h-4 text-purple-400" />;
      case "Analyzing Data":
        return <LineChart className="w-4 h-4 text-pink-400" />;
      default:
        return <Cpu className="w-4 h-4 text-purple-400" />;
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 10, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 10, scale: 0.95 }}
        transition={{ duration: 0.2 }}
        className="fixed bottom-24 left-1/2 -translate-x-1/2 z-30 pointer-events-auto"
      >
        <div className="px-4 py-2.5 rounded-2xl bg-zinc-950/90 border border-purple-500/30 shadow-2xl backdrop-blur-xl flex items-center gap-3 text-xs">
          {/* Animated Icon Container */}
          <div className="w-7 h-7 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center shrink-0">
            {tool.status === "completed" ? (
              <CheckCircle className="w-4 h-4 text-emerald-400" />
            ) : (
              getToolIcon()
            )}
          </div>

          {/* Label and Details */}
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-zinc-100">{tool.name}</span>
              {tool.status === "running" && (
                <Loader2 className="w-3 h-3 text-purple-400 animate-spin" />
              )}
            </div>
            {tool.details && (
              <span className="text-[11px] text-zinc-400 max-w-[240px] sm:max-w-[320px] truncate">
                {tool.details}
              </span>
            )}
          </div>

          {/* Progress Bar Line */}
          <div className="w-16 h-1.5 rounded-full bg-white/10 overflow-hidden ml-2">
            <motion.div
              className={`h-full ${
                tool.status === "completed"
                  ? "bg-emerald-400"
                  : "bg-gradient-to-r from-purple-500 to-blue-500"
              }`}
              initial={{ width: "0%" }}
              animate={{
                width: tool.status === "completed" ? "100%" : "70%"
              }}
              transition={{
                duration: tool.status === "completed" ? 0.3 : 1.5,
                repeat: tool.status === "running" ? Infinity : 0,
                repeatType: "reverse"
              }}
            />
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};
