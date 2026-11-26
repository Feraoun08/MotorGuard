

# PHASE 06 — ML INFERENCE INTEGRATION CONTEXT

## Project

**MotorGuard IoT** is an industrial predictive-maintenance platform designed to monitor motors, collect telemetry, and detect bearing conditions using machine learning.

Phase 06 integrates the trained ML model from Phase 01 into the existing backend API, allowing the system to diagnose a motor using its latest telemetry.

---

# 1. Project Progress

The previous phases have been completed:

- **Phase 01:** Dataset preparation, feature engineering, model training, evaluation, and model artifact export.
- **Phase 02:** Motor simulation, sensor generation, motor states, scenarios, and telemetry generation.
- **Phase 03:** MQTT integration and message publishing.
- **Phase 04:** MQTT ingestion pipeline, subscriber, validation, and telemetry processing.
- **Phase 05:** REST API, database integration, factories, motors, telemetry, and maintenance.
- **Phase 06:** ML inference integration into the backend API.

Phase 06 has been implemented and validated.

---

# 2. Phase 06 Objective

The objective was to integrate the previously trained machine-learning model into the existing backend without modifying the completed MQTT ingestion or simulation architecture.

The backend must be capable of:

1. Loading the trained model when the API starts.
2. Loading the model only once rather than on every diagnosis request.
3. Retrieving the latest telemetry for a specific motor.
4. Extracting the required ML features in the exact training order.
5. Running inference using the Random Forest classifier.
6. Returning the predicted bearing condition.
7. Returning the prediction confidence when supported by the model.
8. Preserving telemetry metadata, including ground truth.
9. Handling missing motors, missing telemetry, and invalid feature data.
10. Exposing diagnosis through a REST endpoint.

---

# 3. Existing ML Model

The model was trained during Phase 01 using the CWRU bearing dataset.

## Dataset

- Dataset: CWRU bearing dataset
- Sampling frequency: 48 kHz
- Window size: 2048 samples
- Dataset file: `feature_time_48k_2048_load_1.csv`

## Selected model

Random Forest Classifier.

Training parameters:

- `n_estimators = 200`
- `max_depth = None`
- `max_features = "sqrt"`
- `min_samples_leaf = 2`
- `random_state = 42`

No feature scaling was required for the selected Random Forest model.

## Model evaluation

The model was selected during Phase 01 after evaluating multiple classifiers.

The cross-validation macro F1 score was approximately:

`0.96945`

The trained model and its preprocessing configuration were exported as artifacts.

## Model artifact

```text
models/
├── model.pkl
└── preprocessing_config.json
```

The model is loaded using `joblib`.

The artifact contains the trained classifier, including its learned classes and prediction capabilities.

---

# 4. ML Feature Contract

The inference pipeline must use exactly nine vibration features.

Their order is critical because the model was trained using this feature order.

```python
FEATURE_NAMES = [
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

## Feature definitions

| Feature | Description |
|---|---|
| max | Maximum vibration value |
| min | Minimum vibration value |
| mean | Mean vibration value |
| sd | Standard deviation |
| rms | Root mean square |
| skewness | Distribution asymmetry |
| kurtosis | Distribution tail/peak characteristics |
| crest | Crest factor |
| form | Form factor |

The feature extraction process reads these values from the latest telemetry's vibration section.

The order must never be changed unless the model is retrained using the corresponding new feature order.

Temperature, current, RPM, ground truth, motor IDs, timestamps, and other telemetry metadata are not model inputs for this Phase 06 model.

---

# 5. Phase 06 Architecture

The ML integration was added to the existing backend without replacing the previous architecture.

The inference pipeline is:

```text
                    REST API REQUEST
                           |
                           v
              Diagnosis API Endpoint
                           |
                           v
                 DiagnosisService
                           |
               +-----------+-----------+
               |                       |
               v                       v
      TelemetryService           ModelLoader
               |                       |
               v                       v
        InfluxDB Latest         Random Forest
          Telemetry                 Model
               |                       |
               v                       v
       Feature Extraction        Prediction
               |                       |
               +-----------+-----------+
                           |
                           v
                Diagnosis Response
                           |
                           v
                     HTTP 200
