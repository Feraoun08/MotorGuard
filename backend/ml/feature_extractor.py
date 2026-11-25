import math
from typing import Any


class FeatureExtractionError(ValueError):
    """
    Raised when telemetry cannot be converted into a valid ML input.
    """
    pass


class FeatureExtractor:
    """
    Extracts and validates model features from motor telemetry.

    The feature order must remain identical to the training order.
    """

    FEATURE_NAMES = (
        "max",
        "min",
        "mean",
        "sd",
        "rms",
        "skewness",
        "kurtosis",
        "crest",
        "form",
    )

    @classmethod
    def extract(cls, telemetry: dict[str, Any]) -> list[float]:
        """
        Extract a validated feature vector from telemetry.

        Parameters
        ----------
        telemetry:
            API telemetry response.

        Returns
        -------
        list[float]
            Features ordered exactly as required by the ML model.
        """

        vibration = telemetry.get("vibration")

        if not isinstance(vibration, dict):
            raise FeatureExtractionError(
                "Telemetry vibration data is missing"
            )

        features = []

        for feature_name in cls.FEATURE_NAMES:

            if feature_name not in vibration:
                raise FeatureExtractionError(
                    f"Missing required feature: {feature_name}"
                )

            value = vibration[feature_name]

            if value is None:
                raise FeatureExtractionError(
                    f"Feature '{feature_name}' is null"
                )

            try:
                numeric_value = float(value)

            except (TypeError, ValueError):
                raise FeatureExtractionError(
                    f"Feature '{feature_name}' is not numeric"
                )

            if not math.isfinite(numeric_value):
                raise FeatureExtractionError(
                    f"Feature '{feature_name}' is not finite"
                )

            features.append(numeric_value)

        if len(features) != len(cls.FEATURE_NAMES):
            raise FeatureExtractionError(
                "Invalid feature vector length"
            )

        return features