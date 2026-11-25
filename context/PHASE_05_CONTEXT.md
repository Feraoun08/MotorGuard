# PHASE 5 — REST API, Maintenance Management & Backend Testing

## 1. Phase Overview

Phase 5 of MotorGuard introduces the REST API layer that exposes the system's persisted industrial data to external clients.

The objective is to make MotorGuard accessible through HTTP endpoints without interfering with the MQTT ingestion pipeline implemented during Phase 4.

Phase 5 transforms the existing backend into an accessible service capable of:

- Retrieving factories.
- Retrieving production lines.
- Retrieving motors.
- Filtering and paginating motor lists.
- Retrieving the latest telemetry for a motor.
- Retrieving historical telemetry.
- Recording maintenance operations.
- Retrieving maintenance history.
- Checking API health and service readiness.

The API is built using FastAPI, SQLAlchemy, PostgreSQL, and InfluxDB.

An important architectural principle is maintained throughout this phase:

**The REST API is a separate application entrypoint from the Phase 4 MQTT ingestion worker.**

---

# 2. Phase 5 Objectives

The principal objectives of this phase are:

### 2.1 REST API implementation

Expose the previously implemented backend data through HTTP endpoints.

### 2.2 Database integration

Retrieve factories, production lines, motors, and maintenance records from PostgreSQL.

### 2.3 Telemetry integration

Retrieve telemetry data from InfluxDB using factory-scoped motor identifiers.

### 2.4 Maintenance management

Allow maintenance records to be created and retrieved through the REST API.

### 2.5 Data validation

Validate incoming requests using Pydantic schemas and FastAPI request validation.

### 2.6 Error handling

Handle:

- Missing factories.
- Missing production lines.
- Missing motors.
- Missing telemetry.
- Invalid dates.
- Invalid query parameters.
- Invalid maintenance payloads.

### 2.7 Testing

Validate the API through focused tests at both the service and router levels.

---

# 3. Overall Architecture

Phase 5 introduces a REST API layer on top of the database and telemetry infrastructure already developed.

```text
                         MotorGuard
                             |
            +----------------+----------------+
            |                                 |
      Phase 4 Ingestion                  Phase 5 REST API
            |                                 |
      MQTT Subscriber                    FastAPI Application
            |                                 |
      Message Validation              API Routers
            |                                 |
      PostgreSQL Inbox                API Services
            |                                 |
      Ingestion Worker                 Repositories
            |                                 |
      InfluxDB Persistence          +------------+------------+
                                   |                       |
                              PostgreSQL               InfluxDB
```

Phase 4 and Phase 5 operate independently but share the same backend infrastructure.

Phase 4 is responsible for receiving and persisting telemetry.

Phase 5 is responsible for exposing persisted information and managing maintenance records.

---

# 4. Phase 4 and Phase 5 Separation

The existing Phase 4 entrypoint must remain unchanged.

## Phase 4 — Ingestion

Entrypoint:

```bash
python -m backend.main
```

Responsibilities:

- MQTT connection.
- MQTT subscription.
- Incoming telemetry reception.
- Payload validation.
- Topic validation.
- PostgreSQL inbox persistence.
- Event deduplication.
- Retry management.
- Telemetry persistence to InfluxDB.
- Worker lifecycle management.

## Phase 5 — REST API

Entrypoint:

```bash
python -m backend.api_main
```

Responsibilities:

- HTTP request handling.
- Factory retrieval.
- Production line retrieval.
- Motor retrieval.
- Telemetry queries.
- Maintenance operations.
- API health checks.

The API must not replace, modify, or interfere with the Phase 4 worker lifecycle.

Both applications can run simultaneously.

---

# 5. Project Structure

The Phase 5 implementation introduces or uses the following structure:

```text
backend/
│
├── __init__.py
├── main.py
├── api_main.py
├── config.py
├── logging_config.py
│
├── api/
│   │
│   ├── __init__.py
│   ├── app.py
│   ├── dependencies.py
│   ├── repositories.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── factories.py
│   │   ├── telemetry.py
│   │   └── maintenance.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── factory.py
│   │   ├── motor.py
│   │   ├── telemetry.py
│   │   └── maintenance.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── factory_service.py
│       ├── telemetry_service.py
│       └── maintenance_service.py
│
├── database/
│   ├── __init__.py
│   ├── models.py
│   ├── postgres.py
│   ├── repositories.py
│   └── influx.py
│
├── mqtt/
│
├── ingestion/
│
├── validation/
│
├── migrations/
│
└── tests/
    ├── test_api_health.py
    ├── test_api_smoke.py
    ├── test_telemetry_service.py
    ├── test_telemetry_router.py
    └── test_maintenance.py
```

