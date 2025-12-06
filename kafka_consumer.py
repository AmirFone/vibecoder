"""Kafka consumer for receiving iMessage events."""

import json
import logging
from typing import Callable

from confluent_kafka import Consumer, KafkaException

from config import config

logger = logging.getLogger(__name__)


class KafkaMessageConsumer:
    """Consume messages from Kafka topic."""

    def __init__(self, message_handler: Callable[[dict], None]):
        """
        Initialize consumer with a message handler callback.

        Args:
            message_handler: Function to call for each received message
        """
        self.message_handler = message_handler
        self.consumer = None
        self.running = False

    def _create_consumer(self) -> Consumer:
        """Create Kafka consumer with SASL/SSL configuration."""
        conf = {
            "bootstrap.servers": config.kafka_bootstrap_servers,
            "group.id": config.kafka_consumer_group,
            "auto.offset.reset": "latest",  # Only process new messages
            "enable.auto.commit": True,
            "session.timeout.ms": 30000,
            # SASL Authentication
            "security.protocol": "SASL_SSL",
            "sasl.mechanism": "PLAIN",
            "sasl.username": config.kafka_sasl_username,
            "sasl.password": config.kafka_sasl_password,
        }
        return Consumer(conf)

    def start(self):
        """Start consuming messages (blocking)."""
        self.consumer = self._create_consumer()
        self.consumer.subscribe([config.kafka_topic])
        self.running = True

        logger.info(f"Started consuming from topic: {config.kafka_topic}")
        logger.info(f"Consumer group: {config.kafka_consumer_group}")

        while self.running:
            try:
                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    logger.error(f"Kafka error: {msg.error()}")
                    continue

                # Parse and handle message
                try:
                    value = msg.value()
                    if value:
                        decoded = value.decode("utf-8")
                        logger.info(f"Received raw message: {decoded[:200]}...")

                        data = json.loads(decoded)
                        self.message_handler(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON: {e}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")

            except KafkaException as e:
                logger.error(f"Kafka exception: {e}")
            except Exception as e:
                logger.error(f"Consumer error: {e}")

    def stop(self):
        """Stop consuming."""
        logger.info("Stopping Kafka consumer...")
        self.running = False
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer stopped")
