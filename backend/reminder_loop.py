# reminder_loop.py
import threading
import time
from datetime import datetime
from persistent_memory import PersistentMemory

class ReminderLoop:
    def __init__(self, memory: PersistentMemory, notify_callback):
        self.memory = memory
        self.notify = notify_callback  # function to call when a reminder is due
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            thread = threading.Thread(target=self._run, daemon=True)
            thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            now = datetime.now()
            reminders = self.memory.get_reminders()
            updated = []

            for reminder in reminders:
                reminder_time = reminder.get("time")
                if reminder_time and self._is_due(reminder_time, now):
                    self.notify(f"⏰ Reminder: {reminder['task']}")
                else:
                    updated.append(reminder)

            if len(updated) != len(reminders):
                self.memory.set("reminders", updated)  # remove fired reminders

            time.sleep(10)  # check every 10 seconds

    def _is_due(self, reminder_time_str, now: datetime) -> bool:
        try:
            reminder_time = datetime.strptime(reminder_time_str, "%I:%M %p")  # Format: 10:30 AM
            return now.hour == reminder_time.hour and now.minute == reminder_time.minute
        except Exception as e:
            print(f"[ReminderLoop] Invalid time format: {reminder_time_str}")
            return False