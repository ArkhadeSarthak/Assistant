"use client";

import React, { useRef, useState } from "react";
import { Paperclip, Mic, Send, Square, UploadCloud, Sparkles } from "lucide-react";
import { useChatStore } from "@/store/useChatStore";
import { UploadChip } from "./UploadChip";

export const InputArea: React.FC = () => {
  const {
    inputValue,
    setInputValue,
    sendMessage,
    stopGenerating,
    attachedFiles,
    uploadFileAndAttach,
    removeAttachedFile,
    setVoiceMode,
    isGenerating
  } = useChatStore();

  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);

  // Auto resize textarea
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!isGenerating && (inputValue.trim() || attachedFiles.length > 0)) {
        sendMessage();
        if (textareaRef.current) {
          textareaRef.current.style.height = "auto";
        }
      }
    }
  };

  // Process selected or dropped file via uploadFileAndAttach service
  const handleFileProcess = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    Array.from(files).forEach((file) => {
      uploadFileAndAttach(file);
    });
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileProcess(e.dataTransfer.files);
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className="w-full max-w-3xl mx-auto px-4 pb-6 pt-2 relative z-20 shrink-0 select-none"
    >
      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={(e) => handleFileProcess(e.target.files)}
        multiple
        accept=".pdf,.doc,.docx,.png,.jpg,.jpeg,.xlsx,.csv,.txt,.md"
        className="hidden"
      />

      {/* Drag and Drop Full overlay indicator */}
      {isDragging && (
        <div className="absolute inset-0 m-4 rounded-3xl border-2 border-dashed border-purple-400 bg-purple-950/80 backdrop-blur-xl flex flex-col items-center justify-center gap-2 z-40 text-purple-200">
          <UploadCloud className="w-8 h-8 text-purple-300 animate-bounce" />
          <span className="font-semibold text-sm">Drop PDF, Images, Code or Docs to upload</span>
        </div>
      )}

      {/* Upload Chips Container above prompt input */}
      {attachedFiles.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-2 px-3 py-2 rounded-2xl bg-black/40 border border-white/10 backdrop-blur-md">
          {attachedFiles.map((file) => (
            <UploadChip key={file.id} file={file} onRemove={removeAttachedFile} />
          ))}
        </div>
      )}

      {/* Main Glass Input Bar */}
      <div className="relative rounded-3xl glass-input p-2 flex items-end gap-2 shadow-2xl transition-all duration-300">
        {/* Attach File Button */}
        <button
          onClick={() => fileInputRef.current?.click()}
          className="p-2.5 rounded-2xl text-zinc-400 hover:text-purple-300 hover:bg-white/10 transition-all duration-200 shrink-0"
          title="Attach file (PDF, Images, DOCX, CSV, TXT)"
          aria-label="Attach File"
        >
          <Paperclip className="w-5 h-5" />
        </button>

        {/* Textarea Input */}
        <textarea
          ref={textareaRef}
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          rows={1}
          placeholder="Ask me anything..."
          className="w-full bg-transparent text-sm text-zinc-100 placeholder-zinc-400 focus:outline-none resize-none py-2 px-1 max-h-44 leading-relaxed font-sans"
        />

        {/* Microphone Voice Button */}
        <button
          onClick={() => setVoiceMode(true)}
          className="p-2.5 rounded-2xl text-zinc-400 hover:text-purple-300 hover:bg-white/10 transition-all duration-200 shrink-0"
          title="Activate Voice Assistant Mode"
          aria-label="Microphone"
        >
          <Mic className="w-5 h-5" />
        </button>

        {/* Send / Stop Button */}
        {isGenerating ? (
          <button
            onClick={() => stopGenerating()}
            className="p-2.5 rounded-2xl shrink-0 transition-all duration-200 bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30 hover:scale-105 active:scale-95 shadow-lg shadow-red-500/20 flex items-center justify-center"
            title="Stop response"
            aria-label="Stop Generating"
          >
            <Square className="w-5 h-5 fill-current text-red-400" />
          </button>
        ) : (
          <button
            onClick={() => sendMessage()}
            disabled={!inputValue.trim() && attachedFiles.length === 0}
            className={`p-2.5 rounded-2xl shrink-0 transition-all duration-200 ${
              inputValue.trim() || attachedFiles.length > 0
                ? "bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg shadow-purple-600/30 hover:scale-105 active:scale-95"
                : "bg-white/5 text-zinc-600 cursor-not-allowed"
            }`}
            title="Send message"
            aria-label="Send"
          >
            <Send className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Footer Hint */}
      <div className="flex items-center justify-center text-[10px] text-zinc-400 px-4 mt-2">
        <span className="flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-purple-400" /> Powered by Aura AI
        </span>
      </div>
    </div>
  );
};
