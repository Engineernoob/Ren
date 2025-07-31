"use client";

import { useState, useRef } from "react";
import {
  Mic,
  MicOff,
  Volume2,
  MessageCircle,
  X,
  History,
  AlertTriangle,
} from "lucide-react";

export type AssistantState = "idle" | "listening" | "thinking" | "speaking";

interface FloatingAssistantProps {
  variant?: "default" | "minimal" | "premium";
  state: AssistantState;
  isExpanded: boolean;
  onStateChange: (s: AssistantState) => void;
  onToggleExpanded: () => void;
}

export function FloatingAssistant({
  variant = "default",
  state,
  isExpanded,
  onStateChange,
  onToggleExpanded,
}: FloatingAssistantProps) {
  /* local only */
  const [inputValue, setInputValue] = useState("");
  const [isVoiceOnly, setIsVoiceOnly] = useState(false);
  const [messages, setMessages] = useState<
    { role: "user" | "assistant"; content: string }[]
  >([
    {
      role: "assistant",
      content: "Hello! I'm Ren, your AI assistant. How can I help you today?",
    },
  ]);

  const inputRef = useRef<HTMLInputElement>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  /* ────────── Media-Recorder helpers ────────── */
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream);
      recorderRef.current = rec;
      chunksRef.current = [];

      rec.ondataavailable = (e) =>
        e.data.size && chunksRef.current.push(e.data);
      rec.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        uploadAudio(new Blob(chunksRef.current, { type: "audio/wav" }));
      };

      rec.start();
      onStateChange("listening");
    } catch (err) {
      console.error("Mic access error:", err);
    }
  };

  const stopRecording = () => recorderRef.current?.stop();

  /* ────────── Whisper backend ────────── */
  const uploadAudio = async (blob: Blob) => {
    const fd = new FormData();
    fd.append("file", blob, "recording.wav"); // Flask expects 'file'
    try {
      onStateChange("thinking");
      const res = await fetch("http://localhost:5001/transcribe", {
        method: "POST",
        body: fd,
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const { text } = await res.json(); // returns { text: "..." }

      setMessages((m) => [...m, { role: "user", content: text }]);
      /* ⬇️ TODO: call your LLM -> reply */
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: "I’ve received your request. (LLM reply goes here)",
        },
      ]);
      onStateChange("idle");
    } catch (err) {
      console.error("Whisper backend error:", err);
    }
  };

  /* ────────── UI helpers ────────── */
  const handleToggleListening = () => {
    state === "listening" ? stopRecording() : startRecording();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    setMessages((prev) => [...prev, { role: "user", content: inputValue }]);
    setInputValue("");
    onStateChange("thinking");

    /* fake AI reply */
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sure — here's a stubbed response." },
      ]);
      onStateChange("idle");
    }, 1500);
  };

  const indicator = (() => {
    switch (state) {
      case "listening":
        return { text: "Listening…", color: "text-blue-400" };
      case "thinking":
        return { text: "Thinking…", color: "text-amber-400" };
      case "speaking":
        return { text: "Speaking…", color: "text-green-400" };
      default:
        return { text: "Ready", color: "text-slate-400" };
    }
  })();

  const variantStyles = {
    default: {
      container: "bg-white/20 border-white/30",
      input: "bg-white/10 border-white/20",
      button: "bg-white/20 hover:bg-white/30",
    },
    minimal: {
      container: "bg-white/10 border-white/20",
      input: "bg-white/5  border-white/10",
      button: "bg-white/10 hover:bg-white/20",
    },
    premium: {
      container: "bg-slate-900/40 border-slate-700/30",
      input: "bg-slate-800/30 border-slate-600/20",
      button: "bg-slate-700/30 hover:bg-slate-600/40",
    },
  }[variant];

  /* ────────── JSX ────────── */
  return (
    <div className="fixed top-8 left-1/2 -translate-x-1/2 z-50">
      <div
        className={`relative backdrop-blur-xl ${variantStyles.container}
          border rounded-3xl shadow-2xl transition-all duration-500 ease-out
          ${isExpanded ? "w-96" : "w-80"}`}
      >
        {/* Header */}
        <div className="p-4 pb-0 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${indicator.color}`} />
            <span className={`text-sm ${indicator.color}`}>
              {indicator.text}
            </span>
            && (
            <AlertTriangle className="w-4 h-4 text-red-400" />){"}"}
          </div>

          <button
            onClick={onToggleExpanded}
            className={`p-1.5 rounded-lg ${variantStyles.button} transition`}
          >
            {isExpanded ? (
              <X className="w-4 h-4" />
            ) : (
              <History className="w-4 h-4" />
            )}
          </button>
        </div>

        {/* Text input (disabled while thinking) */}
        {!isVoiceOnly && (
          <form onSubmit={handleSubmit} className="p-4 pb-0">
            <div className="relative">
              <input
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask Ren anything..."
                className={`w-full px-4 py-2.5 ${variantStyles.input}
                  border rounded-2xl placeholder-white/50 text-white bg-transparent
                  focus:outline-none focus:ring-2 focus:ring-blue-400/50`}
                disabled={state === "thinking"}
              />
              {state === "thinking" && (
                <div className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 border-2 border-white/20 border-t-white/60 rounded-full animate-spin" />
              )}
            </div>
          </form>
        )}

        {/* Control buttons */}
        <div className="p-4 flex items-center justify-between">
          <div className="flex gap-2">
            <button
              onClick={handleToggleListening}
              className={`p-2.5 rounded-xl transition ${
                state === "listening"
                  ? "bg-blue-500/80 text-white"
                  : `${variantStyles.button} text-white/70 hover:text-white`
              }`}
              title={state === "listening" ? "Stop" : "Start voice"}
            >
              {state === "listening" ? (
                <Mic className="w-4 h-4" />
              ) : (
                <MicOff className="w-4 h-4" />
              )}
            </button>

            <button
              onClick={() => setIsVoiceOnly((v) => !v)}
              className={`p-2.5 rounded-xl ${variantStyles.button} transition text-white/70 hover:text-white`}
              title="Toggle voice-only"
            >
              <MessageCircle className="w-4 h-4" />
            </button>
          </div>

          <button
            className={`p-2.5 rounded-xl ${variantStyles.button} transition text-white/70 hover:text-white`}
            title="Speaker"
          >
            <Volume2 className="w-4 h-4" />
          </button>
        </div>

        {/* Expanded history */}
        {isExpanded && (
          <div className="border-t border-white/20 p-4 max-h-64 overflow-y-auto">
            <div className="space-y-3 text-sm">
              {messages.map((m, i) => (
                <div
                  key={i}
                  className={`flex ${m.role === "user" ? "justify-end" : ""}`}
                >
                  <div
                    className={`px-3 py-2 rounded-xl max-w-[80%] ${
                      m.role === "user"
                        ? "bg-blue-500/20 border border-blue-400/30 text-white/90"
                        : "bg-white/10 border border-white/20 text-white/70"
                    }`}
                  >
                    {m.content}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Voice-only overlay */}
      {isVoiceOnly && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div
              className={`w-16 h-16 rounded-full ${variantStyles.container} border flex items-center justify-center mb-2`}
            >
              <Mic className="w-8 h-8 text-white/80" />
            </div>
            <p className="text-white/60 text-sm">Voice mode active</p>
          </div>
        </div>
      )}
    </div>
  );
}
