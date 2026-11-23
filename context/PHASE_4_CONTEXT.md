# MotorGuard — Phase 4 Context
## Backend MQTT Ingestion, PostgreSQL, InfluxDB and Reliability

---

# 1. Project Overview

MotorGuard is an industrial predictive-maintenance system focused on
monitoring virtual electric motors and detecting bearing faults.

The system uses:

- A motor simulation environment.
- CWRU bearing vibration feature data.
- Virtual motors and factories.
- Synthetic additional sensors.
- MQTT communication.
- A backend ingestion and persistence system.
- PostgreSQL for relational data.
- InfluxDB for time-series telemetry.
- A future FastAPI backend.
- A future React dashboard.
- A future predictive-maintenance inference layer.

The system is being developed incrementally through separate phases.

Each phase should preserve the functionality of previous phases.

---

# 2. Project Architecture

The project is organized conceptually into the following layers.

## Phase 1 — Dataset and Feature Preparation

The project uses a prepared CWRU feature dataset.

The dataset contains extracted vibration features used by the
virtual motors.

The project uses nine vibration features:

- max
- min
- mean
- sd
- rms
- skewness
- kurtosis
- crest
- form

The feature contract must remain consistent with the simulation
and future machine-learning models.

---

## Phase 2 — Motor Simulation

Phase 2 introduced the simulation layer.

Its responsibilities include:

- Dataset loading.
- Sampling from the different bearing conditions.
- Feature-vector generation.
- Motor initialization.
- Multiple independent virtual motors.
- Motor states.
- Scenario transitions.
- Synthetic additional sensor generation.
- Telemetry serialization.
- JSON Schema validation.

The simulator should remain independent from the backend.

Phase 2 should not be rewritten in Phase 5.

---

## Phase 3 — MQTT Communication

Phase 3 introduced the communication layer.

Its responsibilities include:

- MQTT configuration.
- MQTT publishing.
- Topic generation.
- MQTT subscriber.
- Factory-to-MQTT integration.
- Connection handling.
- Reconnection.
- Logging.
- Telemetry publication.
- Subscriber validation.
- Graceful shutdown.

The publisher uses the existing MQTT broker.

Phase 4 and Phase 5 must reuse the same broker.

Do not add another broker.

---

## Phase 4 — Backend Ingestion and Persistence

Phase 4 introduced an independent backend process.

The backend is independent of the simulator.

It does not import virtual motor objects or rely on factory engine
objects to receive telemetry.

It receives messages exclusively through MQTT.

Phase 4 responsibilities:

- MQTT wildcard subscription.
- Telemetry decoding.
- Telemetry validation.
- Topic/payload consistency checks.
- Durable PostgreSQL inbox.
- Metadata persistence.
- Duplicate detection.
- InfluxDB time-series writes.
- Background persistence worker.
- Retry tracking.
- Error logging.
- Graceful shutdown.
- Reliability testing.

---

# 3. Existing MQTT Contract

The existing MQTT broker must be reused.

The global telemetry subscription is:

motorguard/factories/+/motors/+/telemetry

The individual motor telemetry topic is:

motorguard/factories/{factory_id}/motors/{motor_id}/telemetry

Example:

motorguard/factories/FACTORY_01/motors/MOTOR_01/telemetry

Topic IDs must correspond to the telemetry payload.

The topic format must not be changed without updating the publisher,
subscriber, validation, and all dependent phases.

---

# 4. MQTT Configuration

The existing MQTT configuration is located in:

communication/mqtt_config.py

The configuration includes:

- MQTT_HOST
- MQTT_PORT
- MQTT_CLIENT_ID
- MQTT_USERNAME
- MQTT_PASSWORD
- MQTT_KEEPALIVE
- MQTT_CONNECT_TIMEOUT
- MQTT_QOS
- MQTT_RECONNECT_MIN_DELAY
- MQTT_RECONNECT_MAX_DELAY

The backend uses a distinct MQTT client ID:

motorguard_backend_consumer

The simulator publisher and backend consumer must not use the same
client ID simultaneously.

The project uses MQTT QoS 1.

QoS 1 provides at-least-once delivery and can produce duplicates.

Duplicate telemetry is therefore expected and must be handled safely.

---

# 5. Telemetry Schema Contract

Telemetry schema version:

1.0

Required top-level fields:

- schema_version
- timestamp
- motor_id
- motor_name
- factory_id
- line_id
- motor_state
- bearing_condition
- vibration
- ground_truth
- sensors
- simulation

