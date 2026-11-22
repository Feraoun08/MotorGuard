

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class MQTTConfig:
    host: str = "localhost"
    port: int = 1883
    client_id: str = "motorguard_publisher"
    username: str | None = None
    password: str | None = None
    keepalive: int = 60
    connect_timeout: int = 10
    qos: int = 1
    reconnect_min_delay: int = 1
    reconnect_max_delay: int = 30

    def __post_init__(self):
        if not self.host.strip():
            raise ValueError("MQTT host cannot be empty")

        if not 1 <= self.port <= 65535:
            raise ValueError("MQTT port must be between 1 and 65535")

        if not self.client_id.strip():
            raise ValueError("MQTT client ID cannot be empty")

        if self.keepalive <= 0:
            raise ValueError("MQTT keepalive must be positive")

        if self.connect_timeout <= 0:
            raise ValueError("MQTT connect timeout must be positive")

        if self.qos not in (0, 1, 2):
            raise ValueError("MQTT QoS must be 0, 1, or 2")

        if self.reconnect_min_delay < 0:
            raise ValueError(
                "MQTT reconnect minimum delay cannot be negative"
            )

        if self.reconnect_max_delay < self.reconnect_min_delay:
            raise ValueError(
                "MQTT reconnect maximum delay must be "
                "greater than or equal to the minimum delay"
            )

    @classmethod
    def from_env(cls) -> "MQTTConfig":
        """
        Build configuration from environment variables.
        """

        return cls(
            host=os.getenv(
                "MQTT_HOST",
                "localhost",
            ),
            port=int(
                os.getenv(
                    "MQTT_PORT",
                    "1883",
                )
            ),
            client_id=os.getenv(
                "MQTT_CLIENT_ID",
                "motorguard_publisher",
            ),
            username=os.getenv(
                "MQTT_USERNAME",
            ) or None,
            password=os.getenv(
                "MQTT_PASSWORD",
            ) or None,
            keepalive=int(
                os.getenv(
                    "MQTT_KEEPALIVE",
                    "60",
                )
            ),
            connect_timeout=int(
                os.getenv(
                    "MQTT_CONNECT_TIMEOUT",
                    "10",
                )
            ),
            qos=int(
                os.getenv(
                    "MQTT_QOS",
                    "1",
                )
            ),
            reconnect_min_delay=int(
                os.getenv(
                    "MQTT_RECONNECT_MIN_DELAY",
                    "1",
                )
            ),
            reconnect_max_delay=int(
                os.getenv(
                    "MQTT_RECONNECT_MAX_DELAY",
                    "30",
                )
            ),
        )
