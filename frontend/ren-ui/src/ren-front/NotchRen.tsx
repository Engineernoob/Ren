"use client";

import React, { useState, useRef, useEffect } from "react";
import { Mic, MicOff, Volume2, VolumeX, ChevronDown, Wifi } from "lucide-react";

type RenState = "idle" | "listening" | "responding" | "error";

interface NotchRenProps {
  state?: RenState;
  isDarkMode?: boolean;
  isHandoffActive?: boolean;
  onStateChange?: (state: RenState) => void;
  onToggleExpanded?: () => void;
  isExpanded?: boolean;
}

export function NotchRen({
  state = "idle",
  isDarkMode = false,
  isHandoffActive = false,
  onStateChange,
  onToggleExpanded,
  isExpanded = false,
}: NotchRenProps) {
  const [inputValue, setInputValue] = useState("");
  const [isSpeechEnabled, setIsSpeechEnabled] = useState(true);
  const [currentResponse, setCurrentResponse] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [conversations, setConversations] = useState([
    {
      role: "assistant",
      content: "Good morning! How can I help you today?",
      timestamp: new Date(),
    },
    {
      role: "user",
      content: "What's on my calendar?",
      timestamp: new Date(),
    },
    {
      role: "assistant",
      content:
        "You have a team meeting at 2 PM and a design review at 4 PM today.",
      timestamp: new Date(),
    },
  ]);

  const inputRef = useRef<HTMLInputElement>(null);
  const waveformRef = useRef<HTMLDivElement>(null);

  // Typing animation for responses
  useEffect(() => {
    if (state === "responding" && currentResponse) {
      setIsTyping(true);
      const timer = setTimeout(() => setIsTyping(false), 2000);
      return () => clearTimeout(timer);
    }
  }, [state, currentResponse]);

  // Waveform animation
  useEffect(() => {
    if (state === "listening" && waveformRef.current) {
      const bars = waveformRef.current.children;
      const animateWaveform = () => {
        Array.from(bars).forEach((bar, index) => {
          const element = bar as HTMLElement;
          const height = Math.random() * 12 + 4;
          element.style.height = `${height}px`;
          element.style.animationDelay = `${index * 100}ms`;
        });
      };

      const interval = setInterval(animateWaveform, 150);
      return () => clearInterval(interval);
    }
  }, [state]);

  const handleToggleListening = () => {
    const newState = state === "listening" ? "idle" : "listening";
    onStateChange?.(newState);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && state !== "responding") {
      setConversations((prev) => [
        ...prev,
        {
          role: "user",
          content: inputValue,
          timestamp: new Date(),
        },
      ]);
      setCurrentResponse(
        "I understand your request. Let me help you with that..."
      );
      setInputValue("");
      onStateChange?.("responding");

      setTimeout(() => {
        setConversations((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "I understand your request. Let me help you with that...",
            timestamp: new Date(),
          },
        ]);
        setCurrentResponse("");
        onStateChange?.("idle");
      }, 3000);
    }
  };

  const getStateStyles = () => {
    const baseStyles = isDarkMode
      ? "bg-black/30 backdrop-blur-2xl border-white/10"
      : "bg-white/30 backdrop-blur-2xl border-white/20";

    switch (state) {
      case "listening":
        return `${baseStyles} shadow-2xl shadow-blue-500/25 ring-1 ring-blue-400/40`;
      case "responding":
        return `${baseStyles} shadow-2xl shadow-green-500/25 ring-1 ring-green-400/40`;
      case "error":
        return `${baseStyles} shadow-2xl shadow-red-500/25 ring-1 ring-red-400/40`;
      default:
        return `${baseStyles} shadow-2xl shadow-black/15`;
    }
  };

  const getStateIndicator = () => {
    switch (state) {
      case "listening":
        return { color: "bg-blue-400", pulse: true };
      case "responding":
        return { color: "bg-green-400", pulse: true };
      case "error":
        return { color: "bg-red-400", pulse: true };
      default:
        return {
          color: isDarkMode ? "bg-white/40" : "bg-slate-400",
          pulse: false,
        };
    }
  };

  const stateIndicator = getStateIndicator();
  const textColor = isDarkMode ? "text-white" : "text-slate-900";
  const placeholderColor = isDarkMode
    ? "placeholder-white/60"
    : "placeholder-slate-500";

  return (
    <div className="fixed top-0 left-1/2 transform -translate-x-1/2 z-50">
      {/* MacBook Notch Simulation */}
      <div className="w-48 h-8 bg-black rounded-b-2xl" />

      {/* Background Fade Gradient */}
      <div className="absolute top-8 left-1/2 transform -translate-x-1/2 w-96 h-16 pointer-events-none">
        <div
          className={`
          w-full h-full 
          ${
            isDarkMode
              ? "bg-gradient-to-b from-black/40 via-black/20 to-transparent"
              : "bg-gradient-to-b from-black/20 via-black/10 to-transparent"
          }
        `}
        />
      </div>

      {/* Main Ren Bar with Enhanced Design */}
      <div className="relative mt-0">
        {/* Notch Integration Shadow */}
        <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 w-52 h-4 bg-black/50 blur-lg rounded-b-3xl" />

        <div
          className={`
            relative transition-all duration-500 ease-out border
            ${getStateStyles()}
            ${isExpanded ? "w-96 h-auto" : "w-80 h-12"}
          `}
          style={{
            // Concave top curve that echoes the notch
            clipPath: isExpanded
              ? "polygon(0 8px, 35% 8px, 40% 0, 60% 0, 65% 8px, 100% 8px, 100% 100%, 0 100%)"
              : "polygon(0 8px, 35% 8px, 40% 0, 60% 0, 65% 8px, 100% 8px, 100% 100%, 0 100%)",
            borderRadius: isExpanded ? "0 0 24px 24px" : "0 0 24px 24px",
            borderTop: "none",
          }}
        >
          {/* Glass Reflection Overlay */}
          <div
            className="absolute inset-0 opacity-30 pointer-events-none"
            style={{
              background: `linear-gradient(135deg, 
                transparent 0%, 
                rgba(255,255,255,0.1) 25%, 
                rgba(255,255,255,0.2) 40%, 
                rgba(255,255,255,0.1) 60%, 
                transparent 100%)`,
              clipPath: "inherit",
              borderRadius: "inherit",
            }}
          />

          {/* Additional diagonal light streak */}
          <div
            className="absolute top-2 left-8 w-32 h-1 opacity-20 pointer-events-none"
            style={{
              background:
                "linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent)",
              transform: "rotate(-15deg)",
              filter: "blur(1px)",
            }}
          />

          {/* Compact Mode */}
          {!isExpanded && (
            <div className="flex items-center h-full px-4 space-x-3 pt-2">
              {/* State Indicator */}
              <div
                className={`
                w-2 h-2 rounded-full transition-all duration-200
                ${stateIndicator.color} 
                ${stateIndicator.pulse ? "animate-pulse" : ""}
              `}
              />

              {/* Waveform (Listening State) */}
              {state === "listening" && (
                <div ref={waveformRef} className="flex items-center space-x-1">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <div
                      key={i}
                      className="w-1 bg-blue-400 rounded-full transition-all duration-150"
                      style={{ height: "8px" }}
                    />
                  ))}
                </div>
              )}

              {/* Input Area */}
              <form onSubmit={handleSubmit} className="flex-1">
                <input
                  ref={inputRef}
                  type="text"
                  value={state === "responding" ? currentResponse : inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder={
                    state === "listening"
                      ? "Listening..."
                      : state === "responding"
                      ? "Ren is thinking..."
                      : state === "error"
                      ? "Try again..."
                      : "Ask Ren anything..."
                  }
                  className={`
                    w-full bg-transparent border-none outline-none
                    ${textColor} ${placeholderColor} text-sm
                  `}
                  disabled={state === "responding" || state === "listening"}
                  readOnly={state === "responding"}
                />
              </form>

              {/* Controls */}
              <div className="flex items-center space-x-2">
                {/* Handoff Indicator */}
                {isHandoffActive && (
                  <div className="flex items-center space-x-1">
                    <Wifi
                      className={`w-3 h-3 ${
                        isDarkMode ? "text-blue-400" : "text-blue-500"
                      }`}
                    />
                    <div className="w-1 h-1 bg-blue-400 rounded-full animate-pulse" />
                  </div>
                )}

                {/* Mic Button */}
                <button
                  onClick={handleToggleListening}
                  className={`
                    p-1.5 rounded-full transition-all duration-200
                    ${
                      state === "listening"
                        ? "bg-blue-500/80 text-white shadow-lg shadow-blue-500/30"
                        : isDarkMode
                        ? "bg-white/10 text-white/70 hover:bg-white/20 hover:text-white"
                        : "bg-black/10 text-slate-600 hover:bg-black/20 hover:text-slate-900"
                    }
                  `}
                >
                  {state === "listening" ? (
                    <Mic className="w-3 h-3" />
                  ) : (
                    <MicOff className="w-3 h-3" />
                  )}
                </button>

                {/* Speaker Button */}
                <button
                  onClick={() => setIsSpeechEnabled(!isSpeechEnabled)}
                  className={`
                    p-1.5 rounded-full transition-all duration-200
                    ${
                      isDarkMode
                        ? "bg-white/10 text-white/70 hover:bg-white/20 hover:text-white"
                        : "bg-black/10 text-slate-600 hover:bg-black/20 hover:text-slate-900"
                    }
                  `}
                >
                  {isSpeechEnabled ? (
                    <Volume2 className="w-3 h-3" />
                  ) : (
                    <VolumeX className="w-3 h-3" />
                  )}
                </button>

                {/* Expand Button */}
                <button
                  onClick={onToggleExpanded}
                  className={`
                    p-1.5 rounded-full transition-all duration-200
                    ${
                      isDarkMode
                        ? "bg-white/10 text-white/70 hover:bg-white/20 hover:text-white"
                        : "bg-black/10 text-slate-600 hover:bg-black/20 hover:text-slate-900"
                    }
                  `}
                >
                  <ChevronDown className="w-3 h-3" />
                </button>
              </div>
            </div>
          )}

          {/* Expanded Mode */}
          {isExpanded && (
            <div className="p-4 pt-6 space-y-4">
              {/* Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div
                    className={`w-2 h-2 rounded-full ${stateIndicator.color} ${
                      stateIndicator.pulse ? "animate-pulse" : ""
                    }`}
                  />
                  <span className={`text-sm ${textColor}/70`}>
                    {state === "listening"
                      ? "Listening..."
                      : state === "responding"
                      ? "Responding..."
                      : state === "error"
                      ? "Error"
                      : "Ready"}
                  </span>
                  {isHandoffActive && (
                    <div className="flex items-center space-x-1 ml-2">
                      <Wifi
                        className={`w-3 h-3 ${
                          isDarkMode ? "text-blue-400" : "text-blue-500"
                        }`}
                      />
                      <span className={`text-xs ${textColor}/50`}>Synced</span>
                    </div>
                  )}
                </div>
                <button
                  onClick={onToggleExpanded}
                  className={`p-1 rounded-lg ${
                    isDarkMode ? "hover:bg-white/10" : "hover:bg-black/10"
                  } transition-colors`}
                >
                  <ChevronDown
                    className={`w-4 h-4 ${textColor}/70 rotate-180`}
                  />
                </button>
              </div>

              {/* Enhanced Input */}
              <form onSubmit={handleSubmit} className="relative">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Ask Ren anything..."
                  className={`
                    w-full px-3 py-2 rounded-xl border transition-all duration-200
                    ${
                      isDarkMode
                        ? "bg-white/5 border-white/20 text-white placeholder-white/60"
                        : "bg-black/5 border-black/20 text-slate-900 placeholder-slate-500"
                    }
                    focus:outline-none focus:ring-2 focus:ring-blue-400/50
                  `}
                  disabled={state === "responding"}
                />
                {state === "responding" && (
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <div
                      className={`w-4 h-4 border-2 rounded-full animate-spin ${
                        isDarkMode
                          ? "border-white/20 border-t-white/60"
                          : "border-slate-300 border-t-slate-600"
                      }`}
                    />
                  </div>
                )}
              </form>

              {/* Conversation History */}
              <div className="max-h-48 overflow-y-auto space-y-2">
                {conversations.slice(-5).map((message, index) => (
                  <div
                    key={index}
                    className={`text-sm ${
                      message.role === "user" ? "text-right" : "text-left"
                    }`}
                  >
                    <div
                      className={`inline-block px-3 py-1.5 rounded-lg max-w-[80%] ${
                        message.role === "user"
                          ? isDarkMode
                            ? "bg-blue-500/20 text-blue-100 border border-blue-400/30"
                            : "bg-blue-500/10 text-blue-900 border border-blue-400/30"
                          : isDarkMode
                          ? "bg-white/10 text-white/80 border border-white/20"
                          : "bg-black/10 text-slate-700 border border-black/20"
                      }`}
                    >
                      {message.content}
                    </div>
                  </div>
                ))}

                {/* Typing Indicator */}
                {isTyping && (
                  <div className="text-left">
                    <div
                      className={`inline-block px-3 py-1.5 rounded-lg border ${
                        isDarkMode
                          ? "bg-white/10 border-white/20"
                          : "bg-black/10 border-black/20"
                      }`}
                    >
                      <div className="flex space-x-1">
                        <div
                          className={`w-1 h-1 rounded-full animate-pulse ${
                            isDarkMode ? "bg-white/60" : "bg-slate-600"
                          }`}
                        />
                        <div
                          className={`w-1 h-1 rounded-full animate-pulse ${
                            isDarkMode ? "bg-white/60" : "bg-slate-600"
                          }`}
                          style={{ animationDelay: "0.2s" }}
                        />
                        <div
                          className={`w-1 h-1 rounded-full animate-pulse ${
                            isDarkMode ? "bg-white/60" : "bg-slate-600"
                          }`}
                          style={{ animationDelay: "0.4s" }}
                        />
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Controls Row */}
              <div className="flex items-center justify-between pt-2 border-t border-white/10">
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleToggleListening}
                    className={`
                      p-2 rounded-lg transition-all duration-200
                      ${
                        state === "listening"
                          ? "bg-blue-500/80 text-white shadow-lg shadow-blue-500/30"
                          : isDarkMode
                          ? "bg-white/10 text-white/70 hover:bg-white/20"
                          : "bg-black/10 text-slate-600 hover:bg-black/20"
                      }
                    `}
                  >
                    {state === "listening" ? (
                      <Mic className="w-4 h-4" />
                    ) : (
                      <MicOff className="w-4 h-4" />
                    )}
                  </button>

                  <button
                    onClick={() => setIsSpeechEnabled(!isSpeechEnabled)}
                    className={`
                      p-2 rounded-lg transition-all duration-200
                      ${
                        isDarkMode
                          ? "bg-white/10 text-white/70 hover:bg-white/20"
                          : "bg-black/10 text-slate-600 hover:bg-black/20"
                      }
                    `}
                  >
                    {isSpeechEnabled ? (
                      <Volume2 className="w-4 h-4" />
                    ) : (
                      <VolumeX className="w-4 h-4" />
                    )}
                  </button>
                </div>

                <div className={`text-xs ${textColor}/40`}>
                  {conversations.length} messages
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Enhanced Glow Effect */}
        {(state === "listening" || state === "responding") && (
          <>
            {/* Primary glow */}
            <div
              className={`
              absolute inset-0 rounded-b-3xl blur-xl opacity-40 pointer-events-none
              ${state === "listening" ? "bg-blue-400/40" : "bg-green-400/40"}
            `}
              style={{ clipPath: "inherit" }}
            />

            {/* Secondary ambient glow */}
            <div
              className={`
              absolute -inset-4 rounded-b-3xl blur-2xl opacity-20 pointer-events-none
              ${state === "listening" ? "bg-blue-500/30" : "bg-green-500/30"}
            `}
            />
          </>
        )}
      </div>
    </div>
  );
}
