
# MotorGuard — Phase 3 Context
# MQTT Communication Layer

---

## 1. Project Overview

MotorGuard is a predictive-maintenance platform designed to monitor
industrial electric motors, analyze vibration-related behavior, identify
bearing conditions, and provide a foundation for predictive maintenance.

The project uses a virtual factory environment to simulate motors,
generate telemetry, transport telemetry through MQTT, and eventually
integrate data storage, backend services, machine-learning inference,
and a monitoring dashboard.

Phase 3 focuses exclusively on implementing and validating the MQTT
communication layer between the existing virtual factory simulator
and an MQTT broker.

The MQTT layer must transport telemetry without introducing unnecessary
dependencies into the simulation engine.

---

## 2. Project Objectives

The broader MotorGuard project aims to:

- Simulate industrial motors.
- Generate realistic motor telemetry.
- Represent different motor states and operating conditions.
- Simulate vibration and additional sensor measurements.
- Identify and classify bearing-related conditions.
- Transport telemetry through a communication layer.
- Prepare telemetry for backend processing.
- Support future predictive-maintenance analysis.
- Provide a foundation for monitoring and visualization.

Phase 3 addresses only the telemetry transport and reception
requirements.

---

## 3. Phase 3 Objective

The objective of Phase 3 is to establish reliable communication
between the MotorGuard virtual factory and an MQTT broker.

The phase introduces a transport layer responsible for:

1. MQTT configuration.
2. MQTT connection management.
3. Topic construction.
4. Telemetry publication.
5. Integration with the FactoryEngine callback.
6. Independent telemetry subscription.
7. Incoming message validation.
8. Error handling.
9. Publication and reception statistics.
10. Graceful disconnection.
11. Automated testing.

The MQTT implementation must not alter the existing simulation
logic or telemetry structure.

---

## 4. Phase 3 Scope

### Included

- MQTT configuration
- Environment-based configuration
- MQTT publisher
- MQTT topic utilities
- Factory-to-MQTT adapter
- Independent MQTT subscriber
- MQTT message reception
- Topic validation
- JSON validation
- Telemetry validation
- JSON Schema validation
- Topic/payload consistency verification
- Logging and error handling
- Connection and disconnection management
- Automated tests
- MQTT documentation

### Excluded

The following components are not part of Phase 3:

- FastAPI backend
- REST API
- WebSocket API
- PostgreSQL integration
- InfluxDB integration
- Database models
- Database migrations
- React dashboard
- Node-RED automation
- Frontend visualization
- New machine-learning training
- New classification pipeline
- Modifying the original dataset
- Changing the telemetry contract
- Replacing the MQTT broker
- Implementing a new sensor-generation pipeline

These components belong to future phases.

---

## 5. Overall System Architecture

The current architecture is divided into independent components.

```text
+------------------------------------------+
|          MotorGuard Simulator           |
|                                          |
|  DatasetProvider                         |
|       |                                  |
|       v                                  |
|  SensorSimulator                         |
|       |                                  |
|       v                                  |
|  Virtual Motors                          |
|       |                                  |
|       v                                  |
|  FactoryEngine                           |
|       |                                  |
|       v                                  |
|  Telemetry Reading                       |
+-------------------+----------------------+
                    |
                    v
+------------------------------------------+
|         MQTT Factory Adapter             |
|                                          |
|  Receives factory callback               |
|  Forwards telemetry to publisher          |
+-------------------+----------------------+
                    |
                    v
+------------------------------------------+
|           MQTT Publisher                 |
|                                          |
|  Validation                               |
|  Serialization                            |
|  Topic generation                        |
|  MQTT publication                        |
+-------------------+----------------------+
                    |
                    v
+------------------------------------------+
|             MQTT Broker                 |
|                                          |
|  Message distribution                     |
|  Topic routing                           |
|  QoS handling                            |
+-------------------+----------------------+
                    |
                    v
+------------------------------------------+
|       Independent MQTT Subscriber         |
|                                          |
|  Subscription                             |
|  Message reception                       |
|  Topic validation                        |
|  JSON validation                         |
|  Telemetry validation                    |
|  Schema validation                      |
|  Statistics                              |
+------------------------------------------+
```

