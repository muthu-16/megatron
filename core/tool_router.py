import re
from typing import Tuple, Dict, Any

class ToolRouter:
    """
    Intent classifier and tool dispatcher for Megatron.
    Uses regex pattern matching for fast routing.
    """
    
    # Destructive intents that require security flows
    DESTRUCTIVE_INTENTS = ["delete memory", "reset", "unlink", "format", "erase"]
    
    def __init__(self):
        # A simple keyword to tool mapping for multiple languages
        self.routes = {
            "search": [r"\bsearch for\b", r"\bbuscar\b", r"\bchercher\b", r"खोज", r"தேடு"],
            "news": [r"\bnews\b", r"\bnoticias\b", r"\bnouvelles\b", r"समाचार", r"செய்திகள்"],
            "weather": [r"\bweather\b", r"\bclima\b", r"\bmétéo\b", r"मौसम", r"வானிலை"],
            "flights": [r"\bflight\b", r"\bvuelo\b", r"\bvol\b", r"उड़ान", r"விமானம்"],
            "screen_vision": [r"\bon my screen\b", r"\ben mi pantalla\b", r"\bsur mon écran\b", r"मेरी स्क्रीन पर", r"என் திரையில்"],
            "reminders": [r"\bremind me\b", r"\brecuérdame\b", r"\brappelle-moi\b", r"मुझे याद दिलाएं", r"எனக்கு நினைவூட்டு"],
            "system_monitor": [r"\bsystem status\b", r"\bcpu\b", r"\bram\b"],
            "computer_control": [r"\bopen\b", r"\blaunch\b", r"\babrir\b", r"\bouvrir\b"],
            "mobile_automation": [r"\bopen on phone\b", r"\bcall\b"],
            "browser_control": [r"\bgo to\b", r"\bwebsite\b"],
            "file_handler": [r"\bread file\b", r"\bcreate file\b"],
            "messaging": [r"\bsend message\b", r"\btext\b", r"\bwhatsapp\b", r"\btelegram\b"],
            "youtube_control": [r"\byoutube\b"],
            "game_updater": [r"\bupdate game\b", r"\bpatch\b"],
            "code_helper": [r"\bwrite code\b", r"\bdebug\b", r"\bfix error\b"],
            "settings_control": [r"\bchange setting\b", r"\bchange volume\b", r"\bbrightness\b"],
            "memory_query": [r"\bwhat do you remember\b", r"\bdelete memory\b", r"\berase\b"],
            "proactive": [r"\bwhat's up\b", r"\bbriefing\b"],
            "help": [r"\bhelp\b", r"\bayuda\b", r"\baide\b", r"मदद", r"உதவி"]
        }

    def route(self, text: str, language: str = 'en') -> Tuple[str, Dict[str, Any]]:
        """
        Routes the text to the appropriate tool.
        Returns (tool_name, params)
        """
        text_lower = text.lower()
        
        # Check for destructive intent flag
        requires_security = any(keyword in text_lower for keyword in self.DESTRUCTIVE_INTENTS)
        
        # Fast keyword match
        for tool_name, patterns in self.routes.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return tool_name, {"text": text, "requires_security": requires_security}
                    
        # Default fallback
        return "chat", {"text": text, "requires_security": False}
