
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.io import loadmat

DATA_DIR = Path(".")

# 1. Inspect all raw MATLAB recordings
raw_dir = DATA_DIR / "raw"

print("=" * 60)
print("RAW MATLAB FILES")
print("=" * 60)

for file_path in sorted(raw_dir.glob("*.mat")):
    print(f"\nFILE: {file_path.name}")

    mat = loadmat(file_path)

    for key, value in mat.items():
        if key.startswith("__"):
            continue

        if isinstance(value, np.ndarray):
            print(
                f"  {key}: shape={value.shape}, "
                f"dtype={value.dtype}"
            )

# 2. Inspect NPZ labels and distributions
print("\n" + "=" * 60)
print("NPZ CONTENT")
print("=" * 60)

npz = np.load("CWRU_48k_load_1_CNN_data.npz")

data = npz["data"]
labels = npz["labels"]

print("Data shape:", data.shape)
print("Labels shape:", labels.shape)

unique_labels, counts = np.unique(
    labels, return_counts=True
)

print("\nNPZ class distribution:")

for label, count in zip(unique_labels, counts):
    print(f"{label!r}: {count}")

print("\nFirst sample:")
print(data[0])

# 3. Inspect CSV class distribution
print("\n" + "=" * 60)
print("CSV CONTENT")
print("=" * 60)

df = pd.read_csv("feature_time_48k_2048_load_1.csv")

print("CSV classes:")
print(df["fault"].value_counts())

print("\nFirst rows:")
print(df.head())
