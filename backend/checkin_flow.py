# backend/checkin_flow.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional, Tuple

Phase = Literal["intro", "prompt", "reflect", "action", "wrap"]

@dataclass
class CheckInState:
    active: bool = False
    phase: Phase = "intro"
    last_user_input: str = ""
    summary: Optional[str] = None

def handle_checkin_input(state: CheckInState, user_input: str) -> Tuple[CheckInState, str, bool]:
    """
    Update the check-in state and return (new_state, assistant_reply, done).
    This is just a simple placeholder flow — tweak as you like.
    """
    user_input = user_input.strip()
    if not state.active:
        state.active = True
        state.phase = "intro"
        return state, "Let’s do a quick check-in. How are you feeling right now?", False

    if state.phase == "intro":
        state.last_user_input = user_input
        state.phase = "prompt"
        return state, "Got it. What’s the biggest thing on your mind?", False

    if state.phase == "prompt":
        state.last_user_input = user_input
        state.phase = "reflect"
        return state, "Thanks. If you name one thing you can do in the next hour, what would it be?", False

    if state.phase == "reflect":
        state.last_user_input = user_input
        state.phase = "action"
        return state, "Alright. Want me to set a reminder or block time for it?", False

    if state.phase == "action":
        state.summary = f"Focus: {state.last_user_input}"
        state.phase = "wrap"
        return state, "Done. That’s the check-in. Anything else before we wrap?", False

    # wrap
    return state, "All set. We can check in again later.", True