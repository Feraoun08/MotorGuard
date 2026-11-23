import logging
import threading

import paho.mqtt.client as mqtt

from backend.config import BackendConfig
from backend.ingestion.service import TelemetryIngestionService

logger = logging.getLogger("motorguard.backend.mqtt.consumer")

TELEMETRY_SUBSCRIPTION = (
    "motorguard/factories/+/motors/+/telemetry"
)


class BackendMQTTConsumer:

    def __init__(
        self,
        config: BackendConfig,
        ingestion_service: TelemetryIngestionService,
    ):
        self.config = config
        self.ingestion_service = ingestion_service

        self.connected_event = threading.Event()
        self.shutdown_event = threading.Event()

        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=config.mqtt_client_id,
            protocol=mqtt.MQTTv311,
            clean_session=False,
        )

        if config.mqtt_username:
            self.client.username_pw_set(
                config.mqtt_username,
                config.mqtt_password,
            )

        self.client.reconnect_delay_set(
            min_delay=1,
            max_delay=30,
        )

        self.client.manual_ack_set(True)

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        self._loop_started = False
        self._connected = False

    def _on_connect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties,
    ):

        if reason_code == 0:

            self._connected = True
            self.connected_event.set()

            logger.info(
                "Backend connected to MQTT broker "
                "%s:%s",
                self.config.mqtt_host,
                self.config.mqtt_port,
            )

            result, mid = client.subscribe(
                TELEMETRY_SUBSCRIPTION,
                qos=self.config.mqtt_qos,
            )

            if result != mqtt.MQTT_ERR_SUCCESS:

                logger.error(
                    "MQTT subscription failed: %s",
                    result,
                )

            else:

                logger.info(
                    "Subscribed to %s at QoS %s",
                    TELEMETRY_SUBSCRIPTION,
                    self.config.mqtt_qos,
                )

        else:

            self._connected = False
            self.connected_event.clear()

            logger.error(
                "MQTT connection rejected: %s",
                reason_code,
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
        self.connected_event.clear()

        if not self.shutdown_event.is_set():

            logger.warning(
                "MQTT connection lost: %s",
                reason_code,
            )

    def _on_message(
        self,
        client,
        userdata,
        message,
    ):

        try:

            outcome = self.ingestion_service.ingest(
                topic=message.topic,
                raw_payload=message.payload,
            )

            if outcome in (
                "accepted",
                "duplicate",
                "rejected",
            ):

                client.ack(
                    message.mid,
                    message.qos,
                )

            elif outcome == "database_error":

                logger.error(
                    "Message not acknowledged because "
                    "database registration failed | topic=%s",
                    message.topic,
                )

            else:

                logger.error(
                    "Unexpected ingestion result: %s",
                    outcome,
                )

        except Exception:

            logger.exception(
                "Unexpected MQTT handler error | topic=%s",
                message.topic,
            )

    def connect(self) -> bool:

        self.shutdown_event.clear()
        self.connected_event.clear()

        try:

            logger.info(
                "Connecting backend consumer to MQTT "
                "%s:%s",
                self.config.mqtt_host,
                self.config.mqtt_port,
            )

            self.client.connect(
                host=self.config.mqtt_host,
                port=self.config.mqtt_port,
                keepalive=self.config.mqtt_keepalive,
            )

            self.client.loop_start()
            self._loop_started = True

            return self.connected_event.wait(
                timeout=10
            )

        except Exception:

            logger.exception(
                "Backend MQTT connection failed"
            )

            self.disconnect()
            return False

    def disconnect(self):

        self.shutdown_event.set()

        try:

            if self._connected:
                self.client.disconnect()

        except Exception:

            logger.exception(
                "Backend MQTT disconnect error"
            )

        if self._loop_started:

            self.client.loop_stop()
            self._loop_started = False

        self._connected = False
        self.connected_event.clear()

        logger.info(
            "Backend MQTT consumer stopped"
        )

    @property
    def is_connected(self) -> bool:

        return self._connected