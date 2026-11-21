
from pathlib import Path

import joblib
import pandas as pd
import math
import joblib
import pandas as pd

from simulator.config import FEATURE_COLUMNS


class ModelCompatibilityError(ValueError):
    pass


def load_model(model_path: str | Path):
    """Load an existing fitted model or fitted sklearn pipeline."""

    model_path = Path(model_path)

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    model = joblib.load(model_path)

    if not hasattr(model, "predict"):
        raise ModelCompatibilityError(
            "Loaded model does not expose predict()"
        )

    return model


def load_preprocessor(preprocessor_path: str | Path | None):
    """Load an optional existing fitted preprocessing artifact."""

    if preprocessor_path is None:
        return None

    preprocessor_path = Path(preprocessor_path)

    if not preprocessor_path.exists():
        raise FileNotFoundError(
            f"Preprocessor not found: {preprocessor_path}"
        )

    preprocessor = joblib.load(preprocessor_path)

    if not hasattr(preprocessor, "transform"):
        raise ModelCompatibilityError(
            "Preprocessor must expose transform(). "
            "Do not use an unfitted preprocessing object."
        )

    return preprocessor


def validate_feature_contract(features: dict) -> pd.DataFrame:
    """Validate and arrange features in the model's exact input order."""

    if not isinstance(features, dict):
        raise ModelCompatibilityError(
            "Features must be supplied as a dictionary"
        )

    if list(features.keys()) != FEATURE_COLUMNS:
        raise ModelCompatibilityError(
            "Feature order mismatch.\n"
            f"Expected: {FEATURE_COLUMNS}\n"
            f"Received: {list(features.keys())}"
        )

    for name in FEATURE_COLUMNS:
        value = features[name]

        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ModelCompatibilityError(
                f"Feature {name} must be numeric"
            )

        if not math.isfinite(value):
            raise ModelCompatibilityError(
                f"Feature {name} must be finite "
            )

    frame = pd.DataFrame(
        [[features[name] for name in FEATURE_COLUMNS]],
        columns=FEATURE_COLUMNS,
    )

    return frame



def validate_model_input(
    model,
    frame: pd.DataFrame,
    compare_feature_names: bool = True,
) -> None:
    """Validate input size and, when applicable, feature names."""

    if compare_feature_names and hasattr(model, "feature_names_in_"):
        model_features = list(model.feature_names_in_)

        if model_features != FEATURE_COLUMNS:
            raise ModelCompatibilityError(
                "Saved model feature contract does not match simulator.\n"
                f"Model: {model_features}\n"
                f"Simulator: {FEATURE_COLUMNS}"
            )

    if hasattr(model, "n_features_in_"):
        if model.n_features_in_ != frame.shape[1]:
            raise ModelCompatibilityError(
                f"Model expects {model.n_features_in_} features, "
                f"but received {frame.shape[1]}"
            )


def predict_sample(
    features: dict,
    model,
    preprocessor=None,
):
    """Predict using an existing fitted model and optional fitted preprocessor."""

    raw_frame = validate_feature_contract(features)

    # Validate the raw simulator contract against the model only when
    # no separate preprocessing artifact is used.
    if preprocessor is None:
        validate_model_input(
            model,
            raw_frame,
            compare_feature_names=True,
        )
        model_input = raw_frame
    else:
        model_input = preprocessor.transform(raw_frame)

        validate_model_input(
            model,
            model_input,
            compare_feature_names=False,
        )

    prediction = model.predict(model_input)

    return prediction[0]