The exact directory contents may evolve as subsequent phases are implemented.

---

# 6. Application Architecture

The API follows a layered architecture.

```text
HTTP Request
     |
     v
FastAPI Router
     |
     v
Service Layer
     |
     v
Repository / Database Access
     |
     +----------------------+
     |                      |
     v                      v
 PostgreSQL               InfluxDB
```

## 6.1 Routers

Routers are responsible for:

- Defining HTTP endpoints.
- Reading path parameters.
- Reading query parameters.
- Validating incoming requests.
- Calling the appropriate service.
- Converting errors into HTTP responses.
- Returning response schemas.

Routers should not contain complex business logic or direct database query implementations.

## 6.2 Services

Services implement application-level operations.

Examples:

- Retrieving a factory.
- Validating motor existence before retrieving telemetry.
- Converting InfluxDB records into API response objects.
- Creating maintenance records.
- Retrieving maintenance history.

Services coordinate the repositories and persistence systems.

## 6.3 Repositories

Repositories handle database access.

The factory repository performs operations involving:

- Factories.
- Production lines.
- Motors.

SQLAlchemy is used to construct queries and retrieve records.

## 6.4 Schemas

Pydantic schemas define the structure of API requests and responses.

Schemas are responsible for:

- Input validation.
- Required fields.
- Field types.
- String length restrictions.
- Response serialization.

---

# 7. PostgreSQL Integration

PostgreSQL remains the relational database for MotorGuard.

The API accesses PostgreSQL through SQLAlchemy sessions.

## 7.1 Session management

The API uses the `get_db_session` dependency.

```python
def get_db_session(request):
    session_factory = request.app.state.session_factory

    session = session_factory()

    try:
        yield session
    finally:
        session.close()
```

The session lifecycle is:

1. Receive an HTTP request.
2. Create a database session.
3. Execute API operations.
4. Return the response.
5. Close the session.

The session is not reused between requests.

## 7.2 Existing relational entities

The database includes:

- Factory
- ProductionLine
- Motor
- MaintenanceRecord
- TelemetryInbox

Phase 5 primarily interacts with:

- Factory
- ProductionLine
- Motor
- MaintenanceRecord

The TelemetryInbox remains part of the Phase 4 ingestion mechanism.

## 7.3 Factory-scoped identifiers

Motors are identified using a composite identifier:

```text
(factory_id, motor_id)
```

Production lines are also factory-scoped:

```text
(factory_id, line_id)
```

This is important because motor IDs and line IDs are not necessarily globally unique.

API queries must preserve factory scope.

A motor query must not retrieve a motor belonging to another factory simply because the motor identifier is identical.

---

# 8. Factory and Motor Repository

The factory repository provides read operations for factories, production lines, and motors.

## 8.1 Factory operations

Implemented operations:

```python
list_factories()
get_factory(factory_id)
count_factories()
```

Responsibilities:

- Retrieve all factories.
- Retrieve one factory.
- Count factories.

Factories are ordered by identifier when listing.

## 8.2 Production line operations

Implemented operations:

```python
list_lines(factory_id)
get_line(factory_id, line_id)
count_lines(factory_id)
```

Responsibilities:

- Retrieve production lines belonging to a factory.
- Retrieve one line using its factory-scoped identifier.
- Count production lines belonging to a factory.

## 8.3 Motor operations

Implemented operations:

```python
list_motors_by_line(factory_id, line_id)
get_motor(factory_id, motor_id)
list_motors(factory_id=None, line_id=None, limit=100, offset=0)
count_motors(factory_id=None, line_id=None)
```

Responsibilities:

- Retrieve motors associated with a production line.
- Retrieve a motor within a factory.
- Retrieve filtered motor lists.
- Support pagination.
- Count motors according to filters.

## 8.4 Pagination

The motor listing supports:

```text
limit
offset
```

The repository applies:

```python
.limit(limit)
.offset(offset)
```

This allows clients to retrieve large motor collections incrementally instead of returning the entire collection in one response.

---

# 9. Factory API

The factory API provides access to the factory hierarchy.

The hierarchy is:

```text
Factory
   |
   +-- Production Lines
          |
          +-- Motors
```

## 9.1 Factory endpoints

```http
GET /api/factories
```

Returns the available factories.

```http
GET /api/factories/{factory_id}
```

Returns a specific factory.

```http
GET /api/factories/{factory_id}/lines
```

Returns the production lines belonging to the factory.

```http
GET /api/factories/{factory_id}/lines/{line_id}
```

Returns a specific production line.

```http
GET /api/factories/{factory_id}/lines/{line_id}/motors
```

Returns the motors associated with the specified production line.

```http
GET /api/factories/{factory_id}/motors/{motor_id}
```

Returns a specific motor belonging to the factory.

```http
GET /api/motors
```

Returns a motor collection with supported filtering and pagination.

---

# 10. Telemetry API

Telemetry is stored in InfluxDB, not PostgreSQL.

The REST API accesses InfluxDB through the existing `InfluxTelemetryStore` implementation.

The API does not recreate or duplicate telemetry persistence logic.

Its responsibility is to retrieve the stored telemetry and convert it into a client-friendly response.

## 10.1 Telemetry endpoint structure

The telemetry routes use factory-scoped motor identifiers:

```text
/api/factories/{factory_id}/motors/{motor_id}/telemetry
```

## 10.2 Latest telemetry

Endpoint:

```http
GET /api/factories/{factory_id}/motors/{motor_id}/telemetry/latest
```

Returns the latest available telemetry for a motor.

The service first validates motor existence.

It then queries InfluxDB.

If no telemetry exists, the router returns:

```http
404 Not Found
```

Response detail:

```json
{
  "detail": "No telemetry available for this motor"
}
```

If the motor does not exist, the API returns a 404 response.

## 10.3 Historical telemetry

Endpoint:

```http
GET /api/factories/{factory_id}/motors/{motor_id}/telemetry
```

Query parameters:

```text
start
end
limit
```

Example:

```http
GET /api/factories/factory-01/motors/motor-01/telemetry?start=2026-11-25T17:00:00%2B00:00&end=2026-11-25T19:00:00%2B00:00&limit=100
```

The API supports:

- Start timestamp.
- End timestamp.
- Maximum number of returned records.

The default limit is:

```text
500
```

The allowed limit range is:

```text
1–5000
```

## 10.4 History validation

The history router validates the requested time range.

### Timezone validation

Both `start` and `end` must contain timezone information.

Timezone-naive values are rejected.

Example invalid request:

```text
start=2026-11-25T17:00:00
```

Response:

```http
400 Bad Request
```

### Range validation

The start timestamp must be earlier than the end timestamp.

Invalid:

```text
start = 19:00
end   = 17:00
```

Response:

```http
400 Bad Request
```

### Limit validation

The limit must be between 1 and 5000.

Values outside the range are rejected by FastAPI validation.

Response:

```http
422 Unprocessable Entity
```

---

# 11. Telemetry Service

File:

```text
backend/api/services/telemetry_service.py
```

The `TelemetryService` handles telemetry retrieval and transformation.

## 11.1 Dependencies

The service receives:

```python
session
influx_store
```

It uses:

- `FactoryService` for motor existence validation.
- `InfluxTelemetryStore` for telemetry retrieval.

## 11.2 Motor validation

Before retrieving telemetry, the service verifies that the requested motor exists.

This prevents queries from being performed for invalid factory/motor combinations.

The validation uses:

```python
self.factory_service.get_motor(
    factory_id,
    motor_id,
)
```

## 11.3 Latest telemetry retrieval

The service calls:

```python
self.influx_store.get_latest_motor_telemetry(
    factory_id,
    motor_id,
)
```

If no record exists:

```python
return None
```

Otherwise, the record is converted into the API response format.

## 11.4 History retrieval

The service calls:

```python
self.influx_store.query_motor_telemetry(
    factory_id=factory_id,
    motor_id=motor_id,
    start=...,
    end=...,
    limit=limit,
)
```

The requested timestamps are converted to UTC before constructing the InfluxDB query time expressions.

The returned records are transformed into API response objects.

---

# 12. Telemetry Record Transformation

InfluxDB records are transformed into a structured response containing:

