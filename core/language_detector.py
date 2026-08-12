from typing import Tuple, List
import yaml
from pathlib import Path
import langdetect

class LanguageDetector:
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / "config" / "language_config.yaml"
        self.languages = self._load_language_config()

    def _load_language_config(self) -> dict:
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config.get("languages", {})
        except Exception:
            return {}

    def detect_from_audio(self, audio_bytes: bytes) -> Tuple[str, float]:
        """
        Stub for audio language detection (e.g. Whisper language detection).
        Returns language_code, confidence.
        """
        # Placeholder for actual Whisper integration
        return ("en", 0.99)

    def detect_from_text(self, text: str) -> str:
        """
        Detects language from text using langdetect.
        """
        try:
            lang = langdetect.detect(text)
            if lang in self.languages:
                return lang
        except Exception:
            pass
        return "en" # Fallback

    def detect_code_switch(self, text: str) -> List[Tuple[str, str]]:
        """
        Detects code-switching by segmenting text and identifying languages.
        Simple stub returning the whole text as detected main language.
        """
        main_lang = self.detect_from_text(text)
        return [(text, main_lang)]

    def get_tts_voice(self, language_code: str, gender: str = 'female') -> str:
        """
        Returns edge-tts voice name for the given language and gender.
        """
        lang_info = self.languages.get(language_code)
        if lang_info:
            if gender == 'male':
                return lang_info.get("edge_tts_voice_male", "")
            else:
                return lang_info.get("edge_tts_voice_female", "")
        # Fallback to English female
        return self.languages.get("en", {}).get("edge_tts_voice_female", "en-US-JennyNeural")

    def get_whisper_language(self, language_code: str) -> str:
        """
        Returns Whisper language code.
        """
        lang_info = self.languages.get(language_code)
        if lang_info:
            return lang_info.get("whisper_code", "en")
        return "en"
