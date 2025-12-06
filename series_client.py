"""Series iMessage API client for sending messages."""

import logging
from typing import Optional

import requests

from config import config

logger = logging.getLogger(__name__)


class SeriesClient:
    """Client for Series iMessage API."""

    def __init__(self):
        self.api_base = config.series_api_base.rstrip("/")
        self.api_key = config.series_api_key
        self.sender_phone = config.series_sender_phone

    def _get_headers(self) -> dict:
        """Get headers for API requests."""
        return {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

    def send_message_to_chat(
        self, chat_id: str, message: str
    ) -> bool:
        """
        Send a message to an existing chat.

        POST /api/chats/{chat_id}/chat_messages
        """
        try:
            url = f"{self.api_base}/api/chats/{chat_id}/chat_messages"
            payload = {"message": {"text": [message]}}

            logger.info(f"Sending message to chat {chat_id}")

            response = requests.post(
                url, json=payload, headers=self._get_headers(), timeout=30
            )

            if response.status_code in (200, 201, 202):
                logger.info(f"Message sent successfully to chat {chat_id}")
                return True
            else:
                logger.error(
                    f"Failed to send message: {response.status_code} - {response.text}"
                )
                return False

        except requests.RequestException as e:
            logger.error(f"Error sending message to chat: {e}")
            return False

    def create_chat_and_send(
        self, phone_number: str, message: str
    ) -> bool:
        """
        Create a new chat and send a message.

        POST /api/chats
        """
        try:
            url = f"{self.api_base}/api/chats"
            payload = {
                "chat": {"phone_numbers": [phone_number]},
                "message": {"text": [message]},
                "send_from": self.sender_phone,
            }

            logger.info(f"Creating chat and sending message to {phone_number}")

            response = requests.post(
                url, json=payload, headers=self._get_headers(), timeout=30
            )

            if response.status_code in (200, 201, 202):
                logger.info(f"Chat created and message sent to {phone_number}")
                return True
            else:
                logger.error(
                    f"Failed to create chat: {response.status_code} - {response.text}"
                )
                return False

        except requests.RequestException as e:
            logger.error(f"Error creating chat: {e}")
            return False

    def send_message(
        self, phone_number: str, message: str, chat_id: Optional[str] = None
    ) -> bool:
        """
        Send a message - try chat first, then create new chat.
        """
        # If we have a chat_id, try to use it
        if chat_id and chat_id != phone_number:
            if self.send_message_to_chat(chat_id, message):
                return True
            logger.warning(f"Failed to send to chat {chat_id}, trying new chat")

        # Fall back to creating a new chat
        return self.create_chat_and_send(phone_number, message)

    def send_creation_url(
        self,
        phone_number: str,
        url: str,
        prompt: str,
        chat_id: Optional[str] = None,
    ) -> bool:
        """Send the URL of a generated creation."""
        message = f"Here's your creation!\n\n{url}"
        return self.send_message(phone_number, message, chat_id)

    def send_error(
        self,
        phone_number: str,
        error_message: str = "Sorry, I couldn't generate that. Please try again with a different description!",
        chat_id: Optional[str] = None,
    ) -> bool:
        """Send an error message."""
        return self.send_message(phone_number, error_message, chat_id)

    def send_processing(
        self,
        phone_number: str,
        prompt: str,
        chat_id: Optional[str] = None,
    ) -> bool:
        """Send a processing notification."""
        message = f"Creating your \"{prompt}\"... This may take a moment!"
        return self.send_message(phone_number, message, chat_id)
