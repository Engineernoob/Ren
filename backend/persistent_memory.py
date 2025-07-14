# persistent_memory.py

import json
import os
from typing import Any, Dict

MEMORY_FILE = "ren_memory.json"

class PersistentMemory:
    def __init__(self, file_path: str = MEMORY_FILE):
        self.file_path = file_path
        self.memory: Dict[str, Any] = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[PersistentMemory] Error loading memory: {e}")
        return {}

    def save(self) -> None:
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"[PersistentMemory] Error saving memory: {e}")

    def get(self, key: str, default=None) -> Any:
        return self.memory.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.memory[key] = value
        self.save()

    def delete(self, key: str) -> None:
        if key in self.memory:
            del self.memory[key]
            self.save()

    def all(self) -> Dict[str, Any]:
        return self.memory
    
# Optional convenience methods
    def add_reminder(self, reminder: Dict[str, Any]) -> None:
        reminders = self.memory.get("reminders", [])
        reminders.append(reminder)
        self.memory["reminders"] = reminders
        self.save()

    def get_reminders(self) -> list:
        return self.memory.get("reminders", [])

    def delete_reminder(self, reminder_id: str) -> None:
        reminders = self.memory.get("reminders", [])
        reminders = [r for r in reminders if r.get("id") != reminder_id]
        self.memory["reminders"] = reminders
        self.save()