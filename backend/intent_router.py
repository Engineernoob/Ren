# backend/intent_router.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Literal, Optional, Tuple
import re

IntentName = Literal[
    "checkin",       # start/progress wellness check-in
    "exit",          # end session / quit
    "reminder",      # set a reminder
    "greeting",      # hi/hello
    "farewell",      # bye/see ya
    "weather",       # weather queries (placeholder)
    "smalltalk",     # chit-chat
    "agent_action",  # ask Ren to do something (“open…”, “create…”, “schedule…”)
    "chat"           # default catch-all to LLM
]

@dataclass
class Intent:
    name: IntentName
    # freeform fields for downstream handlers
    slots: Dict[str, str]
    confidence: float = 0.7  # simple scalar; bump if you add model scoring

GREETING_PAT = re.compile(r"\b(hi|hello|hey|good (morning|afternoon|evening))\b", re.I)
FAREWELL_PAT = re.compile(r"\b(bye|goodbye|see\s?ya|later|exit|quit)\b", re.I)
CHECKIN_PAT  = re.compile(r"\b(check[\s-]?in|check\s?up|how am i|mental\s?health)\b", re.I)
REMIND_PAT   = re.compile(r"\b(remind|reminder|remember to)\b", re.I)
WEATHER_PAT  = re.compile(r"\b(weather|forecast|temperature)\b", re.I)
ACTION_PAT   = re.compile(r"\b(open|create|schedule|start|launch|send|draft)\b", re.I)
SMALLTALK_PAT= re.compile(r"\b(how are you|what's up|wyd|how's it going)\b", re.I)

# very rough time phrase catcher: “in 2 hours”, “tomorrow 3pm”, “at 4”, “next monday”
TIME_PHRASE  = re.compile(
    r"\b(in\s+\d+\s+(min|mins|minutes|hour|hours|days)|tomorrow|tonight|this (evening|afternoon|morning)|"
    r"(mon|tue|wed|thu|fri|sat|sun)(day)?|next\s+(week|month|monday|tuesday|wednesday|thursday|friday)|"
    r"at\s+\d{1,2}(:\d{2})?\s?(am|pm)?|\d{1,2}(:\d{2})?\s?(am|pm))\b",
    re.I
)

def extract_time(text: str) -> Optional[str]:
    m = TIME_PHRASE.search(text)
    return m.group(0) if m else None

def route_intent(text: str) -> Intent:
    t = text.strip()

    if not t:
        return Intent(name="chat", slots={}, confidence=0.2)

    if FAREWELL_PAT.search(t):
        return Intent(name="farewell", slots={}, confidence=0.95)

    if GREETING_PAT.search(t):
        return Intent(name="greeting", slots={}, confidence=0.9)

    if CHECKIN_PAT.search(t):
        return Intent(name="checkin", slots={}, confidence=0.9)

    if REMIND_PAT.search(t):
        when = extract_time(t)
        # message w/o the “remind/reminder” token — crude task text
        task = re.sub(REMIND_PAT, "", t, flags=re.I).strip(" ,.;:")
        return Intent(name="reminder", slots={"when": when or "", "task": task}, confidence=0.85)

    if WEATHER_PAT.search(t):
        return Intent(name="weather", slots={}, confidence=0.7)

    if SMALLTALK_PAT.search(t):
        return Intent(name="smalltalk", slots={}, confidence=0.7)

    if ACTION_PAT.search(t):
        return Intent(name="agent_action", slots={"command": t}, confidence=0.7)

    # default: let the LLM handle it
    return Intent(name="chat", slots={}, confidence=0.5)