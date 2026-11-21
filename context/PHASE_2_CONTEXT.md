# MotorGuard — Phase 2 Context
## Virtual Factory Simulation

---

## 1. Project Overview

MotorGuard is a predictive maintenance system designed to monitor industrial motors, detect bearing faults, and eventually provide real-time monitoring through a connected application.

Phase 2 focuses on creating a **virtual industrial factory simulation** capable of generating realistic motor operating data and fault scenarios.

The simulator acts as the source of data for future integration with:

- Machine Learning models.
- Backend services.
- MQTT communication.
- Databases.
- Frontend dashboards.
- Real-time monitoring.
- Predictive maintenance workflows.

The goal of Phase 2 is to create a simulation environment that can generate data for multiple motors operating independently under different conditions.

---

# 2. Phase 2 Objectives

The objectives of Phase 2 are:

- Build a virtual motor simulation system.
- Use the existing prepared CWRU dataset as the source of vibration features.
- Simulate multiple independent motors.
- Support healthy and faulty operating conditions.
- Simulate additional sensors such as temperature, current and RPM.
- Allow fault scenarios to be changed dynamically.
- Build a factory simulation engine.
- Generate standardized telemetry.
- Validate generated data.
- Verify compatibility with the existing Machine Learning model.
- Prepare the simulation architecture for future backend and MQTT integration.

The simulator does not generate vibration measurements directly from physical equations.

Instead, it samples vibration features from the prepared dataset and combines them with synthetic operating sensor values.

---

# 3. Phase 2 Architecture

The simulator is organized into separate modules, each responsible for one specific function.

```text
                    ┌─────────────────────────┐
                    │      CWRU Dataset      │
                    │  Prepared CSV Dataset  │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Dataset Provider      │
                    │ Loading & Sampling     │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     Virtual Motors      │
                    │  Motor State & Config  │
                    └────────────┬───────────┘
                                 │
                ┌────────────────┴────────────────┐
                │                                 │
                ▼                                 ▼
      ┌─────────────────────┐          ┌─────────────────────┐
      │ Vibration Features  │          │ Synthetic Sensors  │
      │ Dataset Sampling    │          │ Temp/Current/RPM   │
      └──────────┬──────────┘          └──────────┬──────────┘
                 │                                 │
                 └────────────────┬────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │    Factory Engine      │
                    │ Multi-Motor Simulation │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      Telemetry         │
                    │ Validation & JSON      │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  Model Compatibility   │
                    │  Existing ML Model    │
                    └─────────────────────────┘
```

---

# 4. Subphase Breakdown

## 2.1 — Simulation Foundation and Configuration

The simulation foundation establishes the shared configuration used throughout the simulator.

The configuration module centralizes:

- Dataset paths.
- Feature definitions.
- Target column.
- Available bearing conditions.
- Motor states.
- Sampling modes.
- Default factory identifiers.
- Default production-line identifiers.

### Dataset configuration

The prepared dataset is located at:

```text
data/feature_time_48k_2048_load1.csv
```

### Feature columns

The simulator uses the following nine vibration features:

```python
FEATURE_COLUMNS = [
    "max",
    "min",
    "mean",
    "sd",
    "rms",
    "skewness",
    "kurtosis",
    "crest",
    "form",
]
```

### Target column

```python
TARGET_COLUMN = "fault"
```

### Available bearing conditions

The simulator supports ten classes:

```python
BEARING_CONDITIONS = [
    "Ball_007_1",
    "Ball_014_1",
    "Ball_021_1",
    "IR_007_1",
    "IR_014_1",
    "IR_021_1",
    "OR_007_6_1",
    "OR_014_6_1",
    "OR_021_6_1",
    "Normal_1",
]
```

### Motor states

```text
STOPPED
RUNNING
WARNING
FAULT
```

### Sampling modes

```text
RANDOM
SEQUENTIAL
```

---

## 2.2 — Dataset Provider

File:

```text
simulator/dataset_provider.py
```

The DatasetProvider is responsible for interacting with the prepared vibration dataset.

Its responsibilities include:

- Loading the CSV dataset.
- Accessing vibration data.
- Grouping samples by bearing condition.
- Sampling data from a requested condition.
- Providing vibration feature vectors.
- Returning ground-truth labels.
- Supporting random and sequential sampling.

The DatasetProvider separates dataset management from motor simulation.