## Vibration

The vibration object contains:

- max
- min
- mean
- sd
- rms
- skewness
- kurtosis
- crest
- form

All nine features are numeric.

## Sensors

The sensors object contains:

- temperature
- current
- rpm

All three values are numeric and non-negative according to
the current telemetry schema.

## Simulation provenance

The simulation object contains:

- is_simulated
- vibration_source
- additional_sensor_source

is_simulated must be boolean.

Provenance must be preserved when telemetry is stored.

The backend must not silently replace missing or invalid values with zero.

---

# 6. Phase 4 Validation

Incoming telemetry is independently validated.

Validation includes:

- JSON decoding.
- Supported schema version.
- Required field presence.
- Field type validation.
- Timestamp format.
- Timezone-aware timestamp.
- Numeric validation.
- Finite numeric values.
- Rejection of NaN.
- Rejection of infinity.
- Nine vibration feature validation.
- Sensor validation.
- Simulation provenance validation.
- MQTT topic validation.
- Factory ID consistency.
- Motor ID consistency.

Invalid telemetry is rejected safely.

Validation errors are logged with the reason.

---

# 7. PostgreSQL Responsibilities

PostgreSQL is the relational database.

It stores:

- Factories.
- Production lines.
- Motors.
- Maintenance records.
- Telemetry inbox.

PostgreSQL is NOT intended to store every vibration sample
as the primary time-series database.

The telemetry inbox is a durable intermediate storage layer
protecting MQTT ingestion from immediate downstream failures.

---

# 8. PostgreSQL Tables

## factories

Stores factory metadata.

Primary key:

- id

Fields include:

- id
- name
- created_at

---

## production_lines

Stores production line metadata.

Composite primary key:

- factory_id
- id

A line ID is scoped to its factory.

Two factories may both contain LINE_01.

---

## motors

Stores motor metadata.

Composite primary key:

- factory_id
- id

Motor records reference production lines through:

- factory_id
- line_id

Motor identity is factory-scoped.

---

## maintenance_records

Stores maintenance history.

Fields include:

- id
- factory_id
- motor_id
- maintenance_type
- description
- performed_at
- created_at

Motor references use factory-scoped identity.

---

## telemetry_inbox

Stores telemetry awaiting or undergoing persistence.

Fields include:

- id
- event_key
- topic
- factory_id
- motor_id
- line_id
- payload
- received_at
- status
- attempts
- last_error
- persisted_at
- next_attempt_at
- processing_started_at
- processed_at

Possible statuses:

- pending
- processing
- processed
- failed

The event_key has a unique constraint.

---

# 9. Duplicate Detection

MQTT QoS 1 allows duplicate deliveries.

The backend generates a deterministic SHA-256 event key using
canonical JSON representation of telemetry.

Identical telemetry produces the same event key.

PostgreSQL enforces uniqueness on event_key.

Duplicate telemetry is not inserted a second time.

Duplicate messages are safe to acknowledge when the existing
inbox event has already been successfully registered.

The system must not claim distributed exactly-once delivery.

---

# 10. InfluxDB Responsibilities

InfluxDB is the time-series database.

The measurement name is:

motor_telemetry

Tags include:

- factory_id
- line_id
- motor_id
- motor_state
- bearing_condition
- ground_truth
- is_simulated
- vibration_source, when available
- additional_sensor_source, when available

Numeric fields include:

## Vibration

- max
- min
- mean
- sd
- rms
- skewness
- kurtosis
- crest
- form

## Sensors

- temperature
- current
- rpm

The point timestamp comes from the original telemetry timestamp.

The backend reception time is stored separately in PostgreSQL.

---

# 11. Phase 4 Processing Flow

The processing flow is:

1. MQTT receives telemetry.
2. Backend decodes JSON.
3. Backend validates the payload.
4. Backend validates topic format.
5. Backend checks topic/payload IDs.
6. Backend generates the deterministic event key.
7. PostgreSQL metadata is registered.
8. PostgreSQL inbox record is committed.
9. MQTT message is acknowledged after durable inbox registration.
10. Inbox worker claims pending events.
11. Worker writes telemetry to InfluxDB.
12. Worker marks event as processed.

Invalid telemetry is rejected and acknowledged to prevent
poison-message redelivery.

Unexpected storage errors must not be treated as successful ingestion.

---

# 12. Worker Reliability