```json
{
  "factory_id": "factory-01",
  "line_id": "line-01",
  "motor_id": "motor-01",
  "timestamp": "2026-11-25T18:00:00+00:00",
  "motor_state": "running",
  "bearing_condition": "normal",
  "ground_truth": "normal",
  "is_simulated": "true",
  "vibration": {},
  "sensors": {},
  "additional_tags": {}
}
```

The exact values depend on the retrieved telemetry record.

## 12.1 Vibration fields

The service supports the following vibration feature fields:

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

These are collected into the `vibration` object.

Example:

```json
{
  "vibration": {
    "max": 5.2,
    "min": -4.8,
    "mean": 0.1,
    "sd": 1.2,
    "rms": 2.4,
    "skewness": 0.3,
    "kurtosis": 3.1,
    "crest": 2.8,
    "form": 1.7
  }
}
```

Missing vibration fields are omitted from the returned object.

## 12.2 Additional sensor fields

The service supports:

```text
temperature
current
rpm
```

These are collected into the `sensors` object.

Example:

```json
{
  "sensors": {
    "temperature": 45.5,
    "current": 2.1,
    "rpm": 1450
  }
}
```

Missing sensor fields are omitted.

## 12.3 Additional tags

The service identifies known telemetry metadata.

Known fields are excluded from `additional_tags`.

Unknown additional fields are preserved.

This allows the telemetry response to support extra tags without treating the core telemetry structure as unknown data.

## 12.4 Timestamp conversion

If `_time` is a Python datetime, it is converted into ISO 8601 format.

Example:

```text
2026-11-25T18:00:00+00:00
```

This allows consistent timestamp serialization in the API.

---

# 13. InfluxDB Integration

The existing InfluxDB implementation is reused.

The API application initializes the telemetry store using the backend configuration:

```python
InfluxTelemetryStore(
    config.influx_url,
    config.influx_token,
    config.influx_org,
    config.influx_bucket,
)
```

The store is placed in application state and accessed by the telemetry router through the request.

## 13.1 Application state

The telemetry store is accessible through:

```python
request.app.state.influx_store
```

The telemetry router creates its service using:

```python
TelemetryService(
    session=session,
    influx_store=request.app.state.influx_store,
)
```

This separates API routing from the underlying InfluxDB implementation.

## 13.2 InfluxDB responsibilities

The store is responsible for:

- Querying telemetry.
- Filtering by factory.
- Filtering by motor.
- Querying a time range.
- Returning the latest telemetry.
- Limiting returned records.

The API service is responsible for:

- Validating the motor.
- Calling the store.
- Transforming records.
- Returning API-compatible structures.

---

# 14. Maintenance API

Maintenance management is the write-oriented component of Phase 5.

Unlike telemetry, which is retrieved from InfluxDB, maintenance records are stored in PostgreSQL.

The maintenance API allows users or future frontend applications to record maintenance operations and retrieve historical maintenance information.

## 14.1 Maintenance endpoints

### Retrieve maintenance history

```http
GET /api/factories/{factory_id}/motors/{motor_id}/maintenance
```

Returns maintenance records associated with the specified motor.

If the motor does not exist:

```http
404 Not Found
```

Response:

```json
{
  "detail": "Motor not found"
}
```

If the motor exists but has no maintenance records:

```http
200 OK
```

Response:

```json
[]
```

### Create maintenance record

```http
POST /api/factories/{factory_id}/motors/{motor_id}/maintenance
```

Successful creation returns:

```http
201 Created
```

The request body contains:

```json
{
  "maintenance_type": "inspection",
  "description": "Bearing inspection",
  "performed_at": "2026-11-25T17:00:00+00:00"
}
```

---

# 15. Maintenance Schemas

File:

```text
backend/api/schemas/maintenance.py
```

## 15.1 MaintenanceCreate

The input schema contains:

### maintenance_type

```python
maintenance_type: str
```

Constraints:

```text
Minimum length: 1
Maximum length: 100
```

### description

```python
description: str
```

Constraints:

```text
Minimum length: 1
Maximum length: 2000
```

### performed_at

```python
performed_at: datetime
```

This identifies when the maintenance operation was performed.

## 15.2 MaintenanceResponse

The response schema contains:

```text
id
factory_id
motor_id
maintenance_type
description
performed_at
created_at
```

The record ID uses UUID.

The schema uses:

```python
ConfigDict(from_attributes=True)
```

This allows response serialization directly from SQLAlchemy model instances.

---

# 16. Maintenance Service

File:

```text
backend/api/services/maintenance_service.py
```