Motors do not directly load or manipulate the CSV file.

Instead, they request samples through the DatasetProvider.

### Sampling concept

```text
Virtual Motor
     │
     ▼
DatasetProvider.sample(condition)
     │
     ▼
Selected dataset sample
     │
     ├── Vibration Features
     │
     └── Ground Truth
```

The resulting sample contains:

- The nine vibration features.
- The corresponding ground-truth bearing condition.

---

## 2.3 — Virtual Motor Simulation

File:

```text
simulator/motor.py
```

The VirtualMotor represents an individual motor in the simulated factory.

Each motor has its own configuration and state.

### Motor responsibilities

- Motor initialization.
- Motor identification.
- Factory identification.
- Production-line identification.
- Bearing-condition configuration.
- Motor state management.
- Start and stop operations.
- Vibration measurement generation.
- Sampling configuration.
- Serialization of motor information.

### Motor operating states

| State | Meaning |
|---|---|
| STOPPED | Motor is not operating |
| RUNNING | Motor is operating normally |
| WARNING | Motor is operating under a warning condition |
| FAULT | Motor is in a fault state |

### Motor independence

Each motor has its own:

- ID.
- Configuration.
- Operating state.
- Bearing condition.
- Sampling configuration.

Motors can therefore operate independently within the same simulated factory.

### Vibration generation

The motor requests a sample from the DatasetProvider.

The dataset sample is used to generate a vibration measurement containing the features and ground truth.

The simulator does not modify or retrain the original dataset.

---

## 2.4 — Synthetic Sensor Simulation

File:

```text
simulator/sensors.py
```

The SensorSimulator generates additional synthetic measurements for motors.

The simulated sensors are:

| Sensor | Unit | Purpose |
|---|---|---|
| Temperature | °C | Thermal monitoring |
| Current | A | Electrical operating monitoring |
| RPM | revolutions/minute | Rotational speed monitoring |

These measurements are synthetic and are not extracted from the CWRU vibration dataset.

### Sensor behavior

Sensor values vary according to:

- Motor operating state.
- Whether the motor is faulty.
- Configured baseline values.
- Random variations.
- Warning conditions.

### Sensor configuration

SensorConfig defines parameters such as:

- Normal temperature.
- Normal current.
- Normal RPM.
- Temperature variation.
- Current variation.
- RPM variation.
- Fault-related temperature increase.
- Fault-related current increase.
- Fault-related RPM variation.
- Stopped-motor values.

### Stopped motor behavior

When the motor is stopped:

- Current is zero.
- RPM is zero.
- Temperature is generated around the stopped-motor baseline.

### Running motor behavior

When the motor is running:

- Temperature fluctuates around its normal operating baseline.
- Current fluctuates around its normal operating baseline.
- RPM fluctuates around the normal operating speed.

### Faulty motor behavior

Faulty motors can exhibit:

- Increased temperature.
- Increased current.
- Larger RPM variations.

The sensor simulator is configurable and uses a random generator that can be seeded for reproducibility.

---

## 2.5 — Fault Scenarios

File:

```text
simulator/scenarios.py
```

The scenario module provides predefined fault scenarios.

It separates scenario definitions from motor and factory logic.

### Scenario categories

```text
HEALTHY
BALL_FAULT
INNER_RACE_FAULT
OUTER_RACE_FAULT
```

### Available scenarios

| Scenario | Dataset condition |
|---|---|
| healthy | Normal_1 |
| ball_007 | Ball_007_1 |
| ball_014 | Ball_014_1 |
| ball_021 | Ball_021_1 |
| inner_007 | IR_007_1 |
| inner_014 | IR_014_1 |
| inner_021 | IR_021_1 |
| outer_007 | OR_007_6_1 |
| outer_014 | OR_014_6_1 |
| outer_021 | OR_021_6_1 |

### Scenario responsibilities

- Define available scenarios.
- Map scenarios to dataset conditions.
- Describe fault scenarios.
- Retrieve scenarios by name.
- Validate scenario names.
- Apply scenarios to motors.

### Scenario transitions

A scenario can be changed by updating the motor's bearing-condition configuration.

This changes the class from which the motor samples vibration data.

Scenario transitions do not represent a physical degradation process.

They switch the sampling condition used by the simulator.

---

## 2.6 — Factory Simulation Engine

File:

```text
simulator/factory.py
```

