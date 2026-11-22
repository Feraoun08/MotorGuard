"""
MotorGuard MQTT Subscriber.

Receives telemetry from the MQTT broker independently of the simulator.

Responsibilities:
- Connect to the MQTT broker.
- Subscribe to MotorGuard motor telemetry.
- Validate incoming MQTT topics.
- Decode JSON payloads.
- Validate telemetry using the existing telemetry contract.
- Handle malformed messages without crashing the subscriber.
- Display valid telemetry.
- Maintain reception statistics.
- Gracefully disconnect.
"""

import json
import logging
import threading
from typing import Any

import paho.mqtt.client as mqtt

from communication.mqtt_config import MQTTConfig
from communication.mqtt_topics import all_telemetry_topic
from simulator.telemetry import (
    deserialize_telemetry,
    validate_json_schema,
)


logger = logging.getLogger("motor_guard.mqtt.subscriber")


class MQTTSubscriber:
    """Independent MQTT telemetry receiver."""

    def __init__(self, config: MQTTConfig):
        self.config = config

        self._connected_event = threading.Event()
        self._shutdown_event = threading.Event()

        # A subscriber must use a unique client ID.
        # Do not reuse the publisher's MQTT client ID.
        subscriber_client_id = f"{config.client_id}_subscriber"

        self._client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=subscriber_client_id,
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
        self._client.on_subscribe = self._on_subscribe
        self._client.on_message = self._on_message

        self._loop_started = False
        self._connected = False

        self.received_count = 0
        self.valid_count = 0
        self.invalid_count = 0
        self.topic_error_count = 0
        self.json_error_count = 0
        self.telemetry_error_count = 0

   
    # CONNECTION CALLBACKS
   

    def _on_connect(
        self,
        client,
        userdata,
        connect_flags,
        reason_code,
        properties,
    ):
        if reason_code != 0:
            self._connected = False
            self._connected_event.clear()

            logger.error(
                "MQTT subscriber connection rejected: %s",
                reason_code,
            )
            return

        self._connected = True
        self._connected_event.set()

        logger.info(
            "MQTT subscriber connected to %s:%s",
            self.config.host,
            self.config.port,
        )

        topic = all_telemetry_topic()

        result, mid = client.subscribe(
            topic,
            qos=self.config.qos,
        )

        if result != mqtt.MQTT_ERR_SUCCESS:
            logger.error(
                "Subscription request failed. Topic=%s rc=%s",
                topic,
                result,
            )
            return

        logger.info(
            "Subscription requested | topic=%s | qos=%s",
            topic,
            self.config.qos,
        )

    def _on_disconnect(
        self,
        client,
        userdata,
        disconnect_flags,
        reason_code,
        properties,
    ):
        self._connected = False
        self._connected_event.clear()

        if not self._shutdown_event.is_set():
            logger.warning(
                "MQTT subscriber disconnected. Reason=%s",
                reason_code,
            )

    def _on_subscribe(
        self,
        client,
        userdata,
        mid,
        reason_code_list,
        properties,
    ):
        logger.info(
            "MQTT subscription acknowledged. MID=%s reasons=%s",
            mid,
            reason_code_list,
        )

   
    # TOPIC VALIDATION
   

    @staticmethod
    def _validate_topic(topic: str) -> tuple[str, str]:
        """
        Validate the expected topic structure.

        Expected:
        motorguard/factories/{factory_id}/motors/{motor_id}/telemetry
        """

        parts = topic.split("/")

        if len(parts) != 6:
            raise ValueError(
                f"Unexpected topic structure: {topic}"
            )

        if parts[0] != "motorguard":
            raise ValueError("Invalid topic root")

        if parts[1] != "factories":
            raise ValueError("Expected 'factories' segment")

        if parts[3] != "motors":
            raise ValueError("Expected 'motors' segment")

        if parts[5] != "telemetry":
            raise ValueError("Expected 'telemetry' segment")

        factory_id = parts[2]
        motor_id = parts[4]

        if not factory_id or not motor_id:
            raise ValueError(
                "Factory ID and motor ID must not be empty"
            )

        # Reject wildcard characters and invalid identifier characters.
        allowed_characters = (
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789_-"
        )

        if any(char not in allowed_characters for char in factory_id):
            raise ValueError(
                f"Invalid factory ID in topic: {factory_id}"
            )

        if any(char not in allowed_characters for char in motor_id):
            raise ValueError(
                f"Invalid motor ID in topic: {motor_id}"
            )

        return factory_id, motor_id

   
    # MESSAGE CALLBACK
   

    def _on_message(self, client, userdata, message):
        """
        Process incoming telemetry safely.

        Invalid messages are logged and counted.
        The subscriber remains operational.
        """

        self.received_count += 1

        topic = message.topic

        logger.info(
            "MQTT message received | topic=%s | bytes=%s",
            topic,
            len(message.payload),
        )

       
        # 1. VALIDATE TOPIC
       

        try:
            factory_id, motor_id = self._validate_topic(topic)

        except ValueError as exc:
            self.invalid_count += 1
            self.topic_error_count += 1

            logger.error(
                "Invalid MQTT topic. Message rejected. "
                "Topic=%s Error=%s",
                topic,
                exc,
            )
            return

       
        # 2. DECODE UTF-8
       

        try:
            payload_text = message.payload.decode("utf-8")

        except UnicodeDecodeError as exc:
            self.invalid_count += 1
            self.json_error_count += 1

            logger.error(
                "Payload is not valid UTF-8. Topic=%s Error=%s",
                topic,
                exc,
            )
            return

       
        # 3. JSON CHECK
       

        try:
            json.loads(payload_text)

        except json.JSONDecodeError as exc:
            self.invalid_count += 1
            self.json_error_count += 1

            logger.error(
                "Malformed JSON received. Topic=%s Error=%s",
                topic,
                exc,
            )
            return

       
        # 4. TELEMETRY VALIDATION
       

        try:
            telemetry = deserialize_telemetry(payload_text)
            validate_json_schema(telemetry)

        except Exception as exc:
            self.invalid_count += 1
            self.telemetry_error_count += 1

            logger.error(
                "Telemetry validation failed. "
                "Topic=%s Error=%s",
                topic,
                exc,
            )
            return

       
        # 5. TOPIC / PAYLOAD CONSISTENCY
       

        if telemetry.get("factory_id") != factory_id:
            self.invalid_count += 1
            self.telemetry_error_count += 1

            logger.error(
                "Factory ID mismatch. Topic factory=%s "
                "Payload factory=%s",
                factory_id,
                telemetry.get("factory_id"),
            )
            return

        if telemetry.get("motor_id") != motor_id:
            self.invalid_count += 1
            self.telemetry_error_count += 1

            logger.error(
                "Motor ID mismatch. Topic motor=%s "
                "Payload motor=%s",
                motor_id,
                telemetry.get("motor_id"),
            )
            return

       
        # 6. VALID TELEMETRY
       

        self.valid_count += 1

        self._display_telemetry(topic, telemetry)

   
    # TELEMETRY DISPLAY
   

    @staticmethod
    def _display_telemetry(topic: str, telemetry: dict[str, Any]):
        """Display validated telemetry."""

        print("\n" + "=" * 80)
        print("MOTORGUARD - VALID MQTT TELEMETRY RECEIVED")
        print("=" * 80)

        print(f"Topic            : {topic}")
        print(f"Schema Version   : {telemetry.get('schema_version')}")
        print(f"Timestamp        : {telemetry.get('timestamp')}")
        print(f"Factory         : {telemetry.get('factory_id')}")
        print(f"Motor ID       : {telemetry.get('motor_id')}")
        print(f"Motor Name     : {telemetry.get('motor_name')}")
        print(f"Line           : {telemetry.get('line_id')}")
        print(f"Motor State    : {telemetry.get('motor_state')}")
        print(f"Bearing         : {telemetry.get('bearing_condition')}")
        print(f"Ground Truth   : {telemetry.get('ground_truth')}")

        print("\nVIBRATION FEATURES")
        print("-" * 80)

        for feature, value in telemetry.get("vibration", {}).items():
            print(f"{feature:15}: {value}")

        print("\nSYNTHETIC SENSORS")
        print("-" * 80)

        for sensor, value in telemetry.get("sensors", {}).items():
            print(f"{sensor:15}: {value}")

        print("\nSIMULATION METADATA")
        print("-" * 80)

        for key, value in telemetry.get("simulation", {}).items():
            print(f"{key:25}: {value}")

        print("=" * 80)

   
    # START
   

    def connect(self) -> bool:
        """
        Connect to broker and start the MQTT loop.

        Returns True when connected, False on timeout/failure.
        """

        if self._connected:
            logger.info("MQTT subscriber already connected.")
            return True

        self._shutdown_event.clear()
        self._connected_event.clear()

        try:
            logger.info(
                "Connecting subscriber to %s:%s...",
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
                    "Subscriber connection timeout after %s seconds.",
                    self.config.connect_timeout,
                )

                self.disconnect()
                return False

            return True

        except (OSError, mqtt.MQTTException) as exc:
            logger.error(
                "MQTT subscriber connection failed: %s",
                exc,
            )

            self.disconnect()
            return False

   
    # STATISTICS
   

    def get_statistics(self) -> dict:
        """Return subscriber message statistics."""

        return {
            "received": self.received_count,
            "valid": self.valid_count,
            "invalid": self.invalid_count,
            "topic_errors": self.topic_error_count,
            "json_errors": self.json_error_count,
            "telemetry_errors": self.telemetry_error_count,
        }

   
    # SHUTDOWN
   

    def disconnect(self):
        """Disconnect cleanly and stop the network loop."""

        self._shutdown_event.set()

        try:
            if self._connected:
                logger.info("Disconnecting MQTT subscriber...")
                self._client.disconnect()

        except Exception:
            logger.exception(
                "Error while disconnecting MQTT subscriber."
            )

        finally:
            self._connected = False
            self._connected_event.clear()

            if self._loop_started:
                self._client.loop_stop()
                self._loop_started = False

            logger.info("MQTT subscriber stopped.")

    @property
    def is_connected(self) -> bool:
        return self._connected