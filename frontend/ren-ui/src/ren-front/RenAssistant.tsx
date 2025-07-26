"use client";

import { useState } from "react";
import { FloatingAssistant } from "./FloatingAssistant.tsx";

type AssistantState =
  | "idle"
  | "listening"
  | "speaking"
  | "thinking";

interface RenAssistantProps {
  variant?: "default" | "minimal" | "premium";
  initialState?: AssistantState;
  onStateChange?: (state: AssistantState) => void;
}

export function RenAssistant({
  variant = "default",
  initialState = "idle",
  onStateChange,
}: RenAssistantProps) {
  const [state, setState] =
    useState<AssistantState>(initialState);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleStateChange = (newState: AssistantState) => {
    setState(newState);
    onStateChange?.(newState);
  };

  return (
    <div className="fixed inset-0 pointer-events-none">
      {/* Subtle background for standalone use */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900/20 via-blue-900/10 to-slate-800/20" />

      {/* The floating assistant - only this part has pointer events */}
      <div className="pointer-events-auto">
        <FloatingAssistant
          variant={variant}
          state={state}
          isExpanded={isExpanded}
          onStateChange={handleStateChange}
          onToggleExpanded={() => setIsExpanded(!isExpanded)}
        />
      </div>
    </div>
  );
}