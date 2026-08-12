import logging
import urllib.parse
import webbrowser
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class MessagingController:
    """Controls sending messages via WhatsApp, Telegram, SMS, etc."""

    def __init__(self):
        pass

    def send_whatsapp(self, contact: str, message: str, lang: str = "en") -> bool:
        """
        Send a WhatsApp message using WhatsApp Web URI scheme.
        Requires the user to hit 'send' or can be automated further with Selenium/pywhatkit.
        """
        try:
            # Basic validation
            if not contact:
                logger.error("Contact number is required for WhatsApp.")
                return False
                
            # Strip non-numeric from contact if it's a number
            clean_contact = ''.join(filter(lambda x: x.isdigit() or x == '+', contact))
            encoded_msg = urllib.parse.quote(message)
            
            # Use api.whatsapp.com
            url = f"https://api.whatsapp.com/send?phone={clean_contact}&text={encoded_msg}"
            webbrowser.open(url)
            logger.info(f"Opened WhatsApp Web to send message to {clean_contact} (lang: {lang})")
            return True
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False

    def send_telegram(self, chat_id: str, message: str, token: str) -> bool:
        """
        Send a Telegram message using the Telegram Bot API.
        """
        try:
            import requests
            
            if not token or not chat_id:
                logger.error("Telegram bot token and chat_id are required.")
                return False
                
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message
            }
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                logger.info(f"Telegram message sent to {chat_id}")
                return True
            else:
                logger.error(f"Failed to send Telegram message: {response.text}")
                return False
        except ImportError:
            logger.error("requests module is required to send Telegram messages.")
            return False
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    def send_sms(self, phone_number: str, message: str) -> bool:
        """
        Stub for sending SMS (e.g., via Twilio).
        """
        logger.info(f"SMS Stub: Sending to {phone_number} -> {message}")
        return True

    def read_notifications(self) -> str:
        """
        Stub for reading system or messaging notifications.
        """
        logger.info("Reading notifications stub.")
        return "No new notifications."

    def compose_message(self, topic: str, context: str = "") -> str:
        """
        Draft a message based on a topic and context using LLM (stubbed).
        """
        logger.info(f"Drafting message for topic: {topic}")
        # In a real scenario, this would call an LLM API
        draft = f"Draft message regarding: {topic}. Context: {context}"
        return draft