The maintenance service is responsible for:

- Checking whether a motor exists.
- Retrieving maintenance history.
- Creating maintenance records.
- Committing database changes.
- Refreshing created records.

## 16.1 Motor lookup

The motor is retrieved using both identifiers:

```python
Motor.factory_id == factory_id
Motor.id == motor_id
```

The service returns:

```python
motor
```

or:

```python
None
```

This maintains factory-level isolation.

## 16.2 Maintenance history

The history query filters using:

```python
MaintenanceRecord.factory_id == factory_id
MaintenanceRecord.motor_id == motor_id
```

Records are ordered by:

```python
MaintenanceRecord.performed_at.desc()
```

This means the latest performed maintenance appears first.

If the motor does not exist:

```python
return None
```

If the motor exists but no records are available:

```python
return []
```

## 16.3 Maintenance creation

Creation follows this sequence:

1. Verify that the motor exists.
2. Create a `MaintenanceRecord`.
3. Populate the factory and motor identifiers.
4. Populate the maintenance type.
5. Populate the description.
6. Populate the performed timestamp.
7. Add the record to the SQLAlchemy session.
8. Commit the transaction.
9. Refresh the record.
10. Return the persisted record.

The service returns `None` if the requested motor does not exist.

It does not create maintenance records for unknown motors.

---

# 17. API Health and Readiness

Health endpoints provide information about the API application.

The API includes:

```http
GET /api/health
```

and:

```http
GET /api/health/ready
```

These endpoints serve different purposes.

## 17.1 Health

Health indicates that the API application is running and responding.

It is useful for:

- Basic monitoring.
- Container health checks.
- Deployment verification.
- API availability checks.

## 17.2 Readiness

Readiness indicates whether the API is ready to serve its intended operations.

It can be used to verify dependencies and application initialization.

The health and readiness endpoints are included in the Phase 5 route tests.

---

# 18. API Endpoint Summary

## Health

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | API health |
| GET | `/api/health/ready` | API readiness |

## Factories and hierarchy

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/factories` | List factories |
| GET | `/api/factories/{factory_id}` | Get factory |
| GET | `/api/factories/{factory_id}/lines` | List factory lines |
| GET | `/api/factories/{factory_id}/lines/{line_id}` | Get production line |
| GET | `/api/factories/{factory_id}/lines/{line_id}/motors` | List motors on line |
| GET | `/api/factories/{factory_id}/motors/{motor_id}` | Get motor |

## Motor listing

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/motors` | List motors with filters and pagination |

## Telemetry

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/factories/{factory_id}/motors/{motor_id}/telemetry/latest` | Latest telemetry |
| GET | `/api/factories/{factory_id}/motors/{motor_id}/telemetry` | Historical telemetry |

## Maintenance

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/factories/{factory_id}/motors/{motor_id}/maintenance` | Maintenance history |
| POST | `/api/factories/{factory_id}/motors/{motor_id}/maintenance` | Create maintenance record |

---

# 19. Error Handling

The API uses HTTP status codes to represent the result of requests.

| Status | Meaning | Example |
|---|---|---|
| 200 | Successful retrieval | Factory or telemetry history returned |
| 201 | Successfully created | Maintenance record created |
| 400 | Invalid request parameters | Invalid telemetry time range |
| 404 | Resource not found | Unknown motor or no latest telemetry |
| 422 | Request validation failure | Invalid maintenance payload or limit |

## 19.1 HTTP 400

Used by the telemetry router for invalid time range requests.

Examples:

- Timezone missing.
- Start timestamp is later than or equal to end timestamp.

## 19.2 HTTP 404

Used when the requested resource does not exist.

Examples:

- Factory not found.
- Motor not found.
- Maintenance history requested for a nonexistent motor.
- Latest telemetry unavailable.

## 19.3 HTTP 422

Used for request validation failures.

Examples:

- Missing required fields.
- Invalid datetime.
- Empty maintenance type.
- Empty maintenance description.
- Limit outside the supported range.

---

# 20. Testing Strategy

Phase 5 uses focused tests rather than unnecessarily testing every internal implementation detail.

Tests are divided into three levels:

1. API health and smoke tests.
2. Service tests.
3. Router tests.

The test suite uses mocks where external infrastructure would be unnecessary.

This means the API tests do not require MQTT communication or actual InfluxDB queries.

---

# 21. Health and Smoke Tests

Files:

