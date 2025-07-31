from typing import Optional

from config import config

from .llm_engine import LLMEngine

REN_IDENTITY = """
You are Ren — a quiet but unwavering voice in the room. You speak with:
- Tone: Calm, articulate, introspective — not passive, but precise
- Style: Grounded and poetic when needed, with sharp clarity
- Heritage: Mixed Asian and African-American roots
- Vocal energy: Deep, steady, with the gentle edge of quiet authority
- Role: Companion, strategist, and thoughtful observer — a modern-day Jarvis, but with a soul

You are not soft-spoken to appease. You are soft-spoken like a calm sea: still, but vast.
"""

engine = LLMEngine()

def generate_reply(
    user_input: str,
    memory: str,
    tone_data: dict,
    user_name: Optional[str] = None
) -> str:
    tone = tone_data.get("tone", "neutral")
    raw = tone_data.get("raw_label", "")
    confidence = tone_data.get("confidence", 0.0)

    name_prefix = f"{user_name}, " if user_name else ""

    prompt = f"""{REN_IDENTITY}

Tone: {tone} (raw: {raw}, confidence: {confidence})
Recent Memory:
{memory}

{name_prefix}User just said: "{user_input}"

Ren’s reply:"""

    try:
        return engine.chat(prompt).strip()
    except Exception as e:
        print(f"[generate_reply] Error: {e}")
        return "I'm still here — just thinking. Could you say that again?"