---

## 6. Existing Phase 2 Components Reused

Phase 3 relies on the existing Phase 2 simulator.

The MQTT layer does not replace or redesign these components.

### 6.1 DatasetProvider

Responsible for providing vibration data from the prepared dataset.

The simulator uses the dataset to obtain the vibration samples
required for motor simulation.

The MQTT layer does not interact directly with the dataset.

### 6.2 SensorSimulator

Responsible for the existing sensor simulation process.

It remains part of the simulator and is not replaced by MQTT.

### 6.3 Virtual Motors

Represent simulated industrial motors.

Each motor contains its own identification and operating context.

The motors are registered with the FactoryEngine.

### 6.4 FactoryEngine

Responsible for managing the simulated factory.

Its responsibilities include:

- Motor registration
- Motor management
- Motor state changes
- Scenario changes
- Reading generation
- Factory execution
- Callback invocation

The FactoryEngine generates telemetry and passes readings to the
configured callback.

Phase 3 uses this callback to integrate MQTT publication.

The FactoryEngine itself does not need to know MQTT implementation
details.

### 6.5 Existing Telemetry System

The existing telemetry module is reused.

It provides:

- Telemetry structure
- Feature definitions
- Telemetry validation
- Serialization
- Deserialization
- JSON Schema validation

The MQTT layer uses this module instead of creating a second
telemetry format.

---

## 7. MQTT Communication Model

The MQTT architecture follows a publisher/broker/subscriber model.

### Publisher

The MotorGuard simulator publishes telemetry.

### Broker

The MQTT broker receives messages from publishers and distributes
them to subscribers based on topic subscriptions.

### Subscriber

The independent subscriber receives telemetry without being coupled
to the simulator process.

This separation permits the simulator and subscriber to run in
different processes.

It also establishes the foundation for later backend services
consuming telemetry independently.

---

## 8. MQTT Configuration

File:

```text
communication/mqtt_config.py
```

The configuration module centralizes MQTT settings.

### Configuration parameters

| Parameter | Environment Variable | Default |
|---|---|---|
| Broker host | MQTT_HOST | localhost |
| Broker port | MQTT_PORT | 1883 |
| Client ID | MQTT_CLIENT_ID | motorguard_publisher |
| Username | MQTT_USERNAME | Optional |
| Password | MQTT_PASSWORD | Optional |
| Keepalive | MQTT_KEEPALIVE | 60 |
| Connection timeout | MQTT_CONNECT_TIMEOUT | 10 |
| QoS | MQTT_QOS | 1 |
| Minimum reconnect delay | MQTT_RECONNECT_MIN_DELAY | 1 |
| Maximum reconnect delay | MQTT_RECONNECT_MAX_DELAY | 30 |

The configuration is loaded from environment variables.

Credentials must not be hardcoded into source files.

The `.env` file is local configuration and must not be committed
to the repository.

The `.env.example` file documents the expected variables without
containing private credentials.

### Configuration responsibilities

- Define broker connection parameters.
- Validate port values.
- Validate QoS values.
- Validate timeout values.
- Validate reconnect configuration.
- Provide default configuration.
- Read environment variables.
- Allow separate MQTT client IDs.

---

## 9. MQTT Topic Convention

File:

```text
communication/mqtt_topics.py
```

Motor telemetry follows this topic structure:

```text
motorguard/factories/{factory_id}/motors/{motor_id}/telemetry
```

### Example

```text
motorguard/factories/FACTORY_01/motors/MOTOR_001/telemetry
```

Another motor:

```text
motorguard/factories/FACTORY_01/motors/MOTOR_002/telemetry
```

### Topic hierarchy

```text
motorguard
└── factories
    └── FACTORY_01
        └── motors
            └── MOTOR_001
                └── telemetry
```

### Topic utilities

The topic module provides functions for:

- Validating topic components
- Constructing individual motor topics
- Constructing factory-level wildcard topics
- Constructing global wildcard subscriptions

### Topic component restrictions

Factory and motor identifiers must:

- Be non-empty.
- Use permitted characters.
- Not contain topic separators.
- Not contain MQTT wildcard characters.
- Not contain spaces.

