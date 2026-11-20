
import pandas as pd
import numpy as np

# Inspect CSV
df = pd.read_csv("feature_time_48k_2048_load_1.csv")

print("CSV shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\nFault classes:")
print(df["fault"].value_counts())

# Inspect NPZ
data = np.load("CWRU_48k_load_1_CNN_data.npz")

print("\nNPZ arrays:")
for key in data.files:
    arr = data[key]
    print(key, arr.shape, arr.dtype)
