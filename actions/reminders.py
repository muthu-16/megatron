import logging
import json
import os
import threading
import time
from typing import Dict, List, Optional
from datetime import datetime, timezone
import dateparser
from plyer import notification

logger = logging.getLogger(__name__)

class ReminderManager:
    def __init__(self, memory_file: str = "reminders.json"):
        self.memory_file = memory_file
        self.reminders: List[Dict] = []
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._load()

    def _load(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.reminders = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load reminders: {e}")
                self.reminders = []

    def _save(self):
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.reminders, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save reminders: {e}")

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("ReminderManager started.")

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        logger.info("ReminderManager stopped.")

    def _run_loop(self):
        while self.running:
            now = datetime.now(timezone.utc).timestamp()
            triggered = []
            for r in self.reminders:
                if r['time'] <= now and not r.get('triggered', False):
                    self._trigger_reminder(r)
                    r['triggered'] = True
                    triggered.append(r)
            
            if triggered:
                self.reminders = [r for r in self.reminders if not r.get('triggered', False)]
                self._save()
            
            time.sleep(10)

    def _trigger_reminder(self, reminder: Dict):
        try:
            notification.notify(
                title="Reminder",
                message=reminder['text'],
                app_name="Megatron",
                timeout=10
            )
            logger.info(f"Triggered reminder: {reminder['text']}")
        except Exception as e:
            logger.error(f"Failed to trigger notification: {e}")

    def set_reminder(self, text: str, time_str: str, language: str = 'en') -> str:
        parsed_date = dateparser.parse(time_str, settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True})
        if not parsed_date:
            return "Could not parse the time."
        
        rem = {
            "id": str(int(time.time() * 1000)),
            "text": text,
            "time": parsed_date.timestamp(),
            "language": language,
            "triggered": False
        }
        self.reminders.append(rem)
        self._save()
        return f"Reminder set for {parsed_date.strftime('%Y-%m-%d %H:%M:%S %Z')}."

    def cancel_reminder(self, reminder_id: str) -> bool:
        initial_len = len(self.reminders)
        self.reminders = [r for r in self.reminders if r['id'] != reminder_id]
        if len(self.reminders) < initial_len:
            self._save()
            return True
        return False

    def list_reminders(self) -> List[Dict]:
        return self.reminders