The inbox worker is independent of MQTT message reception.

It uses PostgreSQL inbox status to manage persistence.

The intended lifecycle is:

pending
    |
    v
processing
    |
    +---- successful Influx write ---> processed
    |
    +---- temporary failure --------> pending with retry time
    |
    +---- maximum attempts ---------> failed

Worker processing should use PostgreSQL row locking.

Multiple workers must not claim the same record simultaneously.

The claim query uses:

FOR UPDATE SKIP LOCKED

Processing leases allow recovery of records left in processing
when a worker crashes.

Retry delays increase exponentially and are capped.

Retry scheduling uses next_attempt_at.

The worker must not retry records continuously without delay.

---

# 13. Delivery Guarantees and Limitations

The system provides:

- MQTT QoS 1 delivery.
- Durable PostgreSQL inbox registration.
- Duplicate detection.
- At-least-once processing.
- Retryable downstream persistence.
- Recovery of expired processing records.
- Idempotent InfluxDB writes for identical point identity.

PostgreSQL and InfluxDB do not share a transaction.

A crash after InfluxDB successfully writes but before PostgreSQL
marks the inbox event processed can result in a repeated Influx write.

Identical Influx point identity generally overwrites the same point
rather than creating a distinct duplicate point.

This is not global exactly-once delivery.

---

# 14. Phase 4 File Structure

The backend structure is:

backend/
    __init__.py
    main.py
    config.py
    logging_config.py

    mqtt/
        __init__.py
        consumer.py
        topic_parser.py

    validation/
        __init__.py
        telemetry_validator.py

    database/
        __init__.py
        postgres.py
        models.py
        repositories.py
        influx.py

    ingestion/
        __init__.py
        event_key.py
        service.py
        inbox_worker.py

    migrations/
        env.py
        versions/

    tests/
        __init__.py
        test_telemetry_validation.py
        test_topic_validation.py
        test_event_key.py
        test_ingestion.py
        test_worker_retry.py

Infrastructure:

docker-compose.yml

Environment:

.env
.env.example

---

# 15. Infrastructure

Docker Compose provides:

- PostgreSQL
- InfluxDB 2.x

The MQTT broker remains external to this Compose configuration
and is the same broker used by Phase 3.

PostgreSQL and InfluxDB use persistent Docker volumes.

Do not delete volumes unless intentional data destruction is required.

---

# 16. Environment Configuration

The project uses environment variables for:

## MQTT

- MQTT_HOST
- MQTT_PORT
- MQTT_USERNAME
- MQTT_PASSWORD
- MQTT_KEEPALIVE
- MQTT_QOS
- MQTT_BACKEND_CLIENT_ID

## PostgreSQL

- POSTGRES_URL
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD

## InfluxDB

- INFLUX_URL
- INFLUX_TOKEN
- INFLUX_ORG
- INFLUX_BUCKET

## Worker

- WORKER_POLL_INTERVAL
- WORKER_BATCH_SIZE
- WORKER_MAX_ATTEMPTS
- WORKER_RETRY_BASE_SECONDS
- WORKER_RETRY_MAX_SECONDS
- WORKER_PROCESSING_LEASE_SECONDS

Development credentials must not be used in production.

---

# 17. Migration Management

The backend schema should be managed with Alembic.

Do not rely on:

Base.metadata.create_all()

for production schema evolution.

The backend startup process must not silently change the database schema.

Schema changes should be:

1. Created through migrations.
2. Reviewed.
3. Applied using Alembic.
4. Versioned.

Existing databases must be reconciled with migration history
before applying migrations.

---

# 18. Phase 4 Test Scope

Tests should cover:

## Telemetry validation

- Valid telemetry.
- Invalid JSON.
- Missing fields.
- Unsupported schema.
- Invalid timestamps.
- Naive timestamps.
- NaN.
- Infinity.
- Negative sensor values.
- Missing vibration features.
- Invalid motor state.

## Topic validation

- Valid topic.
- Invalid topic.
- Invalid identifier.
- Factory mismatch.
- Motor mismatch.

## Deduplication

- Same payload produces same event key.
- Dictionary ordering does not change event key.
- Different payload produces different key.
- Duplicate inbox event is ignored.

## Ingestion

- Valid message accepted.
- Duplicate detected.
- Invalid telemetry rejected.
- Database failure reported without acknowledgment.

## Worker

