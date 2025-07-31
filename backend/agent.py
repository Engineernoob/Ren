import logging
import random
import re
import time
from typing import Optional

from config import config
from dialogue_manager import DialogueManager
from generate_reply import generate_reply
from persistent_memory import PersistentMemory
from reminder_loop import ReminderLoop
from reminder_scheduler import ReminderScheduler
from sentiment_analyzer import analyze_tone

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Agent:
    def __init__(self):
        self.conversation_memory = []
        self.memory_store: PersistentMemory = PersistentMemory()
        self.scheduler = ReminderScheduler(memory=self.memory_store)
        self.dialogue_manager = DialogueManager(memory_store=self.memory_store, scheduler=self.scheduler)
        self.user_name: Optional[str] = self.memory_store.get("user_name")
        self.pending_name_change = None
        self.traits = {
            "name": config.AGENT_NAME,
            "personality": config.AGENT_PERSONALITY,
            "memory_threshold": config.MEMORY_THRESHOLD,
        }

        self.reminder_loop = ReminderLoop(self.memory_store, self._handle_reminder_notification)
        self.reminder_loop.start()

        logger.info(f"Agent '{self.traits['name']}' initialized with personality: {self.traits['personality']}")

    def process_statement(self, user_input: str) -> str:
        if not user_input or not isinstance(user_input, str) or not user_input.strip():
            raise ValueError("User input must be a non-empty string")
        if self._is_correction_triggered(user_input):
            return self.retry_with_correction()

        user_input = user_input.strip()
        logger.info(f"Processing user input: {user_input[:100]}...")

        tone_data = analyze_tone(user_input)
        sentiment = tone_data["tone"]
        confidence = tone_data.get("confidence", 0.0)
        logger.info(f"Sentiment analysis result: {tone_data}")

        self.memory_store.set("last_sentiment", {
            "text": user_input,
            "sentiment": sentiment,
            "raw_label": tone_data.get("raw_label"),
            "confidence": confidence,
            "timestamp": time.time(),
        })
        # 🔔 High-confidence emotional alert
        if sentiment in ["serious", "tense", "low"] and confidence > 0.8:
            return f"{self.user_name or ''}, you sound overwhelmed. Want me to pause distractions or give you a moment?"
        
        # 💡 Suggest an action based on tone
        tone_suggestion = self._suggest_action_by_tone(sentiment)
        if tone_suggestion:
            return tone_suggestion

        if self.pending_name_change:
            normalized = user_input.lower()
            if normalized in ["yes", "yeah", "yep", "sure", "correct"]:
                self.user_name = self.pending_name_change
                self.memory_store.set("user_name", self.user_name)
                self.pending_name_change = None
                return f"Okay, I’ll call you {self.user_name} from now on."
            elif normalized in ["no", "nope", "nah", "cancel"]:
                self.pending_name_change = None
                return f"Alright, I'll keep calling you {self.user_name}."
            else:
                return "Please respond with 'yes' or 'no' to confirm the name change."

        self._maybe_remember_name(user_input)

        try:
            self.conversation_memory.append(user_input)
            if len(self.conversation_memory) > self.traits["memory_threshold"]:
                self.conversation_memory.pop(0)

            dialogue_response = self.dialogue_manager.handle_input(user_input, self.user_name)
            if dialogue_response is not None:
                return dialogue_response

            response = self._generate_response(user_input, sentiment)
            logger.info(f"Generated response: {response[:100]}...")
            return response

        except Exception as e:
            logger.error(f"Error processing statement: {e}")
            return f"I'm sorry, but something went wrong on my end: {str(e)}"
        
    def _suggest_action_by_tone(self, tone: str) -> Optional[str]:
        if tone == "tense":
             return "You seem a bit tense. Want me to pause notifications or activate focus mode?"
        elif tone == "low":
             return "I’m sensing some heaviness. Would a breathing exercise or playlist help?"
        elif tone == "serious":
            return "Should I pull up your schedule or give you some quiet time?"
        elif tone == "sharp":
            return "That came through pretty strong. Want to talk through it or switch topics?"
        else:
            return None
        
    def _is_correction_triggered(self, user_input: str) -> bool:
        correction_phrases = [
            "that's not", "you misunderstood", "not what i meant", "wrong", "incorrect", "that isn't it", "no what i meant"]
        return any(word in user_input.lower() for word in correction_phrases)
    
    def retry_with_correction(self) -> str:
        last = self.memory_store.get("last_exchange", {})
        if not last:
            return "I'll need more context to correct myself - could you clarity what I missed?"
        
        original_input = last.get("input", "")
        last_response = last.get("response", "")
        tone_data = self.memory_store.get("last_sentiment", {})
        
        retry_prompt = (
            f"The user said: \"{original_input}\n\n"
            f"I responded: \"{last_response}\n\n"
            "The user seems unsatisfied. Try again - but this time, be more accurate, emotionally aware, and flexiable in interpretation. \n "
        )
        
        try:
            retry_reply = generate_reply(
                user_input=retry_prompt,
                memory="",
                tone_data=tone_data,
                user_name=self.user_name,  
            )
            self.memory_store.set("last_exchange", {
                "input": original_input,
                "response": retry_reply,
                "corrected": True,
                })
            return f"[REWRITE] {retry_reply}"
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I'm sorry, but something went wrong on my end: {str(e)}"

            
    def _generate_response(self, user_input: str, sentiment: Optional[str] = None) -> str:
        user_lower = user_input.lower()
        greetings = ["hi", "hello", "hey", "greetings", "good morning", "good evening", "good afternoon"]
        farewells = ["bye", "goodbye", "farewell", "see you", "later"]
        thanks = ["thank you", "thanks", "thank you so much", "thank you very much"]
        memory_inquiries = ["remember", "memory", "how much do you remember"]
        identity_queries = ["who are you", "what are you", "your name"]
        name_change_triggers = ["actually", "not", "call me", "change my name", "you got it wrong", "my name is actually"]

        if any(word in user_lower for word in greetings):
            return f"Hey. I'm {self.traits['name']}. You sound like you needed someone to talk to. What's your name?" if not self.user_name else f"Hey {self.user_name}. I'm here for you. What’s on your mind?"

        if any(word in user_lower for word in thanks):
            return "Anytime, you’re welcome. How can I help you today?"

        if any(word in user_lower for word in farewells):
            return f"Talk soon{', ' + self.user_name if self.user_name else ''}. I’ll be here when you’re ready again."

        if any(word in user_lower for word in memory_inquiries):
            mem = len(self.conversation_memory)
            return f"I remember our last {mem} message{'s' if mem != 1 else ''}. I keep track of up to {self.traits['memory_threshold']}."

        if any(word in user_lower for word in identity_queries):
            return f"I'm {self.traits['name']} — a voice that listens, and a mind designed to respond patiently."

        if any(trigger in user_lower for trigger in name_change_triggers):
            new_name = self._extract_name(user_input)
            if new_name:
                if new_name != self.user_name:
                    self.pending_name_change = new_name
                    return f"Do you want me to call you {new_name} instead of {self.user_name}? Please reply yes or no."
                else:
                    return f"I already had you as {self.user_name}, but happy to be sure!"
            else:
                return "Okay, I’m listening. What should I call you?"

        if "my name is" in user_lower or "i'm" in user_lower or "i am" in user_lower:
            if self.user_name:
                return f"I’ve already saved your name as {self.user_name}. Let me know if that changes."
            else:
                guessed_name = self._extract_name(user_input)
                if guessed_name:
                    self.user_name = guessed_name
                    self.memory_store.set("user_name", self.user_name)
                    return f"Nice to meet you, {self.user_name}. I’m here if you want to talk."

        if self._sounds_like_small_talk(user_input):
            return self._chit_chat_response(user_input)

        return self._fallback_empathy_response(user_input)

    def _maybe_remember_name(self, text: str):
        if not self.user_name:
            name = self._extract_name(text)
            if name:
                self.user_name = name
                self.memory_store.set("user_name", name)
                logger.info(f"[Ren] Detected and saved user name: {self.user_name}")

    def _extract_name(self, text: str) -> Optional[str]:
        patterns = [
            r"(?:my name is|i am|i'm|call me|you can call me|the name's|name is|name's|this is|they call me|nickname is)\s+([A-Z][a-zA-Z\-']*)",
            r"^\s*([A-Z][a-zA-Z\-']{2,})\s*$"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).capitalize()
        return None

    def _sounds_like_small_talk(self, input_text: str) -> bool:
        small_talk_phrases = [
            "just talk", "just chatting", "i want to talk", "let's talk", "what's up", "how are you", "can we talk"
        ]
        return any(phrase in input_text.lower() for phrase in small_talk_phrases)

    def _chit_chat_response(self, input_text: str) -> str:
        memory = self.conversation_memory
        if len(memory) <= 1:
            return "Yeah... we can just talk. No agenda. No pressure."
        if any(word in input_text.lower() for word in ["tired", "stressed", "bored"]):
            return "Sounds like today’s been a lot. Want to vent a bit?"
        if "talk" in input_text.lower():
            return "Of course. Talking helps. I'm right here."
        return "Still here. Still listening. What's on your mind?"

    def _fallback_empathy_response(self, input_text: str) -> str:
        last = self.memory_store.get("last_sentiment")
        sentiment = last.get("sentiment") if last else None

        if sentiment == "serious":
            return "Still feeling off today? Want to talk more about it?"
        if sentiment == "warm":
            return "Still feeling okay? I'm glad. What else is on your mind?"

        return random.choice([
            "I’m right here. Let’s talk through it.",
            "No judgment. Say whatever’s on your mind.",
            "You’ve got my attention. Go ahead.",
            "Let’s just sit with this for a moment, if that’s okay."
        ])

    def _handle_reminder_notification(self, message: str):
        logger.info(f"[ReminderLoop] {message}")
        self.conversation_memory.append(message)

    def get_conversation_summary(self) -> dict:
        return {
            "memory_count": len(self.conversation_memory),
            "memory_threshold": self.traits["memory_threshold"],
            "recent_inputs": self.conversation_memory[-3:] if self.conversation_memory else [],
            "agent_name": self.traits["name"],
            "personality": self.traits["personality"],
            "user_name": self.user_name or "unknown"
        }