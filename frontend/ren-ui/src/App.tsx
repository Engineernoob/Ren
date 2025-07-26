import { NotchRen } from "./ren-front/NotchRen";
import { useState } from "react";

export default function App() {
  const [state, setState] = useState<
    "idle" | "listening" | "responding" | "error"
  >("idle");
  const [isExpanded, setIsExpanded] = useState(false);
  const [isHandoffActive, setIsHandoffActive] = useState(false);

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Enhanced desktop background with subtle depth */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800">
        {/* Subtle overlay patterns */}
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-purple-500/8 rounded-full blur-3xl" />
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-slate-500/5 rounded-full blur-3xl" />
        </div>

        {/* Top gradient to enhance notch integration */}
        <div className="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-black/40 via-black/20 to-transparent" />
      </div>

      {/* Simulated macOS elements */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Menu bar */}
        <div className="absolute top-0 left-0 right-0 h-6 bg-black/30 backdrop-blur-xl border-b border-white/10">
          <div className="flex items-center justify-between h-full px-4">
            <div className="flex items-center space-x-4">
              <div className="w-4 h-4 bg-white/20 rounded" />
              <div className="w-16 h-3 bg-white/15 rounded" />
              <div className="w-12 h-3 bg-white/10 rounded" />
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-3 bg-white/15 rounded" />
              <div className="w-6 h-3 bg-white/15 rounded" />
              <div className="w-4 h-3 bg-white/15 rounded" />
            </div>
          </div>
        </div>

        {/* Desktop icons */}
        <div className="absolute top-40 right-8 space-y-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className="flex flex-col items-center space-y-2"
            >
              <div className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 shadow-lg" />
              <div className="w-14 h-2 bg-white/20 rounded-full" />
            </div>
          ))}
        </div>

        {/* Dock */}
        <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2">
          <div className="bg-white/15 backdrop-blur-2xl border border-white/25 rounded-2xl px-6 py-3 shadow-2xl">
            <div className="flex space-x-4">
              {Array.from({ length: 8 }).map((_, i) => (
                <div
                  key={i}
                  className="w-14 h-14 bg-white/20 rounded-xl border border-white/30 shadow-lg hover:scale-110 transition-transform duration-200"
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced NotchRen Component */}
      <NotchRen
        state={state}
        isDarkMode={true}
        isHandoffActive={isHandoffActive}
        onStateChange={setState}
        onToggleExpanded={() => setIsExpanded(!isExpanded)}
        isExpanded={isExpanded}
      />

      {/* Development controls (hidden in production) */}
      <div className="absolute bottom-8 left-8 bg-black/20 backdrop-blur-xl border border-white/20 rounded-2xl p-4 space-y-3 max-w-xs">
        <h4 className="text-white/90 text-sm">Dev Controls</h4>

        {/* State Controls */}
        <div>
          <label className="block text-white/70 text-xs mb-2">
            Assistant State
          </label>
          <div className="grid grid-cols-2 gap-2">
            {(
              [
                "idle",
                "listening",
                "responding",
                "error",
              ] as const
            ).map((newState) => (
              <button
                key={newState}
                onClick={() => setState(newState)}
                className={`
                  px-3 py-2 rounded-lg text-xs border transition-all duration-200 capitalize
                  ${
                    state === newState
                      ? "bg-blue-500/30 border-blue-400/50 text-white"
                      : "bg-white/5 border-white/20 text-white/70 hover:bg-white/10 hover:text-white"
                  }
                `}
              >
                {newState}
              </button>
            ))}
          </div>
        </div>

        {/* Feature Toggles */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-white/70 text-xs">
              Expanded View
            </span>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className={`
                relative w-8 h-4 rounded-full transition-all duration-200
                ${isExpanded ? "bg-blue-500" : "bg-white/20"}
              `}
            >
              <div
                className={`
                  absolute top-0.5 w-3 h-3 bg-white rounded-full transition-all duration-200
                  ${isExpanded ? "left-4" : "left-0.5"}
                `}
              />
            </button>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-white/70 text-xs">
              Handoff Sync
            </span>
            <button
              onClick={() =>
                setIsHandoffActive(!isHandoffActive)
              }
              className={`
                relative w-8 h-4 rounded-full transition-all duration-200
                ${isHandoffActive ? "bg-green-500" : "bg-white/20"}
              `}
            >
              <div
                className={`
                  absolute top-0.5 w-3 h-3 bg-white rounded-full transition-all duration-200
                  ${isHandoffActive ? "left-4" : "left-0.5"}
                `}
              />
            </button>
          </div>
        </div>

        {/* Status Display */}
        <div className="pt-2 border-t border-white/20">
          <div className="text-xs text-white/50 space-y-1">
            <div>
              State:{" "}
              <span className="text-white/70 capitalize">
                {state}
              </span>
            </div>
            <div>
              Expanded:{" "}
              <span className="text-white/70">
                {isExpanded ? "Yes" : "No"}
              </span>
            </div>
            <div>
              Handoff:{" "}
              <span className="text-white/70">
                {isHandoffActive ? "Active" : "Inactive"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Handoff Status Indicator (when active) */}
      {isHandoffActive && (
        <div className="absolute top-20 right-8 bg-green-500/20 backdrop-blur-xl border border-green-400/30 rounded-xl p-3 max-w-xs">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-green-200 text-xs">
              Multi-device sync active
            </span>
          </div>
          <div className="text-green-200/70 text-xs mt-1">
            Conversations synced across all devices
          </div>
        </div>
      )}
    </div>
  );
}