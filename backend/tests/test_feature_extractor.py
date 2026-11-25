import pytest

from backend.ml.feature_extractor import (
    FeatureExtractor,
    FeatureExtractionError,
)


@pytest.fixture
def valid_telemetry():
    return {
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
        "ground_truth": "Normal_1",
    }


def test_feature_order(valid_telemetry):

    features = FeatureExtractor.extract(
        valid_telemetry
    )

    assert features == [
        1.0,
        -1.0,
        0.2,
        0.5,
        0.6,
        0.1,
        2.5,
        1.8,
        1.2,
    ]


def test_feature_count(valid_telemetry):

    features = FeatureExtractor.extract(
        valid_telemetry
    )

    assert len(features) == 9


def test_ground_truth_is_not_used(valid_telemetry):

    first = FeatureExtractor.extract(
        valid_telemetry
    )

    valid_telemetry["ground_truth"] = "IR_007_1"

    second = FeatureExtractor.extract(
        valid_telemetry
    )

    assert first == second


def test_missing_vibration():

    with pytest.raises(FeatureExtractionError):

        FeatureExtractor.extract({})


def test_missing_feature(valid_telemetry):

    del valid_telemetry["vibration"]["rms"]

    with pytest.raises(
        FeatureExtractionError,
        match="Missing required feature",
    ):

        FeatureExtractor.extract(
            valid_telemetry
        )


def test_none_feature(valid_telemetry):

    valid_telemetry["vibration"]["rms"] = None

    with pytest.raises(
        FeatureExtractionError,
        match="is null",
    ):

        FeatureExtractor.extract(
            valid_telemetry
        )


def test_non_numeric_feature(valid_telemetry):

    valid_telemetry["vibration"]["rms"] = "invalid"

    with pytest.raises(
        FeatureExtractionError,
        match="is not numeric",
    ):

        FeatureExtractor.extract(
            valid_telemetry
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_non_finite_feature(
    valid_telemetry,
    invalid_value,
):

    valid_telemetry["vibration"]["rms"] = invalid_value

    with pytest.raises(
        FeatureExtractionError,
        match="is not finite",
    ):

        FeatureExtractor.extract(
            valid_telemetry
        )