- Pending record is claimed.
- Successfully persisted record becomes processed.
- Influx failure triggers retry.
- Retry delay increases.
- Retry delay is capped.
- Maximum attempts produce failed status.
- Expired processing records can be recovered.

## Integration

Verify:

MQTT
    -> Backend consumer
    -> PostgreSQL inbox
    -> InfluxDB

Use the real MQTT broker and running persistence infrastructure
for end-to-end verification.

---

# 19. Phase 4 Completion Status

The initial Phase 4 ingestion tests were reported as passing.

The reliability layer adds:

- Migration management.
- Processing leases.
- Retry scheduling.
- Exponential backoff.
- Worker concurrency protection.
- Recovery of expired processing records.

The final reliability changes must be tested in the actual project
environment before they are considered verified.

Do not claim new reliability tests have passed unless their actual
execution results are available.

---

# 20. Next Phase — Phase 5: FastAPI Backend

Phase 5 introduces the REST API layer.

Phase 5 must build on the existing backend instead of replacing it.

The existing MQTT consumer and persistence worker remain independent
background components.

The API must access data through service and repository layers.

---

# 21. Phase 5 Objectives

Implement a FastAPI backend for MotorGuard.

The API should expose data for the future React frontend.

The initial scope should include:

- API application setup.
- API configuration.
- Dependency injection.
- Health endpoints.
- Factory endpoints.
- Production line endpoints.
- Motor endpoints.
- Motor telemetry endpoints.
- Motor status.
- Maintenance records.
- Time-series query interface.
- Pagination.
- Filtering.
- Request validation.
- Response schemas.
- Error handling.
- API documentation.
- Integration tests.

Do not implement the React frontend during Phase 5.

Do not implement machine-learning inference endpoints yet
unless explicitly included in the phase scope.

---

# 22. Suggested Phase 5 Architecture

Keep the API separate from the MQTT ingestion implementation.

Suggested structure:

backend/
    api/
        __init__.py
        app.py

        dependencies.py

        routers/
            __init__.py
            health.py
            factories.py
            lines.py
            motors.py
            telemetry.py
            maintenance.py

        schemas/
            __init__.py
            factory.py
            line.py
            motor.py
            telemetry.py
            maintenance.py

    services/
        __init__.py
        factory_service.py
        line_service.py
        motor_service.py
        telemetry_service.py
        maintenance_service.py

Existing backend components remain:

backend/
    mqtt/
    validation/
    database/
    ingestion/

The API must reuse existing PostgreSQL and InfluxDB configuration.

Do not create another database engine or another InfluxDB client
unnecessarily.

---

# 23. Phase 5 API Design

Initial proposed endpoints:

## Health

GET /api/health

Returns API status and database health.

GET /api/health/ready

Returns readiness status for PostgreSQL and required backend services.

---

## Factories

GET /api/factories

Returns registered factories.

GET /api/factories/{factory_id}

Returns a factory and associated metadata.

GET /api/factories/{factory_id}/lines

Returns production lines for the selected factory.

---

## Lines

GET /api/factories/{factory_id}/lines/{line_id}

Returns a production line.

GET /api/factories/{factory_id}/lines/{line_id}/motors

Returns motors associated with the line.

---

## Motors

GET /api/motors

Supports filters:

- factory_id
- line_id
- motor_state

GET /api/motors/{motor_id}

Returns motor metadata and current status.

GET /api/factories/{factory_id}/motors/{motor_id}

Factory-scoped motor retrieval.

GET /api/factories/{factory_id}/motors/{motor_id}/telemetry/latest

Returns the latest telemetry point.

GET /api/factories/{factory_id}/motors/{motor_id}/telemetry

Returns historical telemetry.

Possible query parameters:

- start
- end
- limit
- measurement/field filters when appropriate

---

## Maintenance

GET /api/factories/{factory_id}/motors/{motor_id}/maintenance

Returns maintenance records.

POST /api/factories/{factory_id}/motors/{motor_id}/maintenance

Creates a maintenance record.

PUT or PATCH should be introduced only when needed.

---

# 24. API Data Source Rules

PostgreSQL is the source for:

- Factory metadata.
- Production lines.
- Motor metadata.
- Maintenance records.
- Inbox processing status.

InfluxDB is the source for:

- Historical vibration features.
- Temperature.
- Current.
- RPM.
- Time-series telemetry.

The API should not query the PostgreSQL inbox as a substitute
for historical telemetry.

The API must use the appropriate database for each type of data.