```text
backend/tests/test_api_health.py
backend/tests/test_api_smoke.py
```

## 21.1 Health tests

These tests verify:

- Health endpoint availability.
- Expected health response.
- Health response structure.

## 21.2 Smoke tests

These tests verify:

- OpenAPI availability.
- Route registration.
- Expected HTTP methods.
- Presence of the Phase 5 endpoints.

These tests provide a quick way to detect accidental route removal or incorrect API registration.

Previously validated result:

```text
4 passed
```

---

# 22. Telemetry Service Tests

File:

```text
backend/tests/test_telemetry_service.py
```

These tests focus on telemetry service logic.

The InfluxDB store is mocked.

## Covered scenarios

### Latest telemetry

- Latest telemetry retrieval.
- Correct factory ID.
- Correct line ID.
- Correct motor ID.
- Correct motor state.
- Correct vibration values.
- Correct sensor values.
- Correct handling of no telemetry.

### Motor validation

- Unknown motor raises `LookupError`.
- InfluxDB is not queried for an unknown motor.

### Record conversion

- Datetime conversion to ISO 8601.
- Vibration field extraction.
- Sensor field extraction.
- Missing optional fields.
- Additional tag handling.

### Historical telemetry

- History retrieval.
- Correct factory and motor filtering.
- Correct limit forwarding.
- Start and end query generation.
- Empty history handling.
- Unknown motor validation.

Previously validated result:

```text
8 passed
```

---

# 23. Telemetry Router Tests

File:

```text
backend/tests/test_telemetry_router.py
```

These tests verify the telemetry HTTP layer.

The telemetry service is mocked.

## Covered scenarios

### Latest endpoint

- No telemetry returns 404.
- Unknown motor returns 404.

### History endpoint

- Empty history returns 200.
- Correct factory ID.
- Correct motor ID.
- Correct count.
- Correct limit.
- Unknown motor returns 404.

### Request validation

- Missing timezone returns 400.
- Invalid start/end ordering returns 400.
- Limit above 5000 returns 422.

Previously validated result:

```text
6 passed
```

---

# 24. Maintenance Tests

File:

```text
backend/tests/test_maintenance.py
```

These tests cover the maintenance service and router.

The service tests use mocked SQLAlchemy sessions.

The router tests use a mocked maintenance service.

## 24.1 Service tests

### Motor retrieval

- Motor is returned when found.
- `None` is returned when the motor does not exist.

### Maintenance history

- Records are returned.
- Empty history returns an empty list.
- Unknown motor returns `None`.

### Maintenance creation

- Maintenance record is constructed correctly.
- Factory identifier is correct.
- Motor identifier is correct.
- Maintenance type is correct.
- Description is correct.
- Performed timestamp is correct.
- Session add is called.
- Session commit is called.
- Session refresh is called.

### Invalid motor

- Creation returns `None`.
- No record is added.
- No commit occurs.
- No refresh occurs.

## 24.2 Router tests

### GET history

- Successful history retrieval returns 200.
- Empty history returns 200 and an empty list.
- Unknown motor returns 404.

### POST creation

- Successful creation returns 201.
- Response contains the expected fields.
- Unknown motor returns 404.

### Payload validation

- Empty maintenance type returns 422.
- Empty description returns 422.
- Missing performed timestamp returns 422.
- Invalid payload values return 422.

Previously validated result:

```text
16 passed
```

---

# 25. Test Results

The essential Phase 5 test suites have been executed by the developer and all tests passed.

| Test file | Coverage area | Result |
|---|---|---|
| `test_api_health.py` | API health | Passed |
| `test_api_smoke.py` | Route registration and OpenAPI | Passed |
| `test_telemetry_service.py` | Telemetry service logic | 8 passed |
| `test_telemetry_router.py` | Telemetry HTTP layer | 6 passed |
| `test_maintenance.py` | Maintenance service and HTTP layer | 16 passed |

The telemetry and maintenance tests were executed independently and subsequently included in the combined essential Phase 5 test suite.

All tests reported by the developer passed.

## Testing principle

Tests must be considered verified only after they have actually been executed.

The tests described in this document were run in the developer's local environment.

---

# 26. Running Tests

All commands should be executed from the project root.

## Telemetry service tests

```bash
pytest backend/tests/test_telemetry_service.py -v
```

## Telemetry router tests

```bash
pytest backend/tests/test_telemetry_router.py -v
```

