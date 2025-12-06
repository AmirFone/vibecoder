"""Twilio SMS client for sending messages."""

import logging
from typing import Optional

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from config import config

logger = logging.getLogger(__name__)


class TwilioClient:
    """Client for sending SMS via Twilio."""

    def __init__(self):
        self.client = Client(config.twilio_account_sid, config.twilio_auth_token)
        self.from_number = config.twilio_phone_number

    def send_sms(self, to_number: str, body: str) -> bool:
        """
        Send an SMS message via Twilio.

        Args:
            to_number: The recipient phone number (e.g., +13474326467)
            body: The message body

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Ensure phone number has + prefix
            if not to_number.startswith("+"):
                to_number = f"+{to_number}"

            logger.info(f"Sending SMS to {to_number}")

            message = self.client.messages.create(
                body=body,
                from_=self.from_number,
                to=to_number
            )

            logger.info(f"SMS sent successfully! SID: {message.sid}")
            return True

        except TwilioRestException as e:
            logger.error(f"Twilio error: {e.msg}")
            return False
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False

    def send_creation_url(
        self,
        phone_number: str,
        url: str,
        prompt: str,
    ) -> bool:
        """Send the URL of a generated creation."""
        message = f"Your creation is ready!\n\n{url}"
        return self.send_sms(phone_number, message)

    def send_error(
        self,
        phone_number: str,
        error_message: str = "Sorry, I couldn't generate that. Please try again!",
    ) -> bool:
        """Send an error message."""
        return self.send_sms(phone_number, error_message)

    def send_processing(
        self,
        phone_number: str,
        prompt: str,
    ) -> bool:
        """Send a processing notification."""
        message = f"Creating your \"{prompt}\"... This may take a moment!"
        return self.send_sms(phone_number, message)
