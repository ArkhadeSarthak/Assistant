"use client";

import React, { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { X, ExternalLink } from "lucide-react";

interface ImageModalProps {
  imageUrl: string;
  altText?: string;
  onClose: () => void;
}

export const ImageModal: React.FC<ImageModalProps> = ({ imageUrl, altText = "Image view", onClose }) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [onClose]);

  if (!mounted || typeof document === "undefined") {
    return null;
  }

  const modalContent = (
    <div
      onClick={onClose}
      className="fixed inset-0 z-[99999] flex items-center justify-center bg-black/90 backdrop-blur-2xl p-4 md:p-8 animate-in fade-in duration-200 select-none"
    >
      {/* Top action controls bar */}
      <div className="fixed top-6 right-6 flex items-center gap-3 z-[100000]">
        <a
          href={imageUrl}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          className="p-3 rounded-full bg-white/10 hover:bg-white/20 text-white transition-all shadow-2xl backdrop-blur-xl border border-white/10 flex items-center justify-center hover:scale-105 active:scale-95"
          title="Open original image in new tab"
        >
          <ExternalLink className="w-5 h-5" />
        </a>
        <button
          onClick={onClose}
          className="p-3 rounded-full bg-white/10 hover:bg-white/20 text-white transition-all shadow-2xl backdrop-blur-xl border border-white/10 flex items-center justify-center hover:scale-105 active:scale-95"
          aria-label="Close image preview"
          title="Close preview (Esc)"
        >
          <X className="w-6 h-6" />
        </button>
      </div>

      {/* Main Big Frame Container */}
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative max-w-[90vw] max-h-[85vh] rounded-3xl border border-white/20 bg-zinc-950/90 shadow-2xl flex items-center justify-center p-3 md:p-4 overflow-hidden backdrop-blur-3xl animate-in zoom-in-95 duration-200"
      >
        <img
          src={imageUrl}
          alt={altText}
          className="max-w-[85vw] max-h-[80vh] object-contain rounded-2xl shadow-2xl select-none"
        />
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};