The FactoryEngine is responsible for coordinating multiple virtual motors.

It is the central component of the virtual factory.

### Responsibilities

- Register motors.
- Unregister motors.
- Retrieve motors.
- Start motors.
- Stop motors.
- Change motor scenarios.
- Generate motor readings.
- Generate readings for multiple motors.
- Run periodic simulation cycles.
- Stop the simulation gracefully.
- Isolate individual motor errors.

### FactoryEngine configuration

The engine receives:

- DatasetProvider.
- Optional SensorSimulator.
- Simulation interval.

### Motor registration

Motors are registered with the factory.

Duplicate motor registration is rejected.

### Motor control

The engine exposes operations for:

```text
register_motor()
unregister_motor()
get_motor()
start_motor()
stop_motor()
change_scenario()
```

### Reading generation

For each motor, the engine combines:

```text
Motor Information
      +
Vibration Measurement
      +
Synthetic Sensors
      +
Simulation Metadata
      │
      ▼
Factory Reading
```

### Reading structure

The generated reading includes:

- Timestamp.
- Motor ID.
- Motor name.
- Factory ID.
- Production-line ID.
- Motor state.
- Bearing condition.
- Vibration features.
- Ground truth.
- Sensor values.
- Simulation metadata.

### Running the factory

The FactoryEngine supports:

- Single-cycle execution.
- Continuous execution.
- Limited-cycle execution.
- Reading callbacks.
- Graceful shutdown.

### Error isolation

Errors during the generation of one motor's reading are handled individually.

An error from one motor should not stop the generation of readings for other motors.

### Stopped motors

Stopped motors are skipped by the factory's periodic reading generation.

This means the engine does not emit stopped-motor telemetry during its normal run loop.

---

# 5. Phase 2.7 — Full Validation and Integration Testing

Phase 2.7 validates the complete simulation system.

The purpose is to verify that individual components work together correctly and that generated data follows the expected contract.

## Validation checklist

- CSV loading.
- Sampling from all ten classes.
- Feature-vector structure.
- Missing and infinite value handling.
- Motor initialization.
- Multiple independent motors.
- Motor state changes.
- Scenario transitions.
- Synthetic sensor generation.
- Telemetry serialization.
- JSON Schema validation.
- Graceful simulator shutdown.

### Dataset validation

Verify:

- Dataset loads successfully.
- All ten classes can be sampled.
- Samples contain all expected features.
- Feature values are numeric.
- Feature values are finite.
- Feature ordering is correct.

### Motor validation

Verify:

- Motors initialize correctly.
- Multiple motors can exist simultaneously.
- Motor states are independent.
- Motors can start and stop.
- Motor configurations are maintained independently.

### Scenario validation

Verify:

- Healthy scenario.
- Ball fault scenarios.
- Inner race scenarios.
- Outer race scenarios.
- Scenario switching.
- Invalid scenario handling.

### Sensor validation

Verify:

- Temperature generation.
- Current generation.
- RPM generation.
- Stopped-motor behavior.
- Running-motor behavior.
- Fault-related sensor behavior.
- Numeric validity.

### Factory validation

Verify:

- Motor registration.
- Duplicate registration rejection.
- Motor retrieval.
- Motor removal.
- Motor start and stop.
- Scenario switching.
- Reading generation.
- Multiple motor readings.
- Stopped motor handling.
- Error isolation.
- Simulator shutdown.

---

# 6. Telemetry Contract

Files:

```text
simulator/telemetry.py
simulator/telemetry_schema.json
```

Telemetry serialization creates a standardized representation of the generated motor readings.

The telemetry contract separates internal simulation objects from data exchanged with other systems.

### Telemetry version

```text
1.0
```

### Telemetry structure

```json
{
  "schema_version": "1.0",
  "timestamp": "2026-11-21T17:30:00+00:00",
  "motor_id": "MOTOR_001",
  "motor_name": "Motor 001",
  "factory_id": "FACTORY_001",
  "line_id": "LINE_001",
  "motor_state": "RUNNING",
  "bearing_condition": "Normal_1",
  "vibration": {
    "max": 0.42,
    "min": -0.39,
    "mean": 0.01,
    "sd": 0.12,
    "rms": 0.15,
    "skewness": 0.08,
    "kurtosis": 3.1,
    "crest": 2.8,
    "form": 1.2
  },
  "ground_truth": "Normal_1",
  "sensors": {
    "temperature": 44.8,
    "current": 4.75,
    "rpm": 1748.2
  },
  "simulation": {
    "is_simulated": true,
    "vibration_source": "CWRU_PREPARED_CSV",
    "additional_sensor_source": "SYNTHETIC"
  }
}
```

