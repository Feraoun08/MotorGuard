from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "model.pkl"

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


def test_real_model_artifact():
    assert MODEL_PATH.exists(), f"Model not found: {MODEL_PATH}"

    model = joblib.load(MODEL_PATH)

    # Verify model capabilities
    assert hasattr(model, "predict")
    assert hasattr(model, "predict_proba")
    assert hasattr(model, "classes_")

    # One sample containing the nine features in the training order
    sample = pd.DataFrame(
        [[
            1.0,
            -1.0,
            0.2,
            0.5,
            0.6,
            0.1,
            2.5,
            1.8,
            1.2,
        ]],
        columns=FEATURE_NAMES,
    )

    # Prediction
    prediction = model.predict(sample)

    # Probability distribution
    probabilities = model.predict_proba(sample)

    assert prediction.shape == (1,)
    assert probabilities.shape == (1, len(model.classes_))
    assert abs(probabilities[0].sum() - 1.0) < 1e-6

    predicted_class = prediction[0]

    # Map the probability to the predicted class correctly
    class_index = list(model.classes_).index(predicted_class)
    confidence = probabilities[0][class_index]

    print("\n========== REAL MODEL ARTIFACT TEST ==========")
    print(f"Model path       : {MODEL_PATH}")
    print(f"Predicted class  : {predicted_class}")
    print(f"Confidence       : {confidence:.4f}")
    print(f"Model classes    : {list(model.classes_)}")
    print(f"Input shape      : {sample.shape}")
    print("Test             : PASSED")
    print("===========================================\n")


if __name__ == "__main__":
    test_real_model_artifact()