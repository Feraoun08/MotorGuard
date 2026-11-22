
# MotorGuard MQTT Telemetry Guide

## 1. Overview

MotorGuard uses MQTT to transport simulated motor telemetry
from the virtual factory to an MQTT broker.

The simulator generates telemetry.
The publisher sends telemetry.
The broker distributes telemetry.
The subscriber independently receives and validates telemetry.

---

## 2. MQTT Topic Convention

Motor telemetry:

motorguard/factories/{factory_id}/motors/{motor_id}/telemetry

Example:

motorguard/factories/FACTORY_01/motors/MOTOR_001/telemetry

Subscribe to all motors from a factory:

motorguard/factories/FACTORY_01/motors/+/telemetry

Subscribe to all motors from all factories:

motorguard/factories/+/motors/+/telemetry

---

## 3. Configuration

MQTT configuration is loaded from environment variables.

Example:

MQTT_HOST=localhost
MQTT_PORT=1883
MQTT_CLIENT_ID=motorguard_publisher
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_KEEPALIVE=60
MQTT_CONNECT_TIMEOUT=10
MQTT_QOS=1
MQTT_RECONNECT_MIN_DELAY=1
MQTT_RECONNECT_MAX_DELAY=30

Do not commit production credentials.

---

## 4. Start the MQTT Broker

Start the broker according to your installed MQTT broker setup.

Verify that the broker is listening on the configured host and port.

Default local configuration:

Host: localhost
Port: 1883

---

## 5. Run the MQTT Subscriber

From the project root:

python -m communication.run_subscriber

The subscriber connects and listens for motor telemetry.

---

## 6. Run the Virtual Factory

In a separate terminal:

python -m simulator.main

The simulator generates readings for its registered motors.

If MQTT is connected, the readings are published.

If MQTT is unavailable, the simulator can run in local display mode.

---

## 7. Subscribe using Mosquitto

To monitor telemetry independently:

mosquitto_sub -h localhost -p 1883 -t "motorguard/factories/+/motors/+/telemetry" -v

To subscribe to one motor:

mosquitto_sub -h localhost -p 1883 -t "motorguard/factories/FACTORY_01/motors/MOTOR_001/telemetry" -v

---

## 8. Validation

Incoming telemetry is checked for:

- Valid topic structure
- UTF-8 encoding
- Valid JSON
- Supported telemetry schema version
- Required fields
- Valid motor state
- Valid vibration feature values
- Valid synthetic sensor values
- Valid simulation metadata
- Topic/payload factory ID consistency
- Topic/payload motor ID consistency

Invalid messages are logged and rejected.

The subscriber continues listening after invalid messages.

---

## 9. QoS

Default QoS: 1

QoS 1 means at-least-once delivery.

Messages may be duplicated.

The current application does not implement persistent deduplication.

Retained messages are disabled for telemetry.

---

## 10. Reliability Limitations

The application does not currently persist telemetry locally.

When the simulator generates a reading while the publisher is disconnected,
the reading may be lost.

Automatic MQTT reconnect does not replay readings that were never successfully
published.

There is no exactly-once delivery guarantee.

---

## 11. Shutdown

Use CTRL+C to stop the simulator or subscriber.

The applications attempt to disconnect MQTT clients and stop their network loops.

---

## 12. Troubleshooting

### Broker connection refused

Check:

- Broker is running
- Host is correct
- Port is correct
- Firewall permits the connection
- MQTT credentials are correct

### No telemetry received

Check:

- Subscriber is running
- Simulator is running
- Topic matches the convention
- Publisher is connected
- Broker is accessible

### Telemetry rejected

Check:

- JSON format
- Schema version
- Required fields
- Motor ID in topic and payload
- Factory ID in topic and payload
- Sensor values
- Vibration feature values

### QoS errors

Check that the broker supports the requested QoS.

---

## 13. Commands

Start subscriber:

python -m communication.run_subscriber

Start simulator:

python -m simulator.main

Run tests:

python -m pytest tests -v

Run tests with summary:

python -m pytest tests -v --tb=short
