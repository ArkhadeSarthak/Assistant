"use client";

import React, { useEffect } from "react";
import { Mic, MicOff, Square, Radio, Sparkles } from "lucide-react";
import { useChatStore } from "@/store/useChatStore";
import { motion } from "framer-motion";

export const VoicePanel: React.FC = () => {
  const {
    setVoiceMode,
    voiceState,
    setVoiceState,
    voiceTimer,
    incrementVoiceTimer,
    resetVoiceTimer,
    liveTranscript
  } = useChatStore();

  // Timer interval effect
  useEffect(() => {
    const interval = setInterval(() => {
      incrementVoiceTimer();
    }, 1000);
    return () => clearInterval(interval);
  }, [incrementVoiceTimer]);

  // Simulate toggle speaking vs listening for demo feel
  const toggleListeningSpeaking = () => {
    if (voiceState === "listening") {
      setVoiceState("speaking");
    } else {
      setVoiceState("listening");
    }
  };

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="w-full max-w-xl mx-auto my-auto p-8 rounded-3xl glass-panel border border-purple-500/20 shadow-2xl flex flex-col items-center justify-center relative overflow-hidden backdrop-blur-2xl"
    >
      {/* Background radial glow */}
      <div className="absolute inset-0 bg-gradient-to-b from-purple-600/10 via-blue-600/5 to-transparent pointer-events-none" />

      {/* Floating Particles Around Mic */}
      <div className="absolute inset-0 pointer-events-none">
        <motion.div
          animate={{ y: [-10, 10, -10], opacity: [0.3, 0.8, 0.3] }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-1/4 left-1/4 w-2 h-2 rounded-full bg-purple-400 blur-[1px]"
        />
        <motion.div
          animate={{ y: [10, -10, 10], opacity: [0.2, 0.7, 0.2] }}
          transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
          className="absolute top-1/3 right-1/4 w-3 h-3 rounded-full bg-blue-400 blur-[1px]"
        />
        <motion.div
          animate={{ scale: [0.8, 1.2, 0.8], opacity: [0.4, 0.9, 0.4] }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
          className="absolute bottom-1/3 left-1/3 w-2 h-2 rounded-full bg-emerald-400 blur-[1px]"
        />
      </div>

      {/* Status Badge & Voice Timer */}
      <div className="flex items-center gap-3 mb-8 z-10">
        <div className="px-3.5 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/30 flex items-center gap-2">
          <Radio className="w-4 h-4 text-purple-400 animate-pulse" />
          <span className="text-xs font-semibold uppercase tracking-wider text-purple-300">
            {voiceState === "listening" ? "Listening..." : "Aura Speaking..."}
          </span>
        </div>
        <div className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-mono text-zinc-300">
          {formatTimer(voiceTimer)}
        </div>
      </div>

      {/* Large Glowing Mic & Circular Waveform */}
      <div className="relative my-6 flex items-center justify-center z-10 cursor-pointer" onClick={toggleListeningSpeaking}>
        {/* Outer Circular Ripples */}
        <motion.div
          animate={{ scale: [1, 1.4, 1], opacity: [0.2, 0.6, 0.2] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
          className="absolute w-44 h-44 rounded-full border border-purple-500/30 bg-purple-500/5"
        />
        <motion.div
          animate={{ scale: [1, 1.7, 1], opacity: [0.1, 0.4, 0.1] }}
          transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
          className="absolute w-56 h-56 rounded-full border border-blue-500/20 bg-blue-500/5"
        />

        {/* Core Glowing Button */}
        <div className="relative w-28 h-28 rounded-full bg-gradient-to-tr from-purple-600 via-indigo-600 to-blue-500 p-[2px] shadow-2xl shadow-purple-600/40">
          <div className="w-full h-full rounded-full bg-zinc-950 flex items-center justify-center backdrop-blur-xl group hover:bg-zinc-900 transition-colors">
            <Mic className="w-12 h-12 text-purple-300 animate-pulse" />
          </div>
        </div>
      </div>

      {/* Sound Waves Equalizer (When AI speaks or listening) */}
      <div className="flex items-center justify-center gap-1.5 h-12 my-4 z-10">
        <div className="w-1.5 rounded-full bg-purple-500 animate-voice-wave-1" />
        <div className="w-1.5 rounded-full bg-indigo-500 animate-voice-wave-2" />
        <div className="w-1.5 rounded-full bg-blue-500 animate-voice-wave-3" />
        <div className="w-1.5 rounded-full bg-emerald-500 animate-voice-wave-4" />
        <div className="w-1.5 rounded-full bg-purple-500 animate-voice-wave-5" />
      </div>

      {/* Transcript Text */}
      <div className="w-full text-center px-6 my-2 z-10 min-h-[40px] flex items-center justify-center">
        <p className="text-sm font-medium text-zinc-300 italic">
          "{voiceState === "listening" ? liveTranscript : "Synthesizing real-time neural audio output..."}"
        </p>
      </div>

      {/* Controls: Stop Button */}
      <div className="mt-6 flex items-center gap-4 z-10">
        <button
          onClick={() => {
            resetVoiceTimer();
            setVoiceMode(false);
          }}
          className="px-6 py-2.5 rounded-2xl bg-red-500/20 hover:bg-red-500/30 border border-red-500/40 text-red-300 hover:text-red-200 text-xs font-semibold flex items-center gap-2 shadow-lg transition-all duration-200"
        >
          <Square className="w-4 h-4 fill-current" />
          <span>Exit Voice Mode</span>
        </button>
      </div>
    </motion.div>
  );
};