This prevents invalid topic structures and accidental wildcard injection.

---

## 10. MQTT Topic Examples

### Individual motor

```text
motorguard/factories/FACTORY_01/motors/MOTOR_001/telemetry
```

### Second motor

```text
motorguard/factories/FACTORY_01/motors/MOTOR_002/telemetry
```

### All motors of a factory

```text
motorguard/factories/FACTORY_01/motors/+/telemetry
```

### All motors of all factories

```text
motorguard/factories/+/motors/+/telemetry
```

The independent subscriber uses the global wildcard subscription.

---

## 11. MQTT Publisher

File:

```text
communication/mqtt_publisher.py
```

The publisher is responsible for transmitting telemetry
from the simulator to the MQTT broker.

### Responsibilities

1. Create an MQTT client.
2. Configure MQTT credentials if present.
3. Configure reconnect delays.
4. Establish a broker connection.
5. Track connection state.
6. Validate telemetry before publication.
7. Serialize telemetry into JSON.
8. Construct the correct MQTT topic.
9. Publish the message.
10. Verify publication status.
11. Log publication failures.
12. Disconnect cleanly.

### Publication process

```text
Telemetry Reading
      |
      v
Telemetry Validation
      |
      v
Telemetry Serialization
      |
      v
Topic Generation
      |
      v
MQTT Publish
      |
      v
Publication Result
```

### Publisher behavior

When connected:

- Telemetry is validated.
- Telemetry is serialized.
- The motor-specific topic is constructed.
- The MQTT message is published.
- The publication result is checked.

When disconnected:

- Publication cannot proceed.
- The publisher reports failure.
- The application must not falsely report a successful delivery.

The current implementation does not provide an offline persistence
queue.

---

## 12. MQTT Delivery Configuration

### QoS

The default QoS is:

```text
QoS 1
```

QoS 1 provides at-least-once delivery at the MQTT protocol
level.

This means the recipient may receive duplicate messages.

QoS 1 does not guarantee exactly-once processing.

### Retained messages

Telemetry publications use:

```text
retain = False
```

The broker therefore does not retain the latest motor telemetry
as a retained message for future subscribers.

### Delivery limitations

MQTT QoS does not automatically provide application-level
persistence.

The current system does not implement:

- Persistent telemetry queues
- Offline telemetry buffering
- Application-level replay
- Duplicate-message deduplication
- Exactly-once telemetry processing

---

## 13. MQTT Factory Adapter

File:

```text
communication/mqtt_factory_adapter.py
```

The adapter connects the existing FactoryEngine callback to the
MQTT publisher.

It serves as an integration boundary.

The FactoryEngine generates readings.

The adapter receives the readings and delegates publication.

### Responsibilities

- Accept a telemetry reading.
- Forward the reading to the publisher.
- Track successful publication count.
- Track failed publication count.
- Provide publication statistics.

### Adapter statistics

The adapter tracks:

```text
published
failed
total
```

Where:

- `published` = successful publishing operations
- `failed` = failed publishing operations
- `total` = total readings passed to the adapter

### Design principle

The FactoryEngine remains independent of MQTT.

MQTT transport is introduced through the callback mechanism
rather than by adding MQTT logic inside the factory engine.

---

## 14. Simulator Integration

File:

```text
simulator/main.py
```

The simulator remains responsible for starting and running the factory.

### Existing simulator flow

```text
Initialize DatasetProvider
        |
        v
Initialize SensorSimulator
        |
        v
Initialize FactoryEngine
        |
        v
Create Virtual Motors
        |
        v
Register Motors
        |
        v
Start Motors
        |
        v
Run FactoryEngine
        |
        v
Generate Telemetry
```

### Phase 3 integration

The factory reading callback is used to transport telemetry.

```text
FactoryEngine
      |
      v
Reading Callback
      |
      v
MQTTFactoryAdapter
      |
      v
MQTTPublisher
      |
      v
MQTT Broker
```

### MQTT unavailable

MQTT is optional for the simulator.

If the MQTT connection cannot be established, the simulator
should remain capable of operating in local mode.

