"use client";

import React, { useEffect, useState, useRef, useCallback } from "react";
import { Mic, MicOff, Square, Radio, Loader2 } from "lucide-react";
import { useChatStore } from "@/store/useChatStore";
import { processVoiceService, playStreamingTtsAudio } from "@/services/voice";
import { motion } from "framer-motion";

const UNLISTENABLE_FALLBACK_TEXT = "I couldn't hear or understand that clearly. Please try speaking a bit louder.";

export const VoicePanel: React.FC = () => {
  const {
    setVoiceMode,
    voiceState,
    setVoiceState,
    voiceTimer,
    incrementVoiceTimer,
    resetVoiceTimer,
    sendMessage
  } = useChatStore();

  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcriptText, setTranscriptText] = useState("Listening for voice... Speak or click mic button");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [barHeights, setBarHeights] = useState<number[]>([8, 12, 8, 16, 8]);

  const isMountedRef = useRef<boolean>(true);

  const mediaStreamRef = useRef<MediaStream | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const currentAudioRef = useRef<{ stop: () => void } | null>(null);

  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animFrameRef = useRef<number | null>(null);

  const isRecordingRef = useRef<boolean>(false);
  const hasUserSpokenRef = useRef<boolean>(false);
  const silenceStartRef = useRef<number | null>(null);
  const stopTriggeredRef = useRef<boolean>(false);

  // Timer interval effect
  useEffect(() => {
    const interval = setInterval(() => {
      incrementVoiceTimer();
    }, 1000);
    return () => clearInterval(interval);
  }, [incrementVoiceTimer]);

  const cleanupAudioNodes = useCallback(() => {
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== "closed") {
      audioContextRef.current.close().catch(() => {});
      audioContextRef.current = null;
    }
    analyserRef.current = null;
  }, []);

  const cleanupAllStreams = useCallback(() => {
    isMountedRef.current = false;
    cleanupAudioNodes();

    if (mediaRecorderRef.current) {
      if (mediaRecorderRef.current.stream) {
        mediaRecorderRef.current.stream.getTracks().forEach((track) => {
          track.enabled = false;
          track.stop();
        });
      }
      if (mediaRecorderRef.current.state !== "inactive") {
        try {
          mediaRecorderRef.current.stop();
        } catch (e) {}
      }
      mediaRecorderRef.current = null;
    }

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => {
        track.enabled = false;
        track.stop();
      });
      mediaStreamRef.current = null;
    }

    if (currentAudioRef.current) {
      currentAudioRef.current.stop();
      currentAudioRef.current = null;
    }

    isRecordingRef.current = false;
    setIsRecording(false);
  }, [cleanupAudioNodes]);

  // Clean up audio & recorder on unmount
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
      cleanupAllStreams();
    };
  }, [cleanupAllStreams]);

  const startActiveRecording = useCallback(() => {
    if (!isMountedRef.current || isRecordingRef.current) return;

    audioChunksRef.current = [];
    hasUserSpokenRef.current = true;
    silenceStartRef.current = null;
    stopTriggeredRef.current = false;
    isRecordingRef.current = true;
    setIsRecording(true);
    setVoiceState("listening");
    setTranscriptText("Listening... Speak now");

    if (mediaStreamRef.current) {
      try {
        const mediaRecorder = new MediaRecorder(mediaStreamRef.current);
        mediaRecorderRef.current = mediaRecorder;

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        mediaRecorder.start();
      } catch (e) {
        console.error("MediaRecorder start error:", e);
      }
    }
  }, [setVoiceState]);

  const stopActiveRecordingAndTranscribe = useCallback(async () => {
    if (stopTriggeredRef.current || !isRecordingRef.current) return;
    stopTriggeredRef.current = true;
    isRecordingRef.current = false;
    setIsRecording(false);

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      setIsProcessing(true);
      setVoiceState("speaking");
      setTranscriptText("Transcribing audio with Deepgram Nova-3...");

      mediaRecorderRef.current.onstop = async () => {
        if (!isMountedRef.current) return;
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });

        const handleFallbackSpeech = () => {
          if (!isMountedRef.current) return;
          setTranscriptText(UNLISTENABLE_FALLBACK_TEXT);
          currentAudioRef.current = playStreamingTtsAudio(UNLISTENABLE_FALLBACK_TEXT, "Aarav", {
            onEnded: () => {
              if (!isMountedRef.current) return;
              setVoiceState("idle");
              setTranscriptText("Listening for voice... Speak or click mic button");
              startBackgroundListener();
            },
            onError: () => {
              if (!isMountedRef.current) return;
              setVoiceState("idle");
              setTranscriptText("Listening for voice... Speak or click mic button");
              startBackgroundListener();
            }
          });
        };

        if (audioBlob.size === 0) {
          setIsProcessing(false);
          handleFallbackSpeech();
          return;
        }

        try {
          const result = await processVoiceService(audioBlob);
          if (!isMountedRef.current) return;
          const text = result?.transcription;

          if (text && text.trim()) {
            setTranscriptText(text);
            await sendMessage(text);
            if (!isMountedRef.current) return;
            const lastMsg = useChatStore.getState().messages.slice(-1)[0];
            const responseText = lastMsg?.role === "assistant" ? lastMsg.content : "Received!";

            currentAudioRef.current = playStreamingTtsAudio(responseText, "Aarav", {
              onEnded: () => {
                if (!isMountedRef.current) return;
                setVoiceState("idle");
                setTranscriptText("Listening for voice... Speak or click mic button");
                startBackgroundListener();
              },
              onError: () => {
                if (!isMountedRef.current) return;
                setVoiceState("idle");
                setTranscriptText("Listening for voice... Speak or click mic button");
                startBackgroundListener();
              }
            });
          } else {
            handleFallbackSpeech();
          }
        } catch (err: any) {
          console.error("STT transcription error:", err);
          if (!isMountedRef.current) return;
          setErrorMessage("Speech-to-Text transcription error.");
          handleFallbackSpeech();
        } finally {
          if (isMountedRef.current) {
            setIsProcessing(false);
          }
        }
      };

      try {
        mediaRecorderRef.current.stop();
      } catch (e) {
        setIsProcessing(false);
      }
    }
  }, [sendMessage, setVoiceState]);

  const startBackgroundListener = useCallback(async () => {
    try {
      if (!isMountedRef.current) return;

      if (currentAudioRef.current) {
        currentAudioRef.current.stop();
      }
      cleanupAudioNodes();
      setErrorMessage(null);
      stopTriggeredRef.current = false;
      hasUserSpokenRef.current = false;
      silenceStartRef.current = null;
      isRecordingRef.current = false;
      setIsRecording(false);

      if (!mediaStreamRef.current || !mediaStreamRef.current.active) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // RACE CONDITION SAFETY GUARD: If user exited Voice Mode while getUserMedia was resolving!
        if (!isMountedRef.current) {
          stream.getTracks().forEach((track) => {
            track.enabled = false;
            track.stop();
          });
          return;
        }

        mediaStreamRef.current = stream;
      }

      if (!isMountedRef.current) return;

      // Set up Web Audio API Volume Intensity Analyzer for speech trigger
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      const audioContext = new AudioCtx();
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 64;
      const source = audioContext.createMediaStreamSource(mediaStreamRef.current);
      source.connect(analyser);

      audioContextRef.current = audioContext;
      analyserRef.current = analyser;

      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      const analyze = () => {
        if (!isMountedRef.current || !analyserRef.current) return;
        analyserRef.current.getByteFrequencyData(dataArray);

        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i];
        }
        const avg = sum / dataArray.length; // 0 to 255
        const normVol = Math.min(1.0, avg / 120);

        // Compute 5 dynamic bar heights matching audio intensity
        const b1 = Math.max(8, ((dataArray[1] || 0) / 255) * 44);
        const b2 = Math.max(8, ((dataArray[3] || 0) / 255) * 52);
        const b3 = Math.max(8, ((dataArray[5] || 0) / 255) * 60);
        const b4 = Math.max(8, ((dataArray[7] || 0) / 255) * 52);
        const b5 = Math.max(8, ((dataArray[9] || 0) / 255) * 44);
        setBarHeights([b1, b2, b3, b4, b5]);

        const SPEECH_THRESHOLD = 0.06;
        const SILENCE_THRESHOLD = 0.03;

        // Auto start recording when user starts speaking
        if (normVol > SPEECH_THRESHOLD && !isRecordingRef.current) {
          startActiveRecording();
        }

        // When recording actively and user pauses speaking for 3 seconds -> auto stop & transcribe
        if (isRecordingRef.current) {
          if (normVol > SPEECH_THRESHOLD) {
            silenceStartRef.current = null;
          } else if (normVol <= SILENCE_THRESHOLD) {
            if (!silenceStartRef.current) {
              silenceStartRef.current = Date.now();
            } else {
              const elapsed = (Date.now() - silenceStartRef.current) / 1000;
              if (elapsed >= 3.0) {
                stopActiveRecordingAndTranscribe();
                return;
              }
            }
          }
        }

        if (isMountedRef.current) {
          animFrameRef.current = requestAnimationFrame(analyze);
        }
      };

      animFrameRef.current = requestAnimationFrame(analyze);
      setVoiceState("idle");
    } catch (err: any) {
      console.error("Microphone access error:", err);
      if (isMountedRef.current) {
        setErrorMessage("Could not access microphone. Please check browser permissions.");
      }
    }
  }, [cleanupAudioNodes, setVoiceState, startActiveRecording, stopActiveRecordingAndTranscribe]);

  // Auto start background audio listener on component mount
  useEffect(() => {
    isMountedRef.current = true;
    startBackgroundListener();
    // eslint-disable-next-line react-hooks.exhaustive-deps
  }, []);

  const toggleMic = () => {
    if (isProcessing) return;
    if (isRecordingRef.current) {
      stopActiveRecordingAndTranscribe();
    } else {
      startActiveRecording();
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
            {isProcessing
              ? "Transcribing STT..."
              : isRecording
              ? "Recording..."
              : voiceState === "speaking"
              ? "Aura Speaking..."
              : "Voice Mode Ready"}
          </span>
        </div>
        <div className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-mono text-zinc-300">
          {formatTimer(voiceTimer)}
        </div>
      </div>

      {/* Large Glowing Mic Button */}
      <div className="relative my-6 flex items-center justify-center z-10 cursor-pointer" onClick={toggleMic}>
        {/* Outer Circular Ripples */}
        {isRecording && (
          <>
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
          </>
        )}

        {/* Core Glowing Button */}
        <div
          className={`relative w-28 h-28 rounded-full p-[2px] shadow-2xl transition-all duration-300 ${
            isRecording
              ? "bg-gradient-to-tr from-red-500 via-purple-600 to-pink-500 shadow-red-500/50"
              : isProcessing
              ? "bg-gradient-to-tr from-blue-500 via-indigo-600 to-purple-500 shadow-indigo-500/50"
              : "bg-gradient-to-tr from-purple-600 via-indigo-600 to-blue-500 shadow-purple-600/40"
          }`}
        >
          <div className="w-full h-full rounded-full bg-zinc-950 flex items-center justify-center backdrop-blur-xl group hover:bg-zinc-900 transition-colors">
            {isProcessing ? (
              <Loader2 className="w-12 h-12 text-indigo-300 animate-spin" />
            ) : isRecording ? (
              <MicOff className="w-12 h-12 text-red-400 animate-pulse" />
            ) : (
              <Mic className="w-12 h-12 text-purple-300" />
            )}
          </div>
        </div>
      </div>

      {/* Dynamic Sound Waves Equalizer Bars matching Audio Volume Intensity */}
      <div className="flex items-center justify-center gap-1.5 h-16 my-4 z-10">
        <div
          style={{ height: `${barHeights[0]}px` }}
          className="w-2 rounded-full bg-purple-500 transition-all duration-75 shadow-lg shadow-purple-500/30"
        />
        <div
          style={{ height: `${barHeights[1]}px` }}
          className="w-2 rounded-full bg-indigo-500 transition-all duration-75 shadow-lg shadow-indigo-500/30"
        />
        <div
          style={{ height: `${barHeights[2]}px` }}
          className="w-2 rounded-full bg-blue-500 transition-all duration-75 shadow-lg shadow-blue-500/30"
        />
        <div
          style={{ height: `${barHeights[3]}px` }}
          className="w-2 rounded-full bg-emerald-500 transition-all duration-75 shadow-lg shadow-emerald-500/30"
        />
        <div
          style={{ height: `${barHeights[4]}px` }}
          className="w-2 rounded-full bg-purple-500 transition-all duration-75 shadow-lg shadow-purple-500/30"
        />
      </div>

      {/* Transcript Text */}
      <div className="w-full text-center px-6 my-2 z-10 min-h-[44px] flex flex-col items-center justify-center">
        <p className="text-sm font-medium text-zinc-200 italic">
          "{transcriptText}"
        </p>
        {errorMessage && <p className="text-xs text-red-400 mt-1 font-sans">{errorMessage}</p>}
      </div>

      {/* Controls: Exit Voice Mode Button */}
      <div className="mt-6 flex items-center gap-4 z-10">
        <button
          onClick={() => {
            cleanupAllStreams();
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
