
import random
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from simulator.config import (
    BEARING_CONDITIONS,
    DATASET_PATH,
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    SamplingMode,
)
from simulator.motor import VibrationMeasurement


class DatasetProvider:
    """
    Loads prepared vibration features and provides observations
    for virtual motors.

    Ground truth is retained separately from model input.
    """

    def __init__(
        self,
        dataset_path: Path = DATASET_PATH,
        random_seed: int | None = None,
    ):
        self.dataset_path = Path(dataset_path)

        self.random_generator = random.Random(random_seed)

        self.dataset = None
        self.samples_by_condition = {}

        # Sequential sampling cursors
        self.cursors = defaultdict(int)

        self._load_dataset()

    def _load_dataset(self):
        """Load and validate the prepared CSV."""

        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {self.dataset_path}"
            )

        self.dataset = pd.read_csv(self.dataset_path)

        required_columns = FEATURE_COLUMNS + [TARGET_COLUMN]

        missing_columns = [
            column
            for column in required_columns
            if column not in self.dataset.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Dataset is missing columns: {missing_columns}"
            )

        # Keep only required features and target.
        self.dataset = self.dataset[required_columns].copy()

        # Validate numerical feature columns.
        for column in FEATURE_COLUMNS:
            self.dataset[column] = pd.to_numeric(
                self.dataset[column],
                errors="coerce"
            )

        # Reject missing or infinite feature values.
        features_array = self.dataset[FEATURE_COLUMNS].to_numpy(
            dtype=float
        )

        if not np.isfinite(features_array).all():
            raise ValueError(
                "Dataset contains missing or infinite feature values."
            )

        # Normalize label representation.
        self.dataset[TARGET_COLUMN] = (
            self.dataset[TARGET_COLUMN].astype(str).str.strip()
        )

        if (self.dataset[TARGET_COLUMN] == "").any():
            raise ValueError("Dataset contains empty fault labels.")

        # Group observations by bearing condition.
        self.samples_by_condition = {
            condition: group.reset_index(drop=True)
            for condition, group in self.dataset.groupby(TARGET_COLUMN)
        }

        # Verify expected bearing classes exist.
        missing_classes = [
            condition
            for condition in BEARING_CONDITIONS
            if condition not in self.samples_by_condition
        ]

        if missing_classes:
            raise ValueError(
                f"Dataset is missing bearing classes: {missing_classes}"
            )

        print(
            f"Dataset loaded successfully: "
            f"{len(self.dataset)} observations"
        )

        print(
            f"Available conditions: "
            f"{len(self.samples_by_condition)}"
        )

    def get_available_conditions(self) -> list[str]:
        """Return all bearing-condition classes available."""
        return list(self.samples_by_condition.keys())

    def get_sample_count(self, condition: str) -> int:
        """Return the number of rows for a given bearing condition."""

        self._validate_condition(condition)

        return len(self.samples_by_condition[condition])

    def _validate_condition(self, condition: str):
        """Verify that the requested bearing condition exists."""

        if condition not in self.samples_by_condition:
            raise ValueError(
                f"Unknown bearing condition: {condition}"
            )

    def _random_sample(self, condition: str) -> pd.Series:
        """Select a random observation from the condition."""

        group = self.samples_by_condition[condition]

        index = self.random_generator.randrange(len(group))

        return group.iloc[index]

    def _sequential_sample(self, condition: str) -> pd.Series:
        """Select observations sequentially and cycle when exhausted."""

        group = self.samples_by_condition[condition]

        cursor = self.cursors[condition]

        sample = group.iloc[cursor]

        self.cursors[condition] = (cursor + 1) % len(group)

        return sample

    def sample(
        self,
        condition: str,
        sampling_mode: SamplingMode = SamplingMode.RANDOM,
    ) -> VibrationMeasurement:
        """
        Sample a vibration observation.

        Returns:
            VibrationMeasurement:
                features: exactly nine model features
                ground_truth: actual source class
        """

        self._validate_condition(condition)

        if isinstance(sampling_mode, str):
            sampling_mode = SamplingMode(sampling_mode)

        if sampling_mode == SamplingMode.RANDOM:
            row = self._random_sample(condition)

        elif sampling_mode == SamplingMode.SEQUENTIAL:
            row = self._sequential_sample(condition)

        else:
            raise ValueError(
                f"Unsupported sampling mode: {sampling_mode}"
            )

        features = {
            column: float(row[column])
            for column in FEATURE_COLUMNS
        }

        values = np.array(list(features.values()), dtype=float)

        if len(features) != len(FEATURE_COLUMNS):
            raise ValueError(
                "Incorrect number of vibration features."
            )

        if not np.isfinite(values).all():
            raise ValueError(
                "Sample contains missing or infinite feature values."
            )

        ground_truth = str(row[TARGET_COLUMN])

        return VibrationMeasurement(
            features=features,
            ground_truth=ground_truth,
        )