---

# 25. Phase 5 Requirements

Implement Phase 5 in small verified steps.

Before writing code:

1. Inspect the current project structure.
2. Inspect actual Phase 4 files.
3. Inspect PostgreSQL models.
4. Inspect repository interfaces.
5. Inspect InfluxDB query implementation.
6. Inspect requirements and environment variables.
7. Confirm Phase 4 tests and reliability status.

Do not assume the context file perfectly reflects the latest
source files.

If the actual source files are not available, request them before
making compatibility-dependent changes.

When implementing:

- Preserve Phase 2.
- Preserve Phase 3.
- Preserve Phase 4.
- Do not rewrite the MQTT consumer.
- Do not change telemetry schema without justification.
- Do not introduce duplicate database configuration.
- Do not create a second MQTT broker.
- Avoid unnecessary abstractions.
- Keep the code modular.
- Use typed request and response schemas.
- Handle errors consistently.
- Test each endpoint.
- Provide complete modified files when changing existing files.
- Do not provide partial code fragments when a full file replacement
  is needed to prevent inconsistent implementations.

---

# 26. Phase 5 Execution Plan

Recommended implementation order:

## Step 1 — API foundation

- FastAPI app.
- Configuration.
- Dependency injection.
- Lifespan.
- Logging.
- CORS.
- Health endpoints.

## Step 2 — PostgreSQL API repositories

- Factory queries.
- Production line queries.
- Motor queries.
- Maintenance queries.
- Pagination.

Reuse the Phase 4 database models.

## Step 3 — Service layer

Implement:

- Factory service.
- Line service.
- Motor service.
- Maintenance service.

Keep API business logic out of route handlers.

## Step 4 — Factory and line endpoints

Implement and test:

- Factory list.
- Factory detail.
- Factory lines.
- Line detail.
- Line motors.

## Step 5 — Motor endpoints

Implement:

- Motor list.
- Filtering.
- Motor detail.
- Factory-scoped motor detail.
- Current status.

## Step 6 — InfluxDB telemetry API

Implement:

- Latest telemetry.
- Historical telemetry.
- Start/end filtering.
- Time-range validation.
- Pagination or limits.
- Field selection.

Use the existing InfluxDB integration.

## Step 7 — Maintenance API

Implement:

- List maintenance history.
- Create maintenance record.
- Validate timestamps and required fields.
- Verify motor existence.

## Step 8 — Integration testing

Test API responses using the actual database infrastructure.

Test:

- Valid requests.
- Missing records.
- Invalid IDs.
- Invalid query parameters.
- PostgreSQL unavailable.
- InfluxDB unavailable.
- Empty telemetry results.
- Pagination.
- Filtering.

## Step 9 — Phase 5 completion

Confirm all API tests pass.

Document:

- Endpoints.
- Response formats.
- Error formats.
- Run commands.
- Environment variables.

Produce:

PHASE_5_CONTEXT.md

for the following phase.

---

# 27. Phase 5 Boundaries

Phase 5 is backend API development.

It does NOT include:

- React UI implementation.
- Dashboard visual design.
- ML model training.
- Predictive inference.
- Node-RED automation.
- MQTT publisher redesign.
- Simulator redesign.
- Dataset preprocessing redesign.

Those remain separate responsibilities.

---

# 28. Project Development Rules

These rules apply to subsequent phases.

1. Preserve the existing architecture.
2. Do not invent source files or functionality.
3. Inspect actual files when compatibility matters.
4. Ask for missing source code when necessary.
5. Deliver complete files for file replacements.
6. Avoid duplicated implementations.
7. Keep components independently testable.
8. Run tests after changes.
9. Do not claim tests passed without actual execution.
10. Explain the purpose of new components.
11. Keep database persistence reliable.
12. Maintain the telemetry contract.
13. Do not silently discard valid telemetry.
14. Never claim exactly-once delivery without a real guarantee.
15. Keep phases clearly separated.
16. Prefer code directly usable in the existing project.

---

# 29. Immediate Starting Point for Phase 5

Begin Phase 5 with an audit of the current backend source files
and database repository interfaces.

Then implement the FastAPI foundation:

- application creation,
- lifespan,
- dependency injection,
- PostgreSQL dependency,
- InfluxDB dependency,
- health routes,
- CORS,
- API configuration.

Do not begin with the React dashboard.

The first goal is a clean, testable API that exposes the data
already collected by Phase 4.