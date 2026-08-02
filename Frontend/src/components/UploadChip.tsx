"use client";

import React from "react";
import { FileText, Image as ImageIcon, FileCode, FileSpreadsheet, X } from "lucide-react";
import { FileAttachment } from "@/store/useChatStore";

interface UploadChipProps {
  file: FileAttachment;
  onRemove?: (id: string) => void;
}

export const UploadChip: React.FC<UploadChipProps> = ({ file, onRemove }) => {
  const getIcon = () => {
    switch (file.type.toLowerCase()) {
      case "pdf":
        return <FileText className="w-4 h-4 text-red-400" />;
      case "image":
      case "png":
      case "jpg":
      case "jpeg":
        return <ImageIcon className="w-4 h-4 text-blue-400" />;
      case "excel":
      case "csv":
      case "xlsx":
        return <FileSpreadsheet className="w-4 h-4 text-emerald-400" />;
      default:
        return <FileCode className="w-4 h-4 text-purple-400" />;
    }
  };

  return (
    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs font-medium text-zinc-200 backdrop-blur-md shadow-sm transition-all hover:bg-white/10 group">
      {getIcon()}
      <span className="max-w-[140px] truncate">{file.name}</span>
      <span className="text-[10px] text-zinc-400">({file.size})</span>
      {onRemove && (
        <button
          onClick={() => onRemove(file.id)}
          className="text-zinc-400 hover:text-red-400 transition-colors p-0.5 rounded-md hover:bg-white/10 ml-1"
          aria-label="Remove file"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
};
