from datetime import datetime
import threading
import time
from typing import Optional

from persistent_memory import PersistentMemory


class ReminderScheduler:
    def __init__(self, memory: PersistentMemory, check_interval: int = 30):
        self.memory = memory
        self.check_interval = check_interval  # in seconds
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def _normalize_time(self, time_str: str) -> str:
        try:
            cleaned = time_str.strip().upper().replace(" ", "")
            dt = datetime.strptime(cleaned, "%I:%M%p")
            return dt.strftime("%H:%M")
        except (ValueError, AttributeError):
            print(f"[ReminderLoop] Invalid time format: {time_str}")
            return ""

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def _run(self):
        while self.running:
            now = datetime.now().strftime("%H:%M")  # 24-hour format e.g. "21:30"
            reminders = self.memory.get_reminders()

            for reminder in reminders:
                reminder_time_norm = self._normalize_time(reminder.get("time", ""))
                if reminder_time_norm == now and not reminder.get("notified"):
                    print(f"[Reminder] {reminder['task']} at {reminder['time']}")
                    reminder["notified"] = True  # Prevent repeated notification

            self.memory.set("reminders", reminders)
            time.sleep(self.check_interval)

    def schedule(self, user: str, task: str, time_str: str):
        reminder_id = f"{user}-{int(time.time())}"
        reminder = {
            "id": reminder_id,
            "user": user,
            "task": task,
            "time": time_str,
            "notified": False
        }
        self.memory.add_reminder(reminder)
        print(f"[Scheduler] Scheduled reminder: {reminder}")

    def delete_reminder_by_id(self, reminder_id: str) -> bool:
        reminders = self.memory.get_reminders()
        new_reminders = [r for r in reminders if r.get("id") != reminder_id]
        if len(new_reminders) < len(reminders):
            self.memory.set("reminders", new_reminders)
            print(f"[Scheduler] Deleted reminder with ID: {reminder_id}")
            return True
        print(f"[Scheduler] Reminder ID not found: {reminder_id}")
        return False

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()

    def __del__(self):
        self.stop()