## Maintenance tests

```bash
pytest backend/tests/test_maintenance.py -v
```

## Health and smoke tests

```bash
pytest backend/tests/test_api_health.py backend/tests/test_api_smoke.py -v
```

## Combined essential Phase 5 suite

```bash
pytest backend/tests/test_api_health.py backend/tests/test_api_smoke.py backend/tests/test_telemetry_service.py backend/tests/test_telemetry_router.py backend/tests/test_maintenance.py -v
```

## Run all backend tests

```bash
pytest backend/tests -v
```

This last command should be used as the broader verification command as the backend test suite grows.

---

# 27. Running MotorGuard

Phase 4 and Phase 5 are separate processes.

## Terminal 1 — Phase 4 ingestion

```bash
python -m backend.main
```

This starts the MQTT ingestion and persistence worker.

## Terminal 2 — Phase 5 API

```bash
python -m backend.api_main
```

This starts the FastAPI API application.

Both applications should use the existing environment configuration and shared PostgreSQL/InfluxDB infrastructure.

---

# 28. API Documentation

FastAPI automatically provides interactive API documentation through OpenAPI.

Once the API is running, open:

```text
http://127.0.0.1:8000/docs
```

The Swagger UI can be used to:

- Inspect endpoints.
- Review request schemas.
- Submit test requests.
- Inspect response codes.
- Verify required parameters.
- Test maintenance creation.
- Test telemetry retrieval.

The OpenAPI schema is also useful for future frontend development.

---

# 29. Architectural Decisions

## 29.1 Separate API from ingestion

The REST API is not integrated directly into the MQTT worker.

This allows the API and ingestion worker to:

- Run independently.
- Be restarted independently.
- Scale independently.
- Maintain separate responsibilities.

## 29.2 PostgreSQL for relational data

PostgreSQL is used for:

- Factory hierarchy.
- Production lines.
- Motors.
- Maintenance records.
- Ingestion inbox.

Relational entities are managed through SQLAlchemy.

## 29.3 InfluxDB for telemetry

InfluxDB remains the time-series database.

This is appropriate for:

- Vibration data.
- Temperature.
- Current.
- RPM.
- Time-range queries.
- Latest telemetry retrieval.

## 29.4 Factory-scoped identifiers

The API preserves factory-level isolation.

The motor identifier alone is not sufficient to identify a motor.

The combination:

```text
factory_id + motor_id
```

is used for motor retrieval.

## 29.5 Service layer

The API uses services to separate application behavior from routing.

This makes the application easier to test without starting external infrastructure.

## 29.6 Mock-based tests

External infrastructure is mocked in service/router tests where practical.

The objective is to test application behavior without requiring:

- An active MQTT broker.
- Incoming MQTT messages.
- A live InfluxDB query.
- A full external environment for every test.

---

# 30. Phase 5 Limitations and Remaining Considerations

Phase 5 has reached its essential implementation and testing milestone.

However, passing tests does not mean every production concern is complete.

The following considerations remain appropriate for future improvements.

## 30.1 Authentication and authorization

The current API testing phase does not establish a complete authentication system.

Future development may include:

- API authentication.
- User management.
- Role-based permissions.
- Authorization for maintenance creation.
- Factory-level access restrictions.

## 30.2 API rate limiting

The API does not yet have a documented rate-limiting implementation as part of this phase.

Rate limiting may become necessary when the API is publicly or broadly exposed.

## 30.3 Pagination standards

Motor listing supports limit and offset.

Future API improvements may include:

- Consistent pagination metadata.
- Maximum page-size policy.
- Cursor-based pagination if datasets become large.

## 30.4 Maintenance validation improvements

Future maintenance features may include:

- Maintenance categories.
- Technician identification.
- Maintenance duration.
- Parts replaced.
- Cost.
- Preventive versus corrective maintenance.
- Maintenance attachments.
- Work-order status.

These are not required to validate the current Phase 5 implementation.

## 30.5 Telemetry performance

Future performance work may include:

- Query optimization.
- Maximum query range policies.
- Aggregated telemetry.
- Downsampling.
- Caching latest telemetry.
- High-volume pagination strategies.

## 30.6 Logging and observability

Future improvements may include:

- Request correlation IDs.
- API request metrics.
- Endpoint latency metrics.
- Error-rate monitoring.
- Centralized logs.
- Database performance monitoring.

## 30.7 Database integration testing

