
import argparse
import json

from simulator.config import BEARING_CONDITIONS
from simulator.dataset_provider import DatasetProvider
from simulator.model_compatibility import (
    load_model,
    load_preprocessor,
    predict_sample,
)


def run_validation(model_path, preprocessor_path=None):
    provider = DatasetProvider(random_seed=42)

    model = load_model(model_path)
    preprocessor = load_preprocessor(preprocessor_path)

    test_conditions = [
        "Normal_1",
        "Ball_007_1",
        "IR_014_1",
    ]

    for condition in test_conditions:
        if condition not in BEARING_CONDITIONS:
            raise ValueError(
                f"Condition not available in simulator dataset: {condition}"
            )

    results = []

    print("\n" + "=" * 65)
    print("MOTORGARD - MODEL COMPATIBILITY VALIDATION")
    print("=" * 65)

    for condition in test_conditions:
        measurement = provider.sample(condition)

        prediction = predict_sample(
            features=measurement.features,
            model=model,
            preprocessor=preprocessor,
        )

        result = {
            "ground_truth": measurement.ground_truth,
            "prediction": str(prediction),
            "correct": str(prediction) == str(measurement.ground_truth),
        }

        results.append(result)

        print(f"\nCondition: {condition}")
        print(f"Ground truth: {result['ground_truth']}")
        print(f"Prediction:   {result['prediction']}")
        print(f"Correct:      {result['correct']}")

    correct_count = sum(result["correct"] for result in results)

    print("\n" + "-" * 65)
    print(f"Samples tested: {len(results)}")
    print(f"Correct:        {correct_count}")
    print(f"Demonstration accuracy: {correct_count / len(results):.2%}")
    print("-" * 65)

    print("\nJSON results:")
    print(json.dumps(results, indent=4))

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Validate MotorGuard simulator compatibility with a saved model"
    )

    parser.add_argument(
        "--model",
        required=True,
        help="Path to the existing fitted model or pipeline",
    )

    parser.add_argument(
        "--preprocessor",
        default=None,
        help="Optional path to the existing fitted preprocessing artifact",
    )

    args = parser.parse_args()

    run_validation(
        model_path=args.model,
        preprocessor_path=args.preprocessor,
    )


if __name__ == "__main__":
    main()
