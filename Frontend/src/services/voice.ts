import { apiFetch } from "./api";

export async function processVoiceService(audioBlob?: Blob, textPrompt?: string): Promise<any> {
  const formData = new FormData();
  if (audioBlob) {
    formData.append("audio_file", audioBlob, "recording.wav");
  }
  if (textPrompt) {
    formData.append("text", textPrompt);
  }

  const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const token = typeof window !== "undefined" ? localStorage.getItem("aura_token") : null;
  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}/voice`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Voice service error ${response.status}`);
  }

  return await response.json();
}
