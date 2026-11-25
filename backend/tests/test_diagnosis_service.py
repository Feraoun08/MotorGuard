from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from backend.api.services.diagnosis_service import DiagnosisService
from backend.ml.feature_extractor import FeatureExtractionError


@pytest.fixture
def telemetry():
    return {
        "factory_id": "factory-01",
        "line_id": "line-01",
        "motor_id": "motor-01",
        "timestamp": "2026-11-25T18:30:00+00:00",
        "ground_truth": "Normal_1",
        "is_simulated": True,
        "vibration": {
            "max": 1.0,
            "min": -1.0,
            "mean": 0.2,
            "sd": 0.5,
            "rms": 0.6,
            "skewness": 0.1,
            "kurtosis": 2.5,
            "crest": 1.8,
            "form": 1.2,
        },
    }


@pytest.fixture
def fake_model():
    model = MagicMock()

    model.classes_ = np.array(
        [
            "Ball_007_1",
            "Normal_1",
            "IR_007_1",
        ]
    )

    model.predict.return_value = np.array(
        ["IR_007_1"]
    )

    model.predict_proba.return_value = np.array(
        [[0.10, 0.20, 0.70]]
    )

    return model


def create_service(fake_model, telemetry):

    model_loader = MagicMock()

    model_loader.get_model.return_value = fake_model

    with patch(
        "backend.api.services.diagnosis_service.TelemetryService"
    ) as telemetry_service_class:

        telemetry_service_class.return_value.get_latest.return_value = telemetry

        service = DiagnosisService(
            session=MagicMock(),
            influx_store=MagicMock(),
            model_loader=model_loader,
        )

    # Keep the mock telemetry service accessible
    service.telemetry_service = (
        telemetry_service_class.return_value
    )

    return service


def test_diagnosis_success(
    fake_model,
    telemetry,
):

    service = create_service(
        fake_model,
        telemetry,
    )

    result = service.diagnose(
        "factory-01",
        "motor-01",
    )

    assert result["predicted_class"] == "IR_007_1"

    assert result["confidence"] == pytest.approx(0.70)

    assert result["factory_id"] == "factory-01"

    assert result["motor_id"] == "motor-01"

    assert result["ground_truth"] == "Normal_1"

    fake_model.predict.assert_called_once()

    fake_model.predict_proba.assert_called_once()


def test_diagnosis_does_not_replace_ground_truth(
    fake_model,
    telemetry,
):

    service = create_service(
        fake_model,
        telemetry,
    )

    result = service.diagnose(
        "factory-01",
        "motor-01",
    )

    assert result["predicted_class"] == "IR_007_1"

    assert result["ground_truth"] == "Normal_1"


def test_missing_telemetry(
    fake_model,
):

    service = create_service(
        fake_model,
        None,
    )

    with pytest.raises(
        LookupError,
        match="No telemetry",
    ):

        service.diagnose(
            "factory-01",
            "motor-01",
        )


def test_invalid_feature(
    fake_model,
    telemetry,
):

    telemetry["vibration"]["rms"] = float("nan")

    service = create_service(
        fake_model,
        telemetry,
    )

    with pytest.raises(
        FeatureExtractionError,
    match="not finite",
    ):

        service.diagnose(
            "factory-01",
            "motor-01",
        )