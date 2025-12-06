"""Parse incoming messages to detect vibecode requests."""

import logging
import re
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class VibeCodeRequest:
    """Parsed vibecode request."""

    sender_phone: str  # Phone number to reply to
    chat_id: str  # Chat/conversation ID
    prompt: str  # What to generate (e.g., "a pac man game")
    raw_message: str  # Original message text


class MessageParser:
    """Parse Kafka messages to extract vibecode requests."""

    # Patterns to match vibecode requests
    # Examples:
    #   "vibecode this: a pac man game"
    #   "vibecode: make a calculator"
    #   "vibe code a todo app"
    #   "vibecoder: create a snake game"
    VIBECODE_PATTERNS = [
        r"vibecode\s*(?:this)?:?\s*(.+)",
        r"vibe\s*code\s*(?:this)?:?\s*(.+)",
        r"(?:hey\s+)?vibecoder:?\s*(.+)",
    ]

    def __init__(self):
        self.patterns = [
            re.compile(p, re.IGNORECASE | re.DOTALL) for p in self.VIBECODE_PATTERNS
        ]

    def parse(self, message: dict) -> Optional[VibeCodeRequest]:
        """
        Parse a Kafka message to extract vibecode request.

        The message format is unknown, so we try multiple common field names.
        Raw messages are logged for debugging.
        """
        try:
            # Log raw message for format discovery
            logger.debug(f"Raw Kafka message: {message}")

            # Extract text - try multiple possible field names
            text = self._extract_field(
                message, ["text", "body", "message", "content", "data.text", "data.body"]
            )

            if not text:
                logger.debug("Message has no text content")
                return None

            # Extract sender phone
            sender_phone = self._extract_field(
                message,
                [
                    "sender",
                    "from",
                    "phone",
                    "sender_phone",
                    "from_phone",
                    "data.sender",
                    "data.from",
                ],
            )

            # Extract chat/conversation ID
            chat_id = self._extract_field(
                message,
                [
                    "chat_id",
                    "conversation_id",
                    "thread_id",
                    "id",
                    "data.chat_id",
                    "data.conversation_id",
                ],
            )

            if not sender_phone:
                logger.warning(f"Message missing sender phone: {message}")
                return None

            # Try each pattern to match vibecode request
            for pattern in self.patterns:
                match = pattern.search(text)
                if match:
                    prompt = match.group(1).strip()
                    if prompt:
                        logger.info(
                            f"Parsed vibecode request: '{prompt}' from {sender_phone}"
                        )
                        return VibeCodeRequest(
                            sender_phone=sender_phone,
                            chat_id=chat_id or sender_phone,
                            prompt=prompt,
                            raw_message=text,
                        )

            # Not a vibecode request
            logger.debug(f"Message is not a vibecode request: {text[:50]}...")
            return None

        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return None

    def _extract_field(self, data: dict, field_names: list) -> Optional[str]:
        """Try to extract a field using multiple possible names."""
        for name in field_names:
            # Handle nested fields (e.g., "data.text")
            if "." in name:
                parts = name.split(".")
                value = data
                for part in parts:
                    if isinstance(value, dict):
                        value = value.get(part)
                    else:
                        value = None
                        break
                if value is not None:
                    return str(value)
            else:
                value = data.get(name)
                if value is not None:
                    return str(value)
        return None