The values above are illustrative examples, not captured readings.

### Telemetry fields

| Field | Description |
|---|---|
| schema_version | Telemetry contract version |
| timestamp | Reading generation timestamp |
| motor_id | Unique motor identifier |
| motor_name | Motor display name |
| factory_id | Factory identifier |
| line_id | Production-line identifier |
| motor_state | Current motor operating state |
| bearing_condition | Dataset sampling condition |
| vibration | Nine vibration features |
| ground_truth | Actual bearing class |
| sensors | Synthetic sensor measurements |
| simulation | Simulation provenance metadata |

### Telemetry validation

Telemetry validation checks:

- Required fields.
- Timestamp validity.
- Identifier validity.
- Motor-state validity.
- Vibration structure.
- Exact feature ordering.
- Numeric vibration values.
- Finite vibration values.
- Sensor structure.
- Finite sensor values.
- Non-negative sensor values.
- Simulation metadata.

### Serialization

Telemetry is serialized into JSON.

The serializer rejects invalid telemetry and prevents NaN or infinite values from being emitted as non-standard JSON numeric values.

### Deserialization

Incoming JSON can be decoded and validated against the telemetry contract.

The schema version is checked before the payload is accepted.

---

# 7. Phase 2.8 — Model Compatibility and Inference Validation

Files:

```text
simulator/model_compatibility.py
simulator/validate_model.py
```

Phase 2.8 verifies compatibility between generated simulator data and the existing fitted ML model.

This subphase does not retrain the model.

### Objectives

- Load the existing fitted model.
- Optionally load an existing fitted preprocessing artifact.
- Validate the simulator feature contract.
- Validate model input dimensions.
- Validate feature names where available.
- Generate simulator samples.
- Run model inference.
- Compare predictions against ground truth.
- Display representative results.

### Feature contract

The simulator must produce exactly nine features in the required order:

```python
[
    "max",
    "min",
    "mean",
    "sd",
    "rms",
    "skewness",
    "kurtosis",
    "crest",
    "form",
]
```

The contract must not be altered without verifying compatibility with the fitted model.

### Feature validation

The inference compatibility layer checks:

- Feature names.
- Feature ordering.
- Feature count.
- Numeric data types.
- Finite feature values.
- Model input dimensions.

### Model artifacts

The existing fitted model is loaded from disk.

Possible model arrangements include:

#### Complete fitted pipeline

```text
Input Features
      │
      ▼
Saved Preprocessing
      │
      ▼
Saved Classifier
      │
      ▼
Prediction
```

The complete fitted pipeline is loaded as one artifact.

#### Separate artifacts

```text
Raw Features
      │
      ▼
Existing Preprocessor
      │
      ▼
Existing Classifier
      │
      ▼
Prediction
```

The existing fitted preprocessor and classifier are loaded separately.

No new model is trained.

No preprocessing component is refitted.

### Sample inference validation

Representative conditions:

| Motor | Condition | Ground truth |
|---|---|---|
| MOTOR_001 | Healthy | Normal_1 |
| MOTOR_002 | Ball fault 007 | Ball_007_1 |
| MOTOR_003 | Inner race fault 014 | IR_014_1 |

For each sample, the validation script reports:

- Ground truth.
- Model prediction.
- Correctness.

A small sample prediction score is only a demonstration of compatibility and is not a formal model performance evaluation.

---

# 8. Sample Simulation Configuration

The demonstration configuration creates three motors.

```text
MOTOR_001
    └── Normal_1

MOTOR_002
    └── Ball_007_1

MOTOR_003
    └── IR_014_1
```

All motors are registered with the FactoryEngine and started.

The factory generates readings periodically.

The current demonstration uses:

- Three motors.
- Five simulation cycles.
- Two seconds between cycles.
- A fixed random seed for reproducibility.

Expected number of readings:

```text
3 motors × 5 cycles = 15 readings
```

This assumes all readings are generated successfully and no motors are stopped.

---

# 9. Project Structure