The MQTT communication failure should not prevent the underlying
simulation engine from generating readings.

### Shutdown

The application should stop the factory and disconnect the MQTT
publisher when execution ends.

The shutdown sequence should be handled in a `finally` block
to reduce the risk of leaving running threads or connections.

---

## 15. Independent MQTT Subscriber

File:

```text
communication/mqtt_subscriber.py
```

The subscriber is an independent application that connects to
the broker and receives telemetry.

It does not depend on the FactoryEngine or simulator process.

### Responsibilities

- Initialize an MQTT client.
- Connect to the broker.
- Subscribe to telemetry topics.
- Receive MQTT messages.
- Validate incoming topics.
- Decode message payloads.
- Parse JSON.
- Validate telemetry structure.
- Validate JSON Schema.
- Verify topic and payload consistency.
- Display valid telemetry.
- Track valid and invalid messages.
- Log validation errors.
- Continue processing after malformed messages.
- Disconnect cleanly.

### Subscriber wildcard

The subscriber listens to:

```text
motorguard/factories/+/motors/+/telemetry
```

This allows the subscriber to receive telemetry from multiple
factories and multiple motors without needing to know their IDs
in advance.

---

## 16. Subscriber Message Validation Pipeline

Every received message passes through a validation pipeline.

```text
MQTT Message
     |
     v
Count Received Message
     |
     v
Validate MQTT Topic
     |
     v
Decode UTF-8
     |
     v
Parse JSON
     |
     v
Validate Telemetry Contract
     |
     v
Validate JSON Schema
     |
     v
Compare Topic IDs
with Payload IDs
     |
     v
Valid Telemetry
     |
     v
Display / Statistics
```

Any invalid message is rejected.

The subscriber should continue listening after rejection.

---

## 17. Subscriber Validation Rules

### 17.1 Topic validation

The subscriber verifies that the received topic follows the
expected structure.

Expected structure:

```text
motorguard/factories/{factory_id}/motors/{motor_id}/telemetry
```

The topic must have the expected number of components.

The factory and motor IDs must be valid.

### 17.2 UTF-8 validation

The payload must be decodable as UTF-8.

Invalid byte sequences must be rejected.

### 17.3 JSON validation

The payload must contain valid JSON.

Malformed JSON is rejected and counted separately.

### 17.4 Telemetry validation

The decoded telemetry must satisfy the existing telemetry
contract.

This includes required fields, data types, motor states,
vibration feature values, sensor values, and simulation metadata.

### 17.5 Schema validation

The telemetry must be compatible with the existing JSON Schema.

The existing schema is reused.

No new MQTT telemetry schema is introduced.

### 17.6 Topic/payload consistency

The subscriber compares the factory and motor identifiers
extracted from the topic with those contained in the telemetry
payload.

For example:

Topic:

```text
motorguard/factories/FACTORY_01/motors/MOTOR_001/telemetry
```

Payload:

```json
{
    "factory_id": "FACTORY_01",
    "motor_id": "MOTOR_001"
}
```

The identifiers must match.

If a message is published on a topic for `MOTOR_001` but contains
telemetry identifying `MOTOR_999`, the message is rejected.

---

## 18. Telemetry Contract

Phase 3 uses the existing telemetry contract.

Schema version:

```text
1.0
```

### Required fields

| Field | Purpose |
|---|---|
| `schema_version` | Telemetry schema version |
| `timestamp` | Reading generation timestamp |
| `motor_id` | Motor identifier |
| `motor_name` | Motor name |
| `factory_id` | Factory identifier |
| `line_id` | Production line identifier |
| `motor_state` | Current motor operating state |
| `bearing_condition` | Simulated bearing condition |
| `vibration` | Vibration feature vector |
| `ground_truth` | Ground-truth condition |
| `sensors` | Additional sensor measurements |
| `simulation` | Simulation source and metadata |

### Vibration features

The telemetry contains the existing vibration feature vector.

```text
max
min
mean
sd
rms
skewness
kurtosis
crest
form
```

The MQTT layer does not calculate these features.

It transports them as generated by the simulator.

### Sensor fields

The current telemetry contract includes:

```text
temperature
current
rpm
```

