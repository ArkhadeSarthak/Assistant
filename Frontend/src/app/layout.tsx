import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "AURA AI",
  description: "A modern, high-end, minimal single-page AI Assistant interface with interactive voice mode, tool execution status, reasoning steps, and file uploads.",
  keywords: ["AI Assistant", "ChatGPT alternative", "Voice AI", "Minimal UI", "Glassmorphism"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jetbrainsMono.variable} dark h-full antialiased selection:bg-purple-500/30 selection:text-purple-200`}
    >
      <body className="h-full bg-[#09090B] text-zinc-100 font-sans flex flex-col overflow-hidden relative">
        {children}
      </body>
    </html>
  );
}
