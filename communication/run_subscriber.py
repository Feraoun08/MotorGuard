"""
MotorGuard standalone MQTT subscriber entry point.

Run independently of the factory simulator to monitor MQTT telemetry.
"""

import logging

from communication.mqtt_config import MQTTConfig
from communication.mqtt_subscriber import MQTTSubscriber


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("motor_guard.subscriber_runner")


def main():
    config = MQTTConfig.from_env()
    subscriber = MQTTSubscriber(config)

    try:
        connected = subscriber.connect()

        if not connected:
            logger.error(
                "Subscriber could not connect to MQTT broker. Exiting."
            )
            return

        logger.info(
            "MotorGuard MQTT subscriber is listening. "
            "Press CTRL+C to stop."
        )

        # Keep the main thread alive while the MQTT background
        # network loop processes incoming messages.
        while True:
            subscriber._shutdown_event.wait(timeout=1)

            if subscriber._shutdown_event.is_set():
                break

    except KeyboardInterrupt:
        logger.info("Shutdown requested by user.")

    finally:
        subscriber.disconnect()

        logger.info(
            "Subscriber statistics: %s",
            subscriber.get_statistics(),
        )


if __name__ == "__main__":
    main()