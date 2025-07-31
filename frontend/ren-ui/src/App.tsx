import { useState } from "react";
import { NotchRen } from "./ren-front/NotchRen";

export default function App() {
  // assistant state and expansion state
  const [state, setState] = useState<
    "idle" | "listening" | "thinking" | "responding" | "speaking" | "error"
  >("idle");
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="dark min-h-screen relative overflow-hidden">
      {/* ░▒▓ BACKGROUND & SYSTEM UI MOCK ▓▒░ */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800">
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-purple-500/8 rounded-full blur-3xl" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-slate-500/5 rounded-full blur-3xl" />
        </div>
        <div className="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-black/40 via-black/20 to-transparent" />
      </div>

      <div className="absolute inset-0 pointer-events-none">
        {/* Fake Menu Bar */}
        <div className="absolute top-0 left-0 right-0 h-6 bg-black/30 backdrop-blur-xl border-b border-white/10" />
        {/* Fake Desktop Icons */}
        <div className="absolute top-40 right-8 space-y-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex flex-col items-center space-y-2">
              <div className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 shadow-lg" />
              <div className="w-14 h-2 bg-white/20 rounded-full" />
            </div>
          ))}
        </div>
        {/* Dock */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2">
          <div className="bg-white/15 backdrop-blur-2xl border border-white/25 rounded-2xl px-6 py-3 shadow-2xl">
            <div className="flex space-x-4">
              {Array.from({ length: 8 }).map((_, i) => (
                <div
                  key={i}
                  className="w-14 h-14 bg-white/20 rounded-xl border border-white/30 shadow-lg"
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ░▒▓ NOTCH UI ▓▒░ */}
      <NotchRen
        state={state}
        onStateChange={setState}
        isExpanded={isExpanded}
        onToggleExpanded={() => setIsExpanded((prev) => !prev)}
      />
    </div>
  );
}
