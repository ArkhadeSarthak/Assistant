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

export async function fetchTtsAudio(text: string, voiceId: string = "Aarav"): Promise<Blob> {
  const BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/+$/, "");
  const token = typeof window !== "undefined" ? localStorage.getItem("aura_token") : null;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}/tts`, {
    method: "POST",
    headers,
    body: JSON.stringify({ text, voice_id: voiceId }),
  });

  if (!response.ok) {
    throw new Error(`TTS synthesis request failed with status ${response.status}`);
  }

  return await response.blob();
}

export function playStreamingTtsAudio(
  text: string,
  voiceId: string = "Aarav",
  callbacks: {
    onStartPlaying?: () => void;
    onEnded?: () => void;
    onError?: (err: any) => void;
  } = {}
): { audio: HTMLAudioElement; stop: () => void } {
  const BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/+$/, "");
  const token = typeof window !== "undefined" ? localStorage.getItem("aura_token") : null;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const audio = new Audio();
  let stopped = false;

  const stop = () => {
    stopped = true;
    audio.pause();
    audio.currentTime = 0;
  };

  audio.onended = () => {
    if (!stopped) {
      callbacks.onEnded?.();
    }
  };

  audio.onerror = (e) => {
    if (!stopped) {
      callbacks.onError?.(e);
    }
  };

  async function fallbackFetch() {
    try {
      const response = await fetch(`${BASE_URL}/tts`, {
        method: "POST",
        headers,
        body: JSON.stringify({ text, voice_id: voiceId }),
      });
      if (!response.ok) throw new Error(`TTS error ${response.status}`);
      const blob = await response.blob();
      if (stopped) return;
      audio.src = URL.createObjectURL(blob);
      await audio.play();
      callbacks.onStartPlaying?.();
    } catch (err) {
      if (!stopped) callbacks.onError?.(err);
    }
  }

  if (typeof MediaSource !== "undefined" && MediaSource.isTypeSupported("audio/mpeg")) {
    const mediaSource = new MediaSource();
    audio.src = URL.createObjectURL(mediaSource);

    mediaSource.addEventListener("sourceopen", async () => {
      let sourceBuffer: SourceBuffer;
      try {
        sourceBuffer = mediaSource.addSourceBuffer("audio/mpeg");
      } catch (err) {
        fallbackFetch();
        return;
      }

      try {
        const response = await fetch(`${BASE_URL}/tts`, {
          method: "POST",
          headers,
          body: JSON.stringify({ text, voice_id: voiceId }),
        });

        if (!response.ok || !response.body) {
          throw new Error(`TTS HTTP error ${response.status}`);
        }

        const reader = response.body.getReader();
        const queue: Uint8Array[] = [];
        let isEnded = false;

        const appendNext = () => {
          if (stopped) return;
          if (queue.length > 0 && !sourceBuffer.updating) {
            const chunk = queue.shift()!;
            try {
              sourceBuffer.appendBuffer(chunk as unknown as BufferSource);
            } catch (e) {
              console.warn("SourceBuffer append warning:", e);
            }
          }
        };

        sourceBuffer.addEventListener("updateend", () => {
          if (stopped) return;
          appendNext();
          if (queue.length === 0 && isEnded && !sourceBuffer.updating) {
            try {
              if (mediaSource.readyState === "open") {
                mediaSource.endOfStream();
              }
            } catch (e) {}
          }
        });

        let hasStartedPlayback = false;

        while (!stopped) {
          const { done, value } = await reader.read();
          if (done) {
            isEnded = true;
            if (queue.length === 0 && !sourceBuffer.updating) {
              try {
                if (mediaSource.readyState === "open") {
                  mediaSource.endOfStream();
                }
              } catch (e) {}
            }
            break;
          }

          if (value && value.length > 0) {
            queue.push(value);
            appendNext();

            if (!hasStartedPlayback && !stopped) {
              hasStartedPlayback = true;
              audio.play().then(() => {
                callbacks.onStartPlaying?.();
              }).catch(err => {
                console.error("Audio play error:", err);
              });
            }
          }
        }
      } catch (err) {
        if (!stopped) {
          callbacks.onError?.(err);
        }
      }
    });
  } else {
    fallbackFetch();
  }

  return { audio, stop };
}
