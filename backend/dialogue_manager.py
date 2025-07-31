import re
from typing import Optional
import uuid

from generate_reply import generate_reply
from persistent_memory import PersistentMemory
from reminder_scheduler import ReminderScheduler
from sentiment_analyzer import analyze_tone


class DialogueManager:
    def __init__(self, memory_store: PersistentMemory, scheduler: ReminderScheduler):
        self.dialogue_state = {}
        self.memory_store = memory_store
        self.scheduler = scheduler

        # --- NEW: Rolling short-term memory for Ren's context ---
        self.recent_memory = []

    def reset_state(self):
        self.dialogue_state.clear()

    def handle_input(self, user_input: str, user_name: Optional[str] = None):
        intent, slots = self._extract_intent_and_slots(user_input)

        # --- Handle delete/cancel reminder intent ---
        if intent == "cancel_reminder":
            deleted = self._delete_matching_reminder(slots.get("task"), slots.get("time"))
            if deleted:
                return f"Got it. I’ve removed the reminder to '{deleted['task']}' at {deleted['time']}."
            return "I couldn’t find a matching reminder to cancel. Want to try again?"

        # Handle in-progress reminder flow
        if self.dialogue_state.get("intent") == "set_reminder":
            return self._continue_set_reminder(user_input, intent, slots, user_name)

        if intent == "set_reminder":
            self.dialogue_state = {
                "intent": intent,
                "pending_slots": ["task", "time"],
                "collected_slots": {}
            }
            for slot, value in slots.items():
                if value:
                    self.dialogue_state["collected_slots"][slot] = value
                    if slot in self.dialogue_state["pending_slots"]:
                        self.dialogue_state["pending_slots"].remove(slot)
            return self._prompt_next_slot(user_name)

        return None

    def _extract_intent_and_slots(self, user_input: str):
        user_lower = user_input.lower()

        # Cancel/Delete reminder intent
        if any(cmd in user_lower for cmd in ["cancel reminder", "delete reminder", "remove reminder", "cancel task", "delete task"]):
            task_match = re.search(r"(?:cancel|delete|remove)\s+(?:reminder|task)\s*(?:for)?\s*(.*?)(?: at| on|$)", user_input, re.IGNORECASE)
            time_match = re.search(r"at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)", user_input, re.IGNORECASE)
            task = task_match.group(1).strip() if task_match else None
            time = time_match.group(1).strip() if time_match else None
            return "cancel_reminder", {"task": task, "time": time}

        # Set reminder intent
        if "remind me" in user_lower or "set reminder" in user_lower:
            task_match = re.search(r"remind me to (.+?)(?: at| on| tomorrow|$)", user_input, re.IGNORECASE)
            time_match = re.search(r"at (\d{1,2}(?::\d{2})?\s*(?:am|pm)?)", user_input, re.IGNORECASE)
            task = task_match.group(1).strip() if task_match else None
            time = time_match.group(1).strip() if time_match else None
            return "set_reminder", {"task": task, "time": time}

        return None, {}

    def _prompt_next_slot(self, user_name: Optional[str] = None):
        if not self.dialogue_state["pending_slots"]:
            task = self.dialogue_state["collected_slots"].get("task")
            time = self.dialogue_state["collected_slots"].get("time")
            name_prefix = f"{user_name}, " if user_name else ""
            return f"{name_prefix}I see you want to '{task}' at {time}. Is that correct? (yes/no)"
        else:
            next_slot = self.dialogue_state["pending_slots"][0]
            if next_slot == "task":
                return "What would you like me to remind you about?"
            elif next_slot == "time":
                return "At what time should I remind you?"

    def _continue_set_reminder(self, user_input: str, new_intent, new_slots, user_name: Optional[str] = None):
        user_lower = user_input.lower()

        if any(yes in user_lower for yes in ["yes", "yeah", "correct", "yep", "sure"]):
            task = self.dialogue_state["collected_slots"].get("task")
            time = self.dialogue_state["collected_slots"].get("time")

            self.scheduler.schedule(user=user_name or "unknown", task=task, time_str=time)

            self.reset_state()
            name_prefix = f"{user_name}, " if user_name else ""
            return f"Great! {name_prefix}I’ve scheduled your reminder to '{task}' at {time}."

        elif any(no in user_lower for no in ["no", "nah", "nope", "incorrect"]):
            self.reset_state()
            return "Okay, let's try again. What would you like me to remind you about?"

        else:
            for slot, value in new_slots.items():
                if value:
                    self.dialogue_state["collected_slots"][slot] = value
                    if slot in self.dialogue_state["pending_slots"]:
                        self.dialogue_state["pending_slots"].remove(slot)

            if self.dialogue_state["pending_slots"]:
                return self._prompt_next_slot(user_name)

            task = self.dialogue_state["collected_slots"].get("task")
            time = self.dialogue_state["collected_slots"].get("time")
            name_prefix = f"{user_name}, " if user_name else ""
            return f"{name_prefix}Just to confirm, you want to '{task}' at {time}. Is that right? (yes/no)"

    def _delete_matching_reminder(self, task: Optional[str], time: Optional[str]) -> Optional[dict]:
        reminders = self.memory_store.get_reminders()
        for reminder in reminders:
            if task and task.lower() in reminder.get("task", "").lower():
                if time:
                    if time.strip().lower() in reminder.get("time", "").lower():
                        self.scheduler.delete_reminder_by_id(reminder["id"])
                        return reminder
                else:
                    self.scheduler.delete_reminder_by_id(reminder["id"])
                    return reminder
        return None

    # --- NEW: Handle real-time input for Jarvis-style streaming ---
    def handle_partial_transcription(self, partial_text: str, user_name: Optional[str] = None):
        """
        Jarvis-style real-time handler for partial speech input.
        """
        if len(partial_text.strip()) < 3:
            return  # Skip empty/short inputs

        tone = analyze_tone(partial_text)
        memory_context = "\n".join(
            [f"User: {m['user']}\nRen: {m['ren']}" for m in self.recent_memory[-5:]]
        )

        ren_reply = generate_reply(
            user_input=partial_text,
            memory=memory_context,
            tone_data=tone,
            user_name=user_name
        )

        self.recent_memory.append({
            "user": partial_text,
            "ren": ren_reply,
            "tone": tone.get("tone", "neutral")
        })

        if len(self.recent_memory) > 10:
            self.recent_memory.pop(0)

        print(f"[Ren] {ren_reply}")
        return ren_reply