```text
MotorGuard/
│
├── simulator/
│   │
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── motor.py
│   ├── dataset_provider.py
│   ├── sensors.py
│   ├── scenarios.py
│   ├── factory.py
│   │
│   ├── telemetry.py
│   ├── telemetry_schema.json
│   │
│   ├── model_compatibility.py
│   └── validate_model.py
│
├── data/
│   └── feature_time_48k_2048_load1.csv
│
├── models/
│   └── Existing fitted model artifacts
│
└── tests/
    │
    ├── test_motor.py
    ├── test_dataset_provider.py
    ├── test_phase_2_4_6.py
    ├── test_phase_2_7.py
    └── test_phase_2_8.py
```

The tree represents the intended Phase 2 organization. Existing model filenames and any additional project files may differ.

---

# 10. Execution Commands

Commands must be executed from the project root:

```text
MotorGuard/
```

## Run the simulator

```powershell
python -m simulator.main
```

## Run Phase 2.7 tests

```powershell
pytest tests/test_phase_2_7.py -v
```

## Run Phase 2.8 tests

```powershell
pytest tests/test_phase_2_8.py -v
```

## Run previous Phase 2 tests

```powershell
pytest tests/test_phase_2_4_6.py -v
```

## Run all tests

```powershell
pytest tests/ -v
```

## Run model compatibility validation

```powershell
python -m simulator.validate_model --model models/your_model.joblib
```

If the preprocessing artifact is separate:

```powershell
python -m simulator.validate_model --model models/your_model.joblib --preprocessor models/your_preprocessor.joblib
```

Replace placeholder paths with the actual fitted artifacts.

---

# 11. Testing Status

The user confirmed that tests for the previous subphases passed and subsequently confirmed that the tests for the final validation subphases also passed.

| Subphase | Component | Status |
|---|---|---|
| 2.1 | Simulation foundation and configuration | Completed |
| 2.2 | Dataset provider | Completed |
| 2.3 | Virtual motor simulation | Completed |
| 2.4 | Synthetic sensor simulation | Completed — tests passed |
| 2.5 | Fault scenarios | Completed — tests passed |
| 2.6 | Factory simulation engine | Completed — tests passed |
| 2.7 | Integration and telemetry validation | Completed — tests passed |
| 2.8 | Model compatibility and inference validation | Completed — tests passed |

The status above reflects the test results reported by the user.

It does not imply that the model inference demonstration was executed against the actual saved model unless the real model artifacts were used and the inference command was executed.

---

# 12. Simulation Limitations

Phase 2 is a virtual simulation environment.

### Vibration

Vibration features are sampled from the prepared dataset.

The simulator does not calculate vibration from a complete physical motor model.

### Additional sensors

Temperature, current and RPM are synthetic.

They are not synchronized real measurements from the CWRU dataset.

### Fault scenarios

Scenario changes switch the vibration sampling condition.

They do not simulate physical bearing damage developing over time.

### Model predictions

Predictions are only meaningful when the input feature contract matches the existing fitted model and its preprocessing.

### Telemetry

Telemetry is validated and serialized locally.

Phase 2 does not yet establish a complete production MQTT or backend transport system.

---

# 13. Architectural Decisions

The following decisions were made during Phase 2.

### 1. Separate responsibilities

Each module has its own responsibility.

```text
config.py
    Configuration and constants

dataset_provider.py
    Dataset loading and sampling

motor.py
    Individual motor behavior

sensors.py
    Additional synthetic measurements

scenarios.py
    Fault scenario definitions

factory.py
    Multi-motor orchestration

telemetry.py
    Data contract, validation and serialization

model_compatibility.py
    Existing model compatibility and inference
```

### 2. Dataset-driven vibration

The simulator uses prepared vibration features instead of attempting to recreate the physical signal.

This preserves compatibility with the existing dataset and ML feature structure.

### 3. Synthetic auxiliary sensors

Temperature, current and RPM are generated independently using configurable simulation parameters.

This allows the factory to provide additional operating context without claiming these sensors are derived from real CWRU measurements.

### 4. Independent motors

Motors have independent identities, configurations and states.

### 5. Configurable fault scenarios

Fault scenarios are centrally defined and applied to motors.

### 6. Factory orchestration

The FactoryEngine manages motor lifecycle operations and periodically generates readings.

### 7. Telemetry standardization

Generated readings are validated and serialized into a versioned JSON structure.

### 8. Existing model reuse