These fields remain governed by the existing telemetry
validation and schema.

### Simulation metadata

The simulation metadata identifies whether the reading is
simulated and records relevant data-source information.

The MQTT layer does not change the simulation metadata.

---

## 19. Telemetry JSON Example

The following is an illustrative structure, not a claim of a
specific reading captured from the broker.

```json
{
    "schema_version": "1.0",
    "timestamp": "2026-11-22T10:00:00+00:00",
    "motor_id": "MOTOR_001",
    "motor_name": "Conveyor Motor",
    "factory_id": "FACTORY_01",
    "line_id": "LINE_01",
    "motor_state": "RUNNING",
    "bearing_condition": "Normal_1",
    "vibration": {
        "max": 1.0,
        "min": 0.1,
        "mean": 0.5,
        "sd": 0.2,
        "rms": 0.6,
        "skewness": 0.1,
        "kurtosis": 2.0,
        "crest": 1.5,
        "form": 1.2
    },
    "ground_truth": "Normal_1",
    "sensors": {
        "temperature": 30.0,
        "current": 1.0,
        "rpm": 1500.0
    },
    "simulation": {
        "is_simulated": true,
        "vibration_source": "CWRU_PREPARED_CSV",
        "additional_sensor_source": "SYNTHETIC"
    }
}
```

The actual numerical values depend on the simulation.

---

## 20. Subscriber Statistics

The subscriber tracks message reception and validation outcomes.

### Counters

- `received_count`
- `valid_count`
- `invalid_count`
- `topic_error_count`
- `json_error_count`
- `telemetry_error_count`

### Meaning

| Counter | Description |
|---|---|
| received | Messages received by subscriber |
| valid | Messages accepted by validation |
| invalid | Messages rejected |
| topic_errors | Messages with invalid topic |
| json_errors | Messages with decoding or JSON issues |
| telemetry_errors | Messages failing telemetry validation |

Statistics are intended to help identify communication
and data-quality problems.

---

## 21. Subscriber Runner

File:

```text
communication/run_subscriber.py
```

The runner starts the independent subscriber process.

The subscriber must not be started automatically inside
the virtual factory.

This permits independent testing and operation.

### Start command

```powershell
python -m communication.run_subscriber
```

### Stop command

```text
CTRL+C
```

The runner should stop the subscriber and report its final
statistics during shutdown.

---

## 22. MQTT Broker

The broker is an independent service.

The publisher and subscriber connect to it using the configured
host and port.

The MQTT implementation does not install, replace, or manage
the broker itself.

The current default connection configuration is:

```text
Host: localhost
Port: 1883
```

The broker must be running before real communication
can be verified.

Broker-specific configuration, authentication, persistence,
and security are managed separately from the Python MQTT layer.

---

## 23. Execution Workflow

### Terminal 1 — MQTT Subscriber

```powershell
python -m communication.run_subscriber
```

Expected behavior:

- MQTT client starts.
- Broker connection is established.
- Subscriber subscribes to the telemetry wildcard topic.
- Subscriber waits for telemetry.

### Terminal 2 — Virtual Factory

```powershell
python -m simulator.main
```

Expected behavior:

- Simulator initializes.
- Motors are registered.
- Motors are started.
- Factory generates telemetry.
- MQTT adapter forwards telemetry.
- Publisher publishes readings.
- Factory execution ends.
- Publisher disconnects.

### Expected subscriber behavior

The subscriber should receive readings from registered motors
and display validated telemetry.

Reception is independent of the simulator's internal process.

---

## 24. Manual Verification

Manual verification has been reported as successful.

### Publisher verification

- [x] Simulator generated telemetry.
- [x] MQTT publishing was integrated.
- [x] MQTT messages reached the broker.

### Subscriber verification

- [x] Independent subscriber was implemented.
- [x] Subscriber received MQTT messages.
- [x] Received messages passed telemetry validation.

These are user-reported manual results.

They are not substitutes for an automated test report.

---

## 25. Automated Testing

The automated tests are intended to validate the MQTT layer
independently of the real broker.

Test framework:

```text
pytest
```

### Test files

