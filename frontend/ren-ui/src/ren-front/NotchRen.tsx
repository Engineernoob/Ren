"use client";

import { useRef, useState } from "react";
import { type FormEvent } from "react";
import {
  Mic,
  MicOff,
  Loader2,
  AlertTriangle,
  ChevronDown,
  Volume2,
} from "lucide-react";

export type AssistantState =
  | "idle"
  | "listening"
  | "responding"
  | "thinking"
  | "speaking"
  | "error";

export interface NotchRenProps {
  state: AssistantState;
  onStateChange: (s: AssistantState) => void;
  isExpanded: boolean;
  onToggleExpanded: () => void;
}

export function NotchRen({
  state,
  onStateChange,
  isExpanded,
  onToggleExpanded,
}: NotchRenProps) {
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState<
    {
      role: "user" | "assistant";
      content: string;
    }[]
  >([
    { role: "assistant", content: "Good morning! How can I help you today?" },
  ]);

  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  /* Recording helpers */
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream);
      recorderRef.current = rec;
      chunksRef.current = [];

      rec.ondataavailable = (e) =>
        e.data.size && chunksRef.current.push(e.data);
      rec.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: "audio/wav" });
        await sendToBackend(blob);
        stream.getTracks().forEach((t) => t.stop());
      };

      rec.start();
      onStateChange("listening");
    } catch {
      onStateChange("error");
    }
  };
  const stopRecording = () => recorderRef.current?.stop();
  const toggleMic = () =>
    state === "listening" ? stopRecording() : startRecording();

  /* Backend */
  const sendToBackend = async (blob: Blob) => {
    const form = new FormData();
    form.append("file", blob, "recording.wav");
    try {
      onStateChange("responding");
      const res = await fetch("http://localhost:5001/transcribe", {
        method: "POST",
        body: form,
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const { text } = await res.json();

      setMessages((m) => [...m, { role: "user", content: text }]);
      setTimeout(() => {
        setMessages((m) => [
          ...m,
          { role: "assistant", content: "Here’s your response from Ren." },
        ]);
        onStateChange("idle");
      }, 1000);
    } catch {
      onStateChange("error");
    }
  };

  /* Submit typed */
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    setMessages((m) => [...m, { role: "user", content: inputValue }]);
    setInputValue("");
    onStateChange("responding");
    setTimeout(() => {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "Sure – I’ve processed your query." },
      ]);
      onStateChange("idle");
    }, 1000);
  };

  /* State indicator */
  const indicator = (() => {
    switch (state) {
      case "listening":
        return { color: "bg-blue-400", text: "Listening…" };
      case "responding":
        return { color: "bg-green-400", text: "Responding…" };
      case "error":
        return { color: "bg-red-400", text: "Error" };
      default:
        return { color: "bg-white/40", text: "Ready" };
    }
  })();

  return (
    <div className="fixed top-6 left-1/2 -translate-x-1/2 z-50">
      {/* Notch Bar */}
      <div className="notch-bar flex items-center space-x-3">
        <div className={`${indicator.color} w-2 h-2 rounded-full`} />
        <button
          onClick={toggleMic}
          className="p-1.5 rounded-full bg-black/10 hover:bg-black/20"
        >
          {state === "listening" ? (
            <Mic className="w-5 h-5 text-black/80" />
          ) : state === "responding" ? (
            <Loader2 className="w-5 h-5 animate-spin text-black/80" />
          ) : state === "error" ? (
            <AlertTriangle className="w-5 h-5 text-red-500" />
          ) : (
            <MicOff className="w-5 h-5 text-black/80" />
          )}
        </button>
        <form onSubmit={handleSubmit} className="flex-1">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={
              indicator.text === "Ready" ? "Ask Ren anything…" : indicator.text
            }
            disabled={state !== "idle"}
            className="w-full bg-transparent border-none outline-none placeholder-black/50 text-black/90 text-sm"
          />
        </form>
        <button
          onClick={onToggleExpanded}
          className="p-1.5 rounded-full bg-black/10 hover:bg-black/20"
        >
          <ChevronDown
            className={`w-4 h-4 transition-transform ${
              isExpanded ? "rotate-180" : ""
            }`}
          />
        </button>
      </div>

      {/* Expanded Panel */}
      {isExpanded && (
        <div className="expanded-panel">
          {messages.map((m, i) => (
            <div key={i} className={`message ${m.role}`}>
              {m.content}
            </div>
          ))}
          <div className="controls">
            <div className="buttons">
              <button
                onClick={toggleMic}
                className="p-2 rounded-lg bg-black/10 hover:bg-black/20"
              >
                {state === "listening" ? (
                  <Mic className="w-5 h-5" />
                ) : (
                  <MicOff className="w-5 h-5" />
                )}
              </button>
              <button className="p-2 rounded-lg bg-black/10 hover:bg-black/20">
                <Volume2 className="w-5 h-5" />
              </button>
            </div>
            <div className="text-xs text-black/70">
              {messages.length} messages
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
