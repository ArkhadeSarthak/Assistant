"use client";

import React, { useState } from "react";
import { Check, Copy, Code2 } from "lucide-react";

interface CodeBlockProps {
  language: string;
  value: string;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ language, value }) => {
  const [copied, setCopied] = useState<boolean>(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative my-4 rounded-xl border border-white/10 bg-zinc-950/80 overflow-hidden shadow-xl backdrop-blur-md">
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-white/5 border-b border-white/10 text-xs font-mono text-zinc-400 select-none">
        <div className="flex items-center gap-2">
          <Code2 className="w-3.5 h-3.5 text-purple-400" />
          <span className="capitalize">{language || "code"}</span>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-white/5 hover:bg-white/10 text-zinc-300 hover:text-white transition-all duration-200 border border-white/5"
          title="Copy code to clipboard"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400 font-medium">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5 text-zinc-400" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Code body */}
      <div className="p-4 overflow-x-auto text-xs font-mono text-zinc-200 leading-relaxed">
        <pre className="m-0 bg-transparent p-0 border-none">
          <code>{value}</code>
        </pre>
      </div>
    </div>
  );
};
