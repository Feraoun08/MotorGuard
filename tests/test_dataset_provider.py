
import numpy as np
import pandas as pd
import pytest

from simulator.config import (
    BEARING_CONDITIONS,
    FEATURE_COLUMNS,
    SamplingMode,
)
from simulator.dataset_provider import DatasetProvider


@pytest.fixture
def sample_dataset(tmp_path):
    rows = []

    for class_index, condition in enumerate(BEARING_CONDITIONS):
        for i in range(5):
            row = {
                feature: float(i + class_index + 1)
                for feature in FEATURE_COLUMNS
            }

            row["fault"] = condition
            rows.append(row)

    dataset_path = tmp_path / "sample.csv"

    pd.DataFrame(rows).to_csv(
        dataset_path,
        index=False,
    )

    return dataset_path


def test_dataset_loading(sample_dataset):
    provider = DatasetProvider(sample_dataset)

    assert len(provider.get_available_conditions()) == 10


def test_sample_returns_nine_features(sample_dataset):
    provider = DatasetProvider(sample_dataset, random_seed=42)

    measurement = provider.sample(
        "Normal_1",
        SamplingMode.RANDOM,
    )

    assert len(measurement.features) == 9
    assert list(measurement.features.keys()) == FEATURE_COLUMNS


def test_ground_truth_is_separate(sample_dataset):
    provider = DatasetProvider(sample_dataset)

    measurement = provider.sample(
        "Ball_007_1",
        SamplingMode.RANDOM,
    )

    assert measurement.ground_truth == "Ball_007_1"
    assert "fault" not in measurement.features


def test_sequential_sampling(sample_dataset):
    provider = DatasetProvider(sample_dataset)

    first = provider.sample(
        "Normal_1",
        SamplingMode.SEQUENTIAL,
    )

    second = provider.sample(
        "Normal_1",
        SamplingMode.SEQUENTIAL,
    )

    assert first.features != second.features


def test_invalid_condition(sample_dataset):
    provider = DatasetProvider(sample_dataset)

    with pytest.raises(ValueError):
        provider.sample("Unknown_Class")


def test_features_are_finite(sample_dataset):
    provider = DatasetProvider(sample_dataset)

    measurement = provider.sample("Normal_1")

    values = np.array(list(measurement.features.values()))

    assert np.isfinite(values).all()


def test_sample_count(sample_dataset):
    provider = DatasetProvider(sample_dataset)

    assert provider.get_sample_count("Normal_1") == 5
