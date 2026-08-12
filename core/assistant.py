import os
import json
import requests
from typing import Generator, List, Dict, Any, Union
try:
    from google import genai
    from google.genai import types
    HAS_GEMINI = True
except ImportError:
    genai = None
    HAS_GEMINI = False

from config.secrets import get_secret
from pathlib import Path

class MegatronAssistant:
    def __init__(self):
        self.gemini_key = get_secret("gemini_api_key")
        self.user_name = get_secret("user_name", "User")
        self.assistant_name = get_secret("assistant_name", "Megatron")
        
        self.gemini_client = None
        if self.gemini_key and HAS_GEMINI:
            self.gemini_client = genai.Client(api_key=self.gemini_key)
            
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        prompt_path = Path(__file__).parent / "prompt.txt"
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                base_prompt = f.read()
        except FileNotFoundError:
            base_prompt = "You are {{assistant_name}}, a highly capable assistant to {{user_name}}."
            
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return base_prompt.replace("{{user_name}}", self.user_name) \
                          .replace("{{assistant_name}}", self.assistant_name) \
                          .replace("{{date_time}}", current_time)

    def chat(self, messages: List[Dict[str, str]], stream: bool = True, language: str = 'en') -> Union[Generator[str, None, None], str]:
        if not self.gemini_client:
            msg = "Gemini API key is not configured. Please set 'gemini_api_key' in config/config.yaml."
            if stream:
                return (chunk for chunk in [msg])
            return msg

        try:
            # Convert messages format to Gemini format
            gemini_messages = []
            for m in messages:
                if m["role"] == "system":
                    continue
                role = "user" if m["role"] == "user" else "model"
                gemini_messages.append({"role": role, "parts": [{"text": m["content"]}]})
                
            config = types.GenerateContentConfig(
                system_instruction=self.system_prompt + f"\n\nRespond in this language: {language}"
            )
            
            if stream:
                response = self.gemini_client.models.generate_content_stream(
                    model='gemini-1.5-flash',
                    contents=gemini_messages,
                    config=config
                )
                def gen():
                    for chunk in response:
                        if chunk.text:
                            yield chunk.text
                return gen()
            else:
                response = self.gemini_client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=gemini_messages,
                    config=config
                )
                return response.text
        except Exception as e:
            msg = f"Gemini API error: {e}"
            print(f"[Assistant] {msg}")
            if stream:
                return (chunk for chunk in [msg])
            return msg

    def summarize_session(self, conversation: List[Dict[str, str]], language: str = 'en') -> str:
        prompt = f"Please provide a short, concise summary of the following conversation in the language '{language}'. Focus on the key facts, decisions, and any action items."
        messages = conversation + [{"role": "user", "content": prompt}]
        summary = self.chat(messages, stream=False, language=language)
        if isinstance(summary, Generator):
            return "".join(summary)
        return summary
