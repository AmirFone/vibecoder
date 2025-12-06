"""Configuration management for Vibecoder."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env file
load_dotenv()


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    # Kafka
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "")
    kafka_topic: str = os.getenv("KAFKA_TOPIC", "")
    kafka_consumer_group: str = os.getenv("KAFKA_CONSUMER_GROUP", "vibecoder")
    kafka_sasl_username: str = os.getenv("KAFKA_SASL_USERNAME", "")
    kafka_sasl_password: str = os.getenv("KAFKA_SASL_PASSWORD", "")

    # Claude API
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    claude_model: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")

    # Series API
    series_api_base: str = os.getenv("SERIES_API_BASE", "")
    series_api_key: str = os.getenv("SERIES_API_KEY", "")
    series_sender_phone: str = os.getenv("SERIES_SENDER_PHONE", "")

    # Twilio SMS
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_phone_number: str = os.getenv("TWILIO_PHONE_NUMBER", "")

    # HTTP Server
    http_host: str = os.getenv("HTTP_HOST", "0.0.0.0")
    http_port: int = int(os.getenv("HTTP_PORT", "8080"))
    public_url_base: str = os.getenv("PUBLIC_URL_BASE", "http://localhost:8080")

    # Storage
    generated_html_dir: str = os.getenv("GENERATED_HTML_DIR", "./generated")


# Global config instance
config = Config()
