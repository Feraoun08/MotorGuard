
import pytest

from simulator.config import FEATURE_COLUMNS
from simulator.model_compatibility import (
    ModelCompatibilityError,
    predict_sample,
    validate_feature_contract,
)


class FakeModel:
    feature_names_in_ = FEATURE_COLUMNS
    n_features_in_ = 9

    def predict(self, frame):
        return ["Normal_1"]


@pytest.fixture
def valid_features():
    return {
        "max": 0.42,
        "min": -0.39,
        "mean": 0.01,
        "sd": 0.12,
        "rms": 0.15,
        "skewness": 0.08,
        "kurtosis": 3.1,
        "crest": 2.8,
        "form": 1.2,
    }


def test_feature_contract_valid(valid_features):
    frame = validate_feature_contract(valid_features)

    assert list(frame.columns) == FEATURE_COLUMNS
    assert frame.shape == (1, 9)


def test_feature_contract_wrong_order(valid_features):
    invalid_features = dict(
        reversed(list(valid_features.items()))
    )

    with pytest.raises(ModelCompatibilityError):
        validate_feature_contract(invalid_features)


def test_feature_contract_missing_feature(valid_features):
    del valid_features["rms"]

    with pytest.raises(ModelCompatibilityError):
        validate_feature_contract(valid_features)


def test_model_prediction(valid_features):
    model = FakeModel()

    prediction = predict_sample(
        features=valid_features,
        model=model,
    )

    assert prediction == "Normal_1"


def test_model_input_dimension_mismatch(valid_features):
    class WrongModel:
        n_features_in_ = 5

        def predict(self, frame):
            return ["Normal_1"]

    with pytest.raises(ModelCompatibilityError):
        predict_sample(
            features=valid_features,
            model=WrongModel(),
        )


def test_nan_feature_rejected(valid_features):
    valid_features["rms"] = float("nan")

    with pytest.raises(ModelCompatibilityError):
        validate_feature_contract(valid_features)


def test_infinite_feature_rejected(valid_features):
    valid_features["rms"] = float("inf")

    with pytest.raises(ModelCompatibilityError):
        validate_feature_contract(valid_features)
