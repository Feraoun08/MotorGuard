"""

Connects FactoryEngine telemetry callbacks to the MQTT publisher.

"""

import logging
from typing import Any

from communication.mqtt_publisher import MQTTPublisher

logger = logging.getLogger("motor_guard.mqtt.adapter")


class MQTTFactoryAdapter:
    """
    Adapter between FactoryEngine and MQTTPublisher.
    """

    def __init__(self, publisher: MQTTPublisher):
        self.publisher = publisher
        self.published_count = 0
        self.failed_count = 0

    def __call__(self, reading: dict[str, Any]) -> None:
        """
        Called by FactoryEngine whenever a motor reading is generated.
        """

        motor_id = reading.get("motor_id", "UNKNOWN")

        success = self.publisher.publish_reading(reading)

        if success:
            self.published_count += 1

            logger.info(
                "Factory telemetry forwarded to MQTT | motor=%s | published=%s",
                motor_id,
                self.published_count,
            )
        else:
            self.failed_count += 1

            logger.warning(
                "Factory telemetry could not be published | motor=%s | failures=%s",
                motor_id,
                self.failed_count,
            )

    def get_statistics(self) -> dict:
        """Return adapter publication statistics."""

        return {
            "published": self.published_count,
            "failed": self.failed_count,
            "total": self.published_count + self.failed_count,
        }