```

## Pipeline

1. The client requests a motor diagnosis.
2. The API validates the factory and motor context through the existing telemetry service.
3. The latest telemetry is retrieved from InfluxDB.
4. The nine vibration features are extracted.
5. The feature values are validated and converted to numerical values.
6. The trained Random Forest model receives the feature vector.
7. The model predicts the bearing condition.
8. The prediction confidence is extracted from the probability distribution.
9. The response is serialized using the diagnosis schema.

---

# 6. New ML Components

The following components were added.

## `backend/ml/__init__.py`

Package initialization for the ML module.

## `backend/ml/model_loader.py`

Responsible for loading and exposing the trained ML model.

Main responsibilities:

- Loading the model using `joblib`.
- Providing the loaded model to the inference service.
- Preventing access to the model before it has been loaded.
- Avoiding unnecessary model reloads during API requests.

The model is loaded during API startup and reused by subsequent diagnosis requests.

## `backend/ml/feature_extractor.py`

Responsible for extracting and validating the model input from telemetry.

Main responsibilities:

- Extracting the nine required vibration features.
- Preserving the exact feature order.
- Checking for missing features.
- Rejecting null values.
- Converting values into numerical values.
- Rejecting non-numeric values.
- Rejecting NaN and infinite values.
- Returning a valid ordered feature vector.

A `FeatureExtractionError` exception is used when feature extraction or validation fails.

---

# 7. Diagnosis Service

File:

```text
backend/api/services/diagnosis_service.py
```

The diagnosis service is responsible for the inference business logic.

It integrates:

- Existing `TelemetryService`
- Existing InfluxDB telemetry storage
- `ModelLoader`
- `FeatureExtractor`
- Diagnosis response schema

## Main workflow

```text
diagnose(factory_id, motor_id)
        |
        v
Retrieve latest motor telemetry
        |
        v
Validate telemetry availability
        |
        v
Extract 9 vibration features
        |
        v
Load already-initialized model
        |
        v
model.predict()
        |
        v
model.predict_proba()
        |
        v
Extract prediction confidence
        |
        v
Build DiagnosisResponse
```

## Prediction

The classifier is called using:

```python
model.predict(features)
```

## Confidence

When the model supports `predict_proba()`, the probability distribution is used to determine the confidence corresponding to the predicted class.

The probability must be mapped using the model's `classes_` attribute rather than assuming that the predicted class position is always fixed.

Conceptually:

```python
predicted_class = model.predict(features)[0]

probabilities = model.predict_proba(features)[0]

class_index = list(model.classes_).index(predicted_class)

confidence = probabilities[class_index]
```

Confidence is returned as a numerical value between 0 and 1.

A confidence of `1.0` means the model assigned 100% probability to the predicted class for that particular input. It does not guarantee that the prediction is objectively correct.

---

# 8. Diagnosis API

New router:

```text
backend/api/routers/diagnosis.py
```

The router exposes diagnosis functionality using the existing factory and motor API structure.

## Endpoint

```http
GET /api/factories/{factory_id}/motors/{motor_id}/diagnosis
```

Example:

```http
GET /api/factories/FACTORY_01/motors/MOTOR_001/diagnosis
```

## Endpoint responsibilities

- Identify the factory.
- Identify the motor.
- Retrieve the latest telemetry.
- Execute the inference service.
- Return the diagnosis.
- Handle expected errors.
- Serialize the response using `DiagnosisResponse`.

## HTTP behavior

| Status | Meaning |
|---|---|
| 200 | Diagnosis successfully generated |
| 404 | Factory, motor, or telemetry not found |
| 422 | Invalid or unusable ML feature data |

The diagnosis endpoint is on-demand.

It does not introduce a new MQTT consumer, worker, scheduler, inference queue, or database table.

---

# 9. Diagnosis Response Schema

New schema:

```text
backend/api/schemas/diagnosis.py
```

Schema:

```python
DiagnosisResponse
```

The response contains:

| Field | Description |
|---|---|
| factory_id | Factory identifier |
| line_id | Production line identifier |
| motor_id | Motor identifier |
| timestamp | Timestamp of the telemetry used for inference |
| predicted_class | Predicted bearing condition |
| confidence | Prediction probability of the predicted class |
| ground_truth | Ground truth metadata, when available |
| is_simulated | Indicates whether the telemetry is simulated, when available |

The timestamp represents the telemetry used for the prediction, not the API request time.

`ground_truth` remains separate from the model prediction and is never used as an ML feature.

---

# 10. API Integration

The diagnosis router is integrated into the existing FastAPI application.

The existing router architecture remains intact.

The diagnosis router was added to:

```text
backend/api/routers/__init__.py
```

The diagnosis response schema was added to:

```text
backend/api/schemas/__init__.py
```

The diagnosis endpoint uses the existing database dependency and application-level InfluxDB/model dependencies.

## Model initialization

The model is loaded during FastAPI startup.

The application initializes the `ModelLoader`, loads the artifact from:

```text
models/model.pkl
```

and stores the loaded model loader in application state for reuse.

The diagnosis request does not reload the model.

---

# 11. Files Added or Modified

## New ML package

```text
backend/ml/
├── __init__.py
├── model_loader.py
└── feature_extractor.py
```

## New diagnosis schema

```text
backend/api/schemas/
└── diagnosis.py
```

## New diagnosis service

```text
backend/api/services/
└── diagnosis_service.py
```

## New diagnosis router

```text
backend/api/routers/
└── diagnosis.py
```

## Modified integration files

```text
backend/api/app.py
backend/api/routers/__init__.py
backend/api/schemas/__init__.py
requirements.txt
```

The existing Phase 04 ingestion and MQTT components were not modified for inference.

---

# 12. Validation and Testing

Phase 06 validation was performed through component tests and real model artifact execution.

## Feature extraction validation

Tests cover:

- Correct feature extraction.
- Correct feature ordering.
- Missing vibration features.
- Null values.
- Invalid numerical values.
- Non-finite values.

## Diagnosis service validation

Tests cover:

- Successful diagnosis.
- Telemetry retrieval.
- Prediction generation.
- Confidence extraction.
- Ground truth preservation.
- Missing telemetry.
- Invalid feature data.

## API router validation

Tests cover:

- Successful diagnosis response.
- HTTP 200.
- Motor/factory lookup failures.
- Missing telemetry.
- Invalid feature data.
- HTTP 404 behavior.
- HTTP 422 behavior.

## Real model artifact validation

File:

```text
backend/tests/test_real_model_artifact.py
```

This test loads the actual model artifact from:

```text
models/model.pkl
```

It validates:

- Model artifact existence.
- Successful model loading.
- `predict()` availability.
- `predict_proba()` availability.
- `classes_` availability.
- Correct input shape.
- Successful prediction.
- Probability output shape.
- Probability sum approximately equal to 1.
- Confidence extraction corresponding to the predicted class.

The model receives one sample containing nine features:

```text
Input shape: (1, 9)
```

The standalone test successfully passed.

### Latest test output

```text
========== REAL MODEL ARTIFACT TEST ==========