The existing fitted model and preprocessing artifacts are reused for compatibility validation.

Retraining is not part of Phase 2.8.

---

# 14. Phase 2 Deliverable

At the end of Phase 2, MotorGuard has a functional virtual factory simulation capable of:

- Loading the prepared bearing dataset.
- Sampling all supported bearing conditions.
- Creating multiple virtual motors.
- Managing motor operating states.
- Switching between fault scenarios.
- Generating vibration feature readings.
- Generating synthetic temperature, current and RPM.
- Running multiple motors through a factory engine.
- Generating periodic readings.
- Handling individual motor generation errors.
- Serializing telemetry to JSON.
- Validating telemetry against a contract.
- Checking compatibility with an existing fitted model.
- Performing inference without retraining.

---

# 15. Phase 2 Completion Criteria

Phase 2 is considered complete when:

- [x] Simulation configuration is implemented.
- [x] Dataset provider is implemented.
- [x] Virtual motor simulation is implemented.
- [x] Additional sensor simulation is implemented.
- [x] Fault scenarios are implemented.
- [x] Factory engine is implemented.
- [x] Multiple motors can operate independently.
- [x] Tests for subphases 2.4, 2.5 and 2.6 pass.
- [x] Integration and telemetry validation is implemented.
- [x] Telemetry JSON serialization is implemented.
- [x] JSON Schema validation is implemented.
- [x] Model compatibility validation is implemented.
- [x] Inference validation tests pass.
- [x] Phase 2 tests pass, as confirmed by the user.

---

# 16. Handoff Context for Phase 3

Phase 2 provides the simulation layer for the next development phase.

The next phase should build on the existing simulator rather than recreate its functionality.

The factory can now serve as a source of motor readings.

A generated reading can be passed to a future integration layer:

```text
FactoryEngine
     │
     ▼
Validated Telemetry
     │
     ▼
Communication Layer
     │
     ├── MQTT
     │
     ├── Backend API
     │
     └── Other Consumers
```

The communication layer should consume the telemetry contract rather than depend on internal motor or factory implementation details.

Future integration should preserve:

- Motor identifiers.
- Factory identifiers.
- Production-line identifiers.
- Timestamp.
- Motor state.
- Bearing condition.
- Vibration features.
- Ground truth.
- Sensor values.
- Simulation metadata.
- Telemetry schema version.

---

# 17. Context for the Next Development Session

When continuing MotorGuard, use the following context:

Phase 1 contains the dataset preparation and existing ML work.

Phase 2 is the virtual factory simulation and is completed, with tests reported as passing.

The simulator is located in:

```text
simulator/
```

The dataset is located in:

```text
data/feature_time_48k_2048_load1.csv
```

The simulator samples vibration features from the prepared CWRU dataset and generates additional synthetic sensor measurements.

The simulator currently supports:

- Ten bearing conditions.
- Four motor states.
- Random and sequential sampling modes.
- Multiple independent motors.
- Scenario switching.
- A factory simulation engine.
- Versioned telemetry.
- JSON serialization and validation.
- Existing-model compatibility validation.

Do not rebuild the Phase 2 components unless a concrete problem requires it.

Before making changes to existing files:

1. Inspect the current implementation.
2. Identify the actual requirement.
3. Preserve working architecture.
4. Avoid unnecessary rewrites.
5. If modifications are needed, provide complete updated files when requested.
6. Specify exact file paths.
7. Explain what the change accomplishes.
8. Provide commands to test the change.

The next phase should focus on integrating the virtual factory with the next layer of the MotorGuard system while preserving the telemetry contract.

---

# PHASE 2 — FINAL STATUS

```text
MOTORGARD
│
├── PHASE 1
│   └── Dataset preparation and Machine Learning
│
└── PHASE 2
    └── Virtual Factory Simulation
        │
        ├── 2.1 Simulation Foundation & Configuration
        ├── 2.2 Dataset Provider
        ├── 2.3 Virtual Motor Simulation
        ├── 2.4 Synthetic Sensor Simulation
        ├── 2.5 Fault Scenarios
        ├── 2.6 Factory Simulation Engine
        ├── 2.7 Integration & Telemetry Validation
        └── 2.8 Model Compatibility & Inference Validation

STATUS: COMPLETED
```

The virtual factory simulation is now established as a reusable component of MotorGuard.

Future phases should build on this foundation rather than duplicate it.