```text
tests/
├── __init__.py
├── test_mqtt_config.py
├── test_mqtt_topics.py
├── test_mqtt_publisher.py
├── test_mqtt_adapter.py
├── test_mqtt_subscriber.py
└── test_mqtt_live.py
```

### Configuration tests

Verify:

- Default configuration
- Valid configuration
- Invalid port
- Invalid QoS
- Invalid host
- Invalid timeout
- Invalid keepalive
- Invalid reconnect configuration
- Environment-variable parsing

### Topic tests

Verify:

- Motor telemetry topic
- Factory wildcard topic
- Global wildcard topic
- Valid topic components
- Invalid topic components

### Publisher tests

Verify:

- Publisher initialization
- Disconnected state
- Valid publication
- Serialization
- QoS configuration
- Retain configuration
- Publication failure
- Invalid telemetry rejection

### Adapter tests

Verify:

- Forwarding
- Successful publication statistics
- Failed publication statistics
- Multiple readings

### Subscriber tests

Verify:

- Valid topic
- Invalid topic
- Valid message
- Malformed JSON
- Invalid UTF-8
- Invalid motor state
- Missing telemetry fields
- Factory ID mismatch
- Motor ID mismatch
- Statistics
- Graceful shutdown

### Live broker integration test

The live broker test is optional.

It is enabled explicitly using:

```powershell
$env:MQTT_TEST_LIVE="1"
```

It requires an active MQTT broker.

The live test verifies the real publish/receive path.

It must not be enabled automatically during ordinary unit tests.

---

## 26. Testing Commands

Run the automated suite:

```powershell
python -m pytest tests -v
```

Run the suite with concise traceback output:

```powershell
python -m pytest tests -v --tb=short
```

Run the MQTT configuration tests:

```powershell
python -m pytest tests/test_mqtt_config.py -v
```

Run the topic tests:

```powershell
python -m pytest tests/test_mqtt_topics.py -v
```

Run the publisher tests:

```powershell
python -m pytest tests/test_mqtt_publisher.py -v
```

Run the adapter tests:

```powershell
python -m pytest tests/test_mqtt_adapter.py -v
```

Run the subscriber tests:

```powershell
python -m pytest tests/test_mqtt_subscriber.py -v
```

Run the live broker test:

```powershell
$env:MQTT_TEST_LIVE="1"
python -m pytest tests/test_mqtt_live.py -v
```

Disable the live test environment variable afterward:

```powershell
Remove-Item Env:MQTT_TEST_LIVE
```

---

## 27. Test Reporting

The final test report should record:

- Python version
- Operating system
- MQTT broker
- Broker version
- Test execution date
- Total tests
- Passed tests
- Failed tests
- Skipped tests
- Configuration test results
- Topic test results
- Publisher test results
- Adapter test results
- Subscriber test results
- Live broker test result
- Known issues
- Reliability limitations

Test results must reflect actual execution.

No tests should be marked as passed simply because the code was
written or because manual testing succeeded.

---

## 28. Reliability Considerations

### Broker unavailable

The simulator should continue to function locally when MQTT
is unavailable.

MQTT transport failure must not unnecessarily prevent telemetry
generation.

### Publisher disconnection

The publisher must not report successful publication when it
cannot publish.

### Subscriber disconnection

The subscriber should maintain appropriate connection state
and attempt reconnection according to its implementation
and the MQTT client behavior.

### Invalid messages

Invalid messages must be rejected.

The subscriber must continue processing subsequent messages
rather than terminating due to one invalid payload.

### Graceful shutdown

The simulator and subscriber should stop their MQTT loops and
disconnect when terminated.

### Duplicate delivery

QoS 1 permits duplicate delivery.

The current system does not implement application-level
deduplication.

### Offline readings

The application does not persist telemetry generated during
broker outages.

Readings that are not successfully published may be lost.

---

## 29. Current Limitations

The current Phase 3 implementation does not include:

- Persistent telemetry storage
- MQTT offline queue
- Automatic replay of lost readings
- Application-level duplicate detection
- Exactly-once application processing
- Database storage
- API endpoints
- Frontend dashboards
- Backend ingestion service
- Authentication authorization logic at the application level
- TLS configuration verification
- Production broker deployment
- High-availability broker architecture
- Centralized monitoring
- Alerting