Model path       : C:\Users\User\Desktop\Motor\models\model.pkl
Predicted class  : IR_014_1
Confidence       : 0.6150

Model classes    :
[
    'Ball_007_1',
    'Ball_014_1',
    'Ball_021_1',
    'IR_007_1',
    'IR_014_1',
    'IR_021_1',
    'Normal_1',
    'OR_007_6_1',
    'OR_014_6_1',
    'OR_021_6_1'
]

Input shape      : (1, 9)
Test             : PASSED
```

This confirms that the actual model artifact can be loaded and used to produce a prediction and probability distribution.

---

# 13. Real API Validation

The diagnosis endpoint was also tested using the running backend.

## Request

```http
GET http://127.0.0.1:8000/api/factories/FACTORY_01/motors/MOTOR_001/diagnosis
```

## HTTP status

```text
200 OK
```

## Actual response

```json
{
  "factory_id": "FACTORY_01",
  "line_id": "LINE_01",
  "motor_id": "MOTOR_001",
  "timestamp": "2026-11-23T19:53:54.753876Z",
  "predicted_class": "Normal_1",
  "confidence": 1,
  "ground_truth": "Normal_1",
  "is_simulated": true
}
```

## Validation results

| Component | Status |
|---|---|
| FastAPI diagnosis route | PASS |
| Factory and motor context | PASS |
| Latest telemetry retrieval | PASS |
| InfluxDB integration | PASS |
| Feature extraction | PASS |
| Feature ordering | PASS |
| Model loading | PASS |
| Model prediction | PASS |
| Confidence extraction | PASS |
| Ground truth preservation | PASS |
| Response serialization | PASS |
| HTTP 200 | PASS |

The endpoint was validated against real application infrastructure, not only mocked service tests.

---

# 14. Known Issue — scikit-learn Version Mismatch

During model loading, the following warnings were observed:

```text
InconsistentVersionWarning:

Trying to unpickle estimator DecisionTreeClassifier
from version 1.9.1 when using version 1.7.2
```

And:

```text
Trying to unpickle estimator RandomForestClassifier
from version 1.9.1 when using version 1.7.2
```

## Versions

Model artifact version:

```text
scikit-learn 1.9.1
```

Current runtime version:

```text
scikit-learn 1.7.2
```

## Impact

The model artifact successfully loaded and executed predictions.

However, loading scikit-learn artifacts with a different version than the version used to train and serialize them is not guaranteed to be compatible.

The warnings remain unresolved.

## Recommended action

Align the backend environment with the model's training environment:

```bash
python -m pip install scikit-learn==1.9.1
```

Verify:

```bash
python -c "import sklearn; print(sklearn.__version__)"
```

Expected:

```text
1.9.1
```

The Python environment used to run MotorGuard must be the same environment where the dependency is installed.

This version alignment is a known pending maintenance task, even though inference has already been successfully validated.

---

# 15. Important ML Limitations

Phase 06 implements inference integration, not a complete industrial predictive-maintenance system.

## Classification only

The current model classifies bearing conditions.

It does not currently estimate:

- Remaining Useful Life (RUL).
- Time until failure.
- Failure probability over a future time window.
- Maintenance dates.
- Degradation trajectory.

## Statistical vibration features

The model operates on statistical vibration features rather than raw signal windows.

It uses the nine vibration statistics defined during Phase 01.

## Dataset limitations

The model was trained using the CWRU dataset.

The available dataset and validation strategy do not establish that the model will generalize to every industrial motor, sensor, mounting configuration, operating speed, load, or factory environment.

## Simulated telemetry

The current successful API test used simulated telemetry.

This validates the complete software inference pipeline but does not establish industrial predictive performance.

## Ground truth

Ground truth is returned as telemetry metadata for comparison and evaluation.

It must never be included in the model's input features because doing so would cause target leakage.

---

# 16. Phase 06 Constraints

The following constraints must be respected during future development.

1. Do not retrain or replace the Phase 01 model without explicitly planning a new model-training phase.
2. Do not change the nine-feature contract without considering model compatibility.
3. Preserve the feature order.
4. Do not include `ground_truth` in model features.
5. Do not reload the model for every request.
6. Do not modify the completed Phase 04 MQTT ingestion pipeline without a clearly justified requirement.
7. Do not introduce unnecessary inference queues, workers, schedulers, or databases.
8. Keep diagnosis logic in the service layer.
9. Keep the API router responsible for HTTP behavior.
10. Keep inference errors explicit and controlled.
11. Do not interpret confidence as guaranteed prediction correctness.
12. Do not interpret simulated telemetry validation as proof of real industrial performance.

---

# 17. How to Run the Backend

## Start the API

From the project root:

```bash
python -m backend.api_main
```

The API should initialize its dependencies and load the model during startup.

## Swagger

```text
http://127.0.0.1:8000/docs
```

## Diagnosis endpoint

```http
GET /api/factories/{factory_id}/motors/{motor_id}/diagnosis
```

Example:

```text
http://127.0.0.1:8000/api/factories/FACTORY_01/motors/MOTOR_001/diagnosis
```

## Run the real model artifact test

```bash
python backend/tests/test_real_model_artifact.py
```

## Run the backend test suite

```bash
pytest backend/tests -v
```

---

# 18. Current Project State

At the completion of Phase 06, MotorGuard contains:

- Factory and motor management.
- Telemetry ingestion.
- MQTT integration.
- Telemetry validation.
- PostgreSQL persistence.
- InfluxDB telemetry storage.
- REST API.
- Maintenance management.
- Motor simulation.
- ML model artifact integration.
- On-demand motor diagnosis.
- Bearing-condition prediction.
- Prediction confidence.
- Ground truth separation.
- Error handling for unavailable telemetry and invalid features.

The diagnosis pipeline is operational.

The remaining known technical issue is scikit-learn version alignment between the serialized model and the backend runtime.

---

# 19. Phase 06 Completion

Phase 06 is considered implemented and functionally validated.

The following have been confirmed:

- Model artifact loads.
- Feature extraction works.
- Model receives correctly structured input.
- Model prediction works.
- Probability prediction works.
- Confidence extraction works.
- Diagnosis service works.
- Diagnosis endpoint works.
- Actual API returns HTTP 200.
- Actual diagnosis JSON response is valid.
- Standalone real model artifact test passes.

The scikit-learn version mismatch remains documented as a pending compatibility improvement.

---

# 20. Context for the Next Phase

The next phase must build on the completed MotorGuard architecture.

Do not recreate:

- The ML model.
- Model training.
- Model loading.
- Feature extraction.
- Diagnosis service.
- Diagnosis endpoint.
- MQTT ingestion.
- Telemetry storage.
- Factory/motor API.

These already exist.

The next phase should begin by defining its objective, scope, architecture, and implementation steps before modifying the code.

The current diagnosis endpoint can be reused as the foundation for future functionality involving:

- Monitoring.
- Fault detection workflows.
- Diagnosis history.
- Alerts.
- Maintenance decision support.
- Operational dashboards.
- Further model evaluation.
- Real-world deployment validation.

Any future extension must respect the separation between telemetry, model inference, API, and maintenance logic.

---

# END OF PHASE 06 CONTEXT