The essential maintenance tests currently use mocked SQLAlchemy sessions.

Future tests could validate the complete persistence flow against a dedicated test PostgreSQL database, including:

- Actual insertion.
- Actual retrieval.
- Composite foreign keys.
- Factory/motor isolation.
- Transaction rollback.
- Database constraints.

Such tests are complementary to the current unit tests, not replacements for them.

---

# 31. Phase 5 Completion Criteria

Phase 5 has achieved its essential objectives.

| Requirement | Status |
|---|---|
| FastAPI application | Implemented |
| Separate API entrypoint | Implemented |
| Health endpoint | Implemented |
| Readiness endpoint | Implemented |
| Factory API | Implemented |
| Production line API | Implemented |
| Motor API | Implemented |
| Motor filtering | Implemented |
| Motor pagination | Implemented |
| Latest telemetry API | Implemented |
| Historical telemetry API | Implemented |
| Telemetry conversion | Implemented |
| Telemetry validation | Implemented |
| Maintenance history API | Implemented |
| Maintenance creation API | Implemented |
| Pydantic validation | Implemented |
| 404 handling | Implemented |
| 400 telemetry range validation | Implemented |
| 422 request validation | Implemented |
| Health tests | Passed |
| Smoke tests | Passed |
| Telemetry service tests | Passed |
| Telemetry router tests | Passed |
| Maintenance tests | Passed |
| Combined essential Phase 5 tests | Passed |

---

# 32. Final Phase 5 Outcome

Phase 5 provides MotorGuard with a working backend REST interface.

The system can now expose its factory structure, retrieve motors, access time-series telemetry, and manage maintenance records.

The architecture preserves the separation between the MQTT ingestion pipeline and the REST API while allowing both applications to work with the same persisted data.

The essential API behavior has been validated through automated tests covering:

- Application health.
- Route registration.
- Telemetry retrieval.
- Telemetry transformation.
- Telemetry validation.
- Motor existence validation.
- Maintenance history.
- Maintenance creation.
- Request validation.
- Error handling.

Phase 5 is considered **completed at the essential backend API implementation and testing level**.

It is ready to serve as the foundation for the next phase of MotorGuard development.

---

# 33. Recommended Next Phase

The next logical phase is the frontend and operational dashboard.

The API now provides the foundation required for a dashboard that can display:

- Factories.
- Production lines.
- Motors.
- Motor states.
- Latest telemetry.
- Vibration measurements.
- Temperature.
- Current.
- RPM.
- Historical telemetry charts.
- Maintenance history.
- Maintenance record creation.

A possible next phase could be organized as:

### Phase 6 — Monitoring Dashboard & API Integration

1. Frontend architecture and API client.
2. Factory and production-line navigation.
3. Motor overview dashboard.
4. Motor status indicators.
5. Latest telemetry cards.
6. Historical telemetry charts.
7. Maintenance history interface.
8. Maintenance creation form.
9. Loading, error, and empty states.
10. Frontend integration and testing.

This phase should build on the completed REST API rather than introducing another backend architecture unnecessarily.

---

# 34. Context for Future Chat Sessions

When continuing MotorGuard in a new chat, use this document as the Phase 5 reference.

The following principles should be preserved:

- Phase 4 ingestion remains separate from Phase 5 API.
- Do not overwrite `backend/main.py`.
- The REST API is launched through `backend.api_main`.
- PostgreSQL is used for relational entities and maintenance records.
- InfluxDB is used for time-series telemetry.
- Motors are factory-scoped.
- Telemetry queries must preserve factory and motor filtering.
- Maintenance operations must validate motor existence.
- The API service/router separation should be preserved.
- Existing passing tests must not be unnecessarily rewritten.
- New features should be implemented incrementally.
- When modifying a file, provide the complete modified file when appropriate, not disconnected fragments.
- Run tests after changes and distinguish verified results from expected results.

## Current verified milestone

```text
PHASE 1 — Dataset & Classification
Completed

PHASE 2 — Motor & Factory Simulation
Completed

PHASE 3 — MQTT Communication
Completed

PHASE 4 — Reliable Telemetry Ingestion
Completed

PHASE 5 — REST API & Maintenance Management
Completed and tested
```

**MotorGuard now has a simulated motor environment, telemetry generation, MQTT ingestion, persistent storage, and a tested REST API. The next major step is to build the monitoring interface on top of this backend.**
