

import logging
import threading
from typing import Any

import paho.mqtt.client as mqtt

from simulator.telemetry import serialize_telemetry
from communication.mqtt_config import MQTTConfig
from communication.mqtt_topics import telemetry_topic


logger = logging.getLogger("motor_guard.mqtt.publisher")


class MQTTPublisher:
    """MQTT publisher for MotorGuard telemetry."""

    def __init__(self, config: MQTTConfig):
        self.config = config

        self._connected_event = threading.Event()
        self._connection_failed_event = threading.Event()
        self._shutdown_event = threading.Event()

        self._client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=config.client_id,
            protocol=mqtt.MQTTv311,
        )

        if config.username:
            self._client.username_pw_set(
                username=config.username,
                password=config.password,
            )

        self._client.reconnect_delay_set(
            min_delay=config.reconnect_min_delay,
            max_delay=config.reconnect_max_delay,
        )

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

        self._client_connected = False
        self._loop_started = False

   
    # MQTT CALLBACKS
   

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self._client_connected = True
            self._connected_event.set()
            self._connection_failed_event.clear()

            logger.info(
                "Connected to MQTT broker %s:%s",
                self.config.host,
                self.config.port,
            )
        else:
            self._client_connected = False
            self._connected_event.clear()

            logger.error(
                "MQTT connection rejected. Reason: %s",
                reason_code,
            )

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        self._client_connected = False
        self._connected_event.clear()

        if not self._shutdown_event.is_set():
            logger.warning(
                "MQTT connection lost. Reason: %s",
                reason_code,
            )

   
    # CONNECTION
   

    def connect(self) -> bool:
        """
        Connect to the broker and start the MQTT network loop.

        Returns:
            True if connection is established.
            False if connection could not be established in time.
        """

        if self._client_connected:
            logger.info("MQTT publisher is already connected.")
            return True

        self._shutdown_event.clear()
        self._connected_event.clear()
        self._connection_failed_event.clear()

        try:
            logger.info(
                "Connecting to MQTT broker %s:%s ...",
                self.config.host,
                self.config.port,
            )

            self._client.connect(
                host=self.config.host,
                port=self.config.port,
                keepalive=self.config.keepalive,
            )

            self._client.loop_start()
            self._loop_started = True

            connected = self._connected_event.wait(
                timeout=self.config.connect_timeout
            )

            if not connected:
                logger.error(
                    "MQTT connection timeout after %s seconds.",
                    self.config.connect_timeout,
                )

                self.disconnect()
                return False

            return True

        except (OSError, mqtt.MQTTException) as exc:
            logger.error("MQTT connection failed: %s", exc)

            self.disconnect()
            return False

   
    # PUBLISHING
   

    def publish_reading(self, reading: dict[str, Any]) -> bool:
        """
        Validate, serialize and publish a simulator reading.
        """

        if not self._client_connected:
            logger.warning(
                "Cannot publish telemetry for motor %s: MQTT disconnected.",
                reading.get("motor_id", "unknown"),
            )
            return False

        try:
            # Existing serializer performs telemetry validation and
            # JSON Schema validation.
            payload = serialize_telemetry(reading)

            topic = telemetry_topic(
                factory_id=reading["factory_id"],
                motor_id=reading["motor_id"],
            )

            result = self._client.publish(
                topic=topic,
                payload=payload,
                qos=self.config.qos,
                retain=False,
            )

            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                logger.error(
                    "MQTT publish failed for motor %s. Return code: %s",
                    reading.get("motor_id"),
                    result.rc,
                )
                return False

            result.wait_for_publish(timeout=self.config.connect_timeout)

            if not result.is_published():
                logger.warning(
                    "Publish not confirmed for motor %s.",
                    reading.get("motor_id"),
                )
                return False

            logger.info(
                "Telemetry published | motor=%s | topic=%s | qos=%s",
                reading["motor_id"],
                topic,
                self.config.qos,
            )

            return True

        except Exception:
            logger.exception(
                "Failed to publish telemetry for motor %s.",
                reading.get("motor_id", "unknown"),
            )
            return False

   
    # SHUTDOWN
   

    def disconnect(self):
        """Disconnect gracefully and stop the MQTT network loop."""

        self._shutdown_event.set()

        try:
            if self._client_connected:
                logger.info("Disconnecting MQTT publisher...")
                self._client.disconnect()

        except Exception:
            logger.exception("Error while disconnecting MQTT publisher.")

        finally:
            self._client_connected = False
            self._connected_event.clear()

            if self._loop_started:
                self._client.loop_stop()
                self._loop_started = False

            logger.info("MQTT publisher stopped.")

   
    # STATUS
   

    @property
    def is_connected(self) -> bool:
        return self._client_connected