"""
Vibecoder - iMessage to HTML Generator

Main entry point that orchestrates all components:
1. Start HTTP server for serving generated pages
2. Start Kafka consumer for receiving iMessages
3. Process vibecode requests via Claude API
4. Send URLs back via Series iMessage API
"""

import logging
import signal
import sys

from config import config
from claude_generator import ClaudeGenerator
from file_manager import FileManager
from http_server import HTTPServer
from kafka_consumer import KafkaMessageConsumer
from message_parser import MessageParser, VibeCodeRequest
from series_client import SeriesClient
from twilio_client import TwilioClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Vibecoder:
    """Main application orchestrator."""

    def __init__(self):
        self.parser = MessageParser()
        self.generator = ClaudeGenerator()
        self.file_manager = FileManager()
        self.http_server = HTTPServer()
        self.series_client = SeriesClient()
        self.twilio_client = TwilioClient()
        self.kafka_consumer = None

    def handle_message(self, message: dict):
        """Process an incoming Kafka message."""
        # Parse the message
        request = self.parser.parse(message)

        if not request:
            # Not a vibecode request, ignore
            return

        self._process_request(request)

    def _process_request(self, request: VibeCodeRequest):
        """Process a vibecode request."""
        logger.info(f"Processing vibecode request: {request.prompt}")

        try:
            # Generate HTML via Claude
            logger.info("Generating HTML with Claude...")
            html_content = self.generator.generate_html(request.prompt)

            if not html_content:
                logger.error("Failed to generate HTML")
                print("\n" + "=" * 60)
                print("ERROR: Failed to generate HTML")
                print("=" * 60 + "\n")
                return

            # Save to file
            filename = self.file_manager.save_html(html_content, request.prompt)

            # Get public URL
            url = self.http_server.get_url(filename)

            # Print URL prominently
            print("\n" + "=" * 60)
            print("YOUR CREATION IS READY!")
            print("=" * 60)
            print(f"Prompt: {request.prompt}")
            print(f"URL: {url}")
            print("=" * 60 + "\n")

            # Send URL via Twilio SMS
            if request.sender_phone:
                logger.info(f"Sending URL to {request.sender_phone} via Twilio...")
                if self.twilio_client.send_creation_url(
                    request.sender_phone, url, request.prompt
                ):
                    logger.info("SMS sent successfully!")
                else:
                    logger.warning("Failed to send SMS, but URL is still available")

            logger.info(f"Successfully processed request: {request.prompt}")

        except Exception as e:
            logger.error(f"Error processing request: {e}")

    def run(self):
        """Run the Vibecoder application."""
        logger.info("=" * 50)
        logger.info("Starting Vibecoder...")
        logger.info("=" * 50)

        # Validate config
        if not config.anthropic_api_key:
            logger.error("ANTHROPIC_API_KEY not set!")
            sys.exit(1)
        if not config.kafka_bootstrap_servers:
            logger.error("KAFKA_BOOTSTRAP_SERVERS not set!")
            sys.exit(1)
        if not config.series_api_key:
            logger.error("SERIES_API_KEY not set!")
            sys.exit(1)

        # Start HTTP server
        self.http_server.start()
        logger.info(f"HTTP server running at {config.public_url_base}")

        # Start Kafka consumer
        self.kafka_consumer = KafkaMessageConsumer(self.handle_message)

        # Handle graceful shutdown
        def shutdown(signum, frame):
            logger.info("\nShutting down...")
            if self.kafka_consumer:
                self.kafka_consumer.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        logger.info("Starting Kafka consumer...")
        logger.info(f"Listening on topic: {config.kafka_topic}")
        logger.info("Send 'vibecode: [your idea]' via iMessage to create something!")
        logger.info("=" * 50)

        # Start consuming (blocking)
        self.kafka_consumer.start()


def main():
    """Entry point."""
    app = Vibecoder()
    app.run()


if __name__ == "__main__":
    main()