These are future improvements or separate architectural tasks.

---

## 30. Security Considerations

MQTT communication should be configured securely before
production deployment.

Current development configuration may use a local broker.

Production deployment should consider:

- Broker authentication
- Strong credentials
- TLS encryption
- Certificate validation
- Restricted topic permissions
- Publisher permissions
- Subscriber permissions
- Environment-based secret management
- Network restrictions
- Avoiding credentials in Git
- Logging without exposing secrets

Security implementation must be aligned with the actual broker
configuration and deployment environment.

---

## 31. Phase 3 Completion Criteria

### MQTT infrastructure

- [x] MQTT configuration module
- [x] Environment configuration
- [x] MQTT topic module
- [x] MQTT publisher

### Simulator integration

- [x] Factory callback integration
- [x] MQTT adapter
- [x] Existing simulator preserved
- [x] Existing telemetry preserved

### Subscriber

- [x] Independent MQTT subscriber
- [x] Wildcard subscription
- [x] Message reception
- [x] Topic validation
- [x] JSON validation
- [x] Telemetry validation
- [x] Topic/payload consistency
- [x] Statistics

### Manual testing

- [x] Publisher manually verified
- [x] Broker reception verified
- [x] Independent subscriber reception verified
- [x] Telemetry validation verified

### Automated testing

- [ ] Automated test suite implemented and reviewed
- [ ] Automated test suite executed
- [ ] Test report recorded
- [ ] Live broker test completed, if required

### Documentation

- [x] MQTT architecture documented
- [x] Topic convention documented
- [x] Telemetry contract documented
- [x] Execution instructions documented
- [x] Limitations documented

Phase 3 must not be declared completely verified until
automated tests have actually been executed and reviewed.

---

## 32. Phase 3 Conclusion

Phase 3 establishes the MQTT communication layer for MotorGuard.

The virtual factory remains responsible for generating motor
telemetry.

The MQTT publisher transports the generated telemetry.

The broker distributes messages.

The independent subscriber receives and validates messages.

The architecture keeps simulation, transport, and reception
separated.

This separation is important for future integration because
the simulator will not need to know how backend storage,
API services, machine-learning inference, or visualization
are implemented.

The MQTT layer becomes a reusable communication boundary
between the virtual factory and the next architectural components.

---

## 33. Next Phase — Phase 4

The next phase is the backend ingestion layer.

The intended architecture is:

```text
Virtual Factory
      |
      v
MQTT Publisher
      |
      v
MQTT Broker
      |
      v
Backend MQTT Consumer
      |
      +---------------------+
      |                     |
      v                     v
PostgreSQL              InfluxDB
Structured Data          Time-Series Data
      |                     |
      +----------+----------+
                 |
                 v
           Backend API
                 |
                 v
          Future Dashboard
```

Phase 4 should introduce backend services that consume MQTT
telemetry independently from the simulator.

The backend must not require changes to the virtual factory
or the MQTT topic contract unless a justified architectural
change is identified.

### Expected Phase 4 objectives

- Backend service structure
- MQTT ingestion service
- Telemetry processing
- Persistence strategy
- PostgreSQL integration
- InfluxDB integration
- Data integrity
- Error handling
- Backend configuration
- Logging
- API preparation

The exact Phase 4 implementation should be planned before
coding begins.

---

## 34. Context Preservation

When continuing MotorGuard development in a new conversation,
use this file as the primary Phase 3 reference.

Before making modifications:

1. Inspect the existing repository.
2. Confirm the Phase 3 files are present.
3. Read this context document.
4. Read the telemetry contract and schema.
5. Verify the MQTT configuration.
6. Verify the publisher and subscriber.
7. Check the current automated test status.
8. Preserve working Phase 2 and Phase 3 functionality.
9. Do not reimplement completed components unnecessarily.
10. Continue from the actual project state rather than assuming
    all documented code is already present.

The project must evolve incrementally.

Changes to the MQTT layer must remain compatible with the existing
simulator and telemetry contract unless a deliberate versioned
change is approved.
