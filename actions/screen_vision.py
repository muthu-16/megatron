import logging
import base64
import os
from PIL import ImageGrab, Image
import cv2
import requests

logger = logging.getLogger(__name__)

class ScreenVision:
    def __init__(self, openai_api_key: str = ""):
        if openai_api_key:
            self.api_key = openai_api_key
        else:
            try:
                from config.secrets import get_secret
                self.api_key = get_secret("openai_api_key", "") or ""
            except Exception:
                self.api_key = os.environ.get("OPENAI_API_KEY", "")

    def capture_screen(self) -> str:
        try:
            path = "temp_screen.png"
            img = ImageGrab.grab()
            img.save(path)
            return path
        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            return ""

    def capture_webcam(self) -> str:
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if ret:
                path = "temp_webcam.png"
                cv2.imwrite(path, frame)
                return path
            else:
                logger.error("Webcam capture failed (no frame)")
                return ""
        except Exception as e:
            logger.error(f"Webcam capture failed: {e}")
            return ""

    def encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _analyze_with_gpt4o(self, image_path: str, question: str, language: str) -> str:
        if not os.path.exists(image_path):
            return "Image not found."
            
        base64_image = self.encode_image(image_path)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{question} (Respond in {language})"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                    ]
                }
            ],
            "max_tokens": 300
        }
        
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                logger.error(f"GPT-4o API Error: {response.text}")
                return "Analysis failed due to API error."
        except Exception as e:
            logger.error(f"GPT-4o API request failed: {e}")
            return "Analysis failed."

    def analyze_screen(self, question: str, language: str = 'en') -> str:
        logger.info("Analyzing screen")
        path = self.capture_screen()
        if path:
            return self._analyze_with_gpt4o(path, question, language)
        return "Failed to capture screen."

    def analyze_webcam(self, question: str, language: str = 'en') -> str:
        logger.info("Analyzing webcam")
        path = self.capture_webcam()
        if path:
            return self._analyze_with_gpt4o(path, question, language)
        return "Failed to capture webcam."

    def analyze_file_image(self, path: str, question: str, language: str = 'en') -> str:
        logger.info(f"Analyzing file: {path}")
        return self._analyze_with_gpt4o(path, question, language)
