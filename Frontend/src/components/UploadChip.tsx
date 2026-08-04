"use client";

import React, { useState } from "react";
import { FileText, FileCode, FileSpreadsheet, X, Image as ImageIcon, Loader2 } from "lucide-react";
import { FileAttachment } from "@/store/useChatStore";
import { ImageModal } from "./ImageModal";

interface UploadChipProps {
  file: FileAttachment;
  onRemove?: (id: string) => void;
}

export const UploadChip: React.FC<UploadChipProps> = ({ file, onRemove }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [hasImageError, setHasImageError] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const isImage =
    !!file.url ||
    file.type?.toLowerCase().startsWith("image") ||
    /\.(jpg|jpeg|png|webp|gif|bmp)$/i.test(file.name || "") ||
    ["jpg", "jpeg", "png", "webp", "gif", "bmp", "image"].includes((file.type || "").toLowerCase());

  const showLoader = file.isUploading || (!imageLoaded && !hasImageError);

  if (isImage) {
    return (
      <>
        <div className="relative group inline-block shrink-0">
          {/* Skeleton / Spinner Loading empty box fitting exact image size */}
          {showLoader && (
            <div className="w-16 h-16 rounded-2xl bg-purple-950/60 border border-purple-500/30 backdrop-blur-md animate-pulse flex flex-col items-center justify-center gap-1 shadow-lg">
              <Loader2 className="w-5 h-5 text-purple-300 animate-spin" />
              <span className="text-[8px] font-semibold text-purple-200 uppercase tracking-tighter">Uploading</span>
            </div>
          )}

          {/* Real Image Preview */}
          {file.url && (
            <img
              src={file.url}
              alt={file.name}
              onClick={() => setIsModalOpen(true)}
              onLoad={() => setImageLoaded(true)}
              onError={() => setHasImageError(true)}
              title="Click to view full image frame"
              className={`w-16 h-16 object-cover rounded-2xl border border-white/20 shadow-md cursor-pointer transition-all duration-300 hover:scale-105 hover:border-purple-400/60 ${
                !file.isUploading && imageLoaded ? "opacity-100 block" : "opacity-0 absolute inset-0 pointer-events-none"
              }`}
            />
          )}

          {/* Image error fallback if URL is unavailable */}
          {(hasImageError || (!file.url && !file.isUploading)) && (
            <div className="w-16 h-16 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex flex-col items-center justify-center p-1 text-center shadow-md">
              <ImageIcon className="w-5 h-5 text-purple-300 mb-0.5" />
              <span className="text-[9px] text-purple-200 truncate w-full px-1">{file.name}</span>
            </div>
          )}

          {/* Hover Remove Button */}
          {onRemove && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onRemove(file.id);
              }}
              className="absolute -top-1.5 -right-1.5 p-1 bg-red-500/90 hover:bg-red-600 text-white rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10"
              title="Remove image"
              aria-label="Remove image"
            >
              <X className="w-3 h-3" />
            </button>
          )}
        </div>

        {/* Big Frame Image Lightbox Modal */}
        {isModalOpen && file.url && (
          <ImageModal
            imageUrl={file.url}
            altText={file.name}
            onClose={() => setIsModalOpen(false)}
          />
        )}
      </>
    );
  }

  // Non-image document files rendering
  const getIcon = () => {
    switch ((file.type || "").toLowerCase()) {
      case "pdf":
        return <FileText className="w-4 h-4 text-red-400" />;
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
      {file.isUploading ? <Loader2 className="w-4 h-4 text-purple-300 animate-spin" /> : getIcon()}
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
