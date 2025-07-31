"use client";

import { useState, useRef } from "react";
import { Mic, MicOff, Loader2, AlertTriangle, ChevronDown } from "lucide-react";

type AssistantState = "idle" | "listening" | "responding" | "error";

export function NotchRen() {
  const [state, setState] = useState<AssistantState>("idle");
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState("");
  const [isExpanded, setIsExpanded] = useState(false);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  /* ---------- Recording helpers ---------- */
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);

      recorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: "audio/wav" });
        await sendToBackend(audioBlob);
        stream.getTracks().forEach((t) => t.stop()); // close mic
      };

      mediaRecorder.start();
      setState("listening");
    } catch (err) {
      console.error("Mic access error:", err);
      setState("error");
    }
  };

  const stopRecording = () => {
    recorderRef.current?.stop();
  };

  /* ---------- Backend call ---------- */
  const sendToBackend = async (blob: Blob) => {
    const formData = new FormData();
    formData.append("audio", blob, "recording.wav");

    try {
      setState("responding");
      const res = await fetch("http://localhost:5001/transcribe", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json(); // { transcript: "...", response: "..." }
      setTranscript(data.transcript);
      setResponse(data.response);
      setState("idle");
    } catch (err) {
      console.error("Whisper backend error:", err);
      setState("error");
    }
  };

  /* ---------- UI helpers ---------- */
  const handleMicClick = () => {
    if (state === "listening") stopRecording();
    else startRecording();
  };

  const icon = () => {
    switch (state) {
      case "listening":
      case "responding":
        return <Loader2 className="w-5 h-5 animate-spin" />;
      case "error":
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      default:
        return state === "idle" ? (
          <Mic className="w-5 h-5" />
        ) : (
          <MicOff className="w-5 h-5" />
        );
    }
  };

  return (
    <div className="fixed top-6 left-1/2 -translate-x-1/2 z-50">
      {/* ░▒▓ Notch Bar ▓▒░ */}
      <div className="notch-bar flex items-center gap-3">
        <button onClick={handleMicClick} className="p-1.5 rounded-lg">
          {icon()}
        </button>

        <span className="text-sm opacity-70 select-none">
          {state === "listening"
            ? "Listening..."
            : state === "responding"
            ? "Transcribing..."
            : state === "error"
            ? "Error - try again"
            : "Ask Ren anything..."}
        </span>

        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="ml-auto p-1.5 rounded-lg hover:bg-white/10"
        >
          <ChevronDown
            className={`w-4 h-4 transition-transform ${
              isExpanded ? "rotate-180" : ""
            }`}
          />
        </button>
      </div>

      {/* ░▒▓ Expanded Panel ▓▒░ */}
      {isExpanded && (
        <div className="mt-3 max-w-sm p-4 rounded-lg bg-white/10 backdrop-blur-lg">
          <h4 className="mb-2 text-sm font-semibold text-white/90">
            Latest Conversation
          </h4>

          <div className="text-xs text-white/80 space-y-1">
            {transcript && (
              <p>
                <span className="font-medium text-blue-300">You:</span>{" "}
                {transcript}
              </p>
            )}

            {response && (
              <p>
                <span className="font-medium text-green-300">Ren:</span>{" "}
                {response}
              </p>
            )}

            {!transcript && !response && (
              <p className="italic text-white/60">No messages yet.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
