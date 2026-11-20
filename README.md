# MotorGuard IoT — Dataset Technical Documentation

## 1. Dataset Overview

MotorGuard IoT is an industrial predictive-maintenance project focused on monitoring motor conditions and detecting bearing faults using vibration measurements and machine learning.

The first machine-learning experiment uses a prepared statistical feature dataset derived from the Case Western Reserve University (CWRU) bearing dataset.

Instead of processing raw vibration recordings during model training, we use an existing CSV file containing statistical features that have already been calculated from vibration signal windows.

### Dataset file

```text
feature_time_48k_2048_load1.csv
```

### Dataset characteristics

| Property | Value |
|---|---|
| Dataset | CWRU Bearing Dataset |
| File format | CSV |
| Total observations | 2,300 |
| Numerical input features | 9 |
| Target variable | fault |
| Number of classes | 10 |
| Observations per class | 230 |
| Sampling frequency indicated by filename | 48,000 Hz |
| Window size indicated by filename | 2,048 samples |
| Window duration | Approximately 42.67 ms |
| Learning task | Supervised multiclass classification |

The sampling frequency and window size are inferred from the dataset filename and its associated preparation context. They are not individual columns in the CSV.

### Dataset structure

```text
feature_time_48k_2048_load1.csv
│
├── max
├── min
├── mean
├── sd
├── rms
├── skewness
├── kurtosis
├── crest
├── form
└── fault
```

The first nine columns represent numerical characteristics of vibration signals.

The `fault` column identifies the corresponding bearing condition and serves as the classification target.

---

## 2. Physical Meaning of the Dataset

### 2.1 Bearing fault detection

Industrial motors use rolling-element bearings to support rotating shafts and reduce friction.

A bearing generally consists of:

- Inner race.
- Outer race.
- Rolling elements (balls or rollers).
- Cage that maintains the spacing of rolling elements.

Mechanical defects can develop on different bearing components.

These defects can generate abnormal vibration patterns during motor operation.

The CWRU dataset contains vibration measurements associated with healthy and faulty bearing conditions.

### 2.2 Fault categories

The dataset contains three fault families and one healthy condition.

| Label prefix | Bearing condition | Description |
|---|---|---|
| B | Ball fault | Defect on a rolling element |
| IR | Inner race fault | Defect on the inner bearing race |
| OR | Outer race fault | Defect on the outer bearing race |
| Normal | Healthy | No seeded bearing fault in the recording |

### 2.3 Defect diameter

The numerical suffix identifies the defect diameter.

| Suffix | Defect diameter |
|---|---|
| 007 | 0.007 inches |
| 014 | 0.014 inches |
| 021 | 0.021 inches |

These correspond approximately to:

| Diameter | Equivalent in millimeters |
|---|---:|
| 0.007 inches | 0.1778 mm |
| 0.014 inches | 0.3556 mm |
| 0.021 inches | 0.5334 mm |

### 2.4 Load and position identifiers

The label suffixes also include experimental configuration information.

- `1` identifies load condition 1 in this dataset.
- `6` in the outer-race labels identifies the outer-race fault position code, associated with the 6 o'clock position in the CWRU naming convention.

For example:

```text
OR_014_6_1
```

means:

- OR: outer-race fault.
- 014: 0.014-inch defect diameter.
- 6: outer-race fault position.
- 1: load condition 1.

The dataset contains the following ten classes:

```text
Ball_007_1
Ball_014_1
Ball_021_1

IR_007_1
IR_014_1
IR_021_1

OR_007_6_1
OR_014_6_1
OR_021_6_1

Normal_1
```

---

## 3. Feature Technical Reference

The dataset contains nine statistical features calculated from vibration signal windows.

These features describe different characteristics of the vibration amplitude distribution.

Let:

- \(x_i\) represent the \(i\)-th vibration measurement.
- \(N\) represent the number of measurements in a window.
- \(\bar{x}\) represent the arithmetic mean.

### 3.1 Maximum (`max`)

**Definition:** The highest signed amplitude recorded in a window.

Formula:

\[
x_{\max} = \max(x_1,x_2,\ldots,x_N)
\]

**Purpose:**

- Identifies the highest positive vibration amplitude.
- Helps characterize the amplitude range.
- Can reflect strong positive vibration peaks.

**Industrial relevance:**

Large maximum amplitudes may indicate increased vibration intensity or abnormal mechanical behavior.

### 3.2 Minimum (`min`)

**Definition:** The lowest signed amplitude recorded in a window.

Formula:

\[
x_{\min} = \min(x_1,x_2,\ldots,x_N)
\]

**Purpose:**

- Identifies the lowest negative vibration amplitude.
- Describes the negative extreme of the signal.
- Complements the maximum amplitude.

**Industrial relevance:**

Together, maximum and minimum values help describe the vibration signal's amplitude range.

### 3.3 Mean (`mean`)

**Definition:** The arithmetic average of all measurements in a window.

Formula:

\[
\bar{x} = \frac{1}{N}\sum_{i=1}^{N}x_i
\]

**Purpose:**

- Measures the average signal level.
- Helps identify signal offsets or asymmetry around zero.
- Describes the central value of the measurements.

**Industrial relevance:**

A change in the mean may indicate a shift in the signal baseline, although vibration fault detection often relies more strongly on other statistical features.

### 3.4 Standard Deviation (`sd`)

**Definition:** Measures the dispersion of vibration measurements around their mean.

A population-style formula is:

\[
\sigma =
\sqrt{
\frac{1}{N}
\sum_{i=1}^{N}(x_i-\bar{x})^2
}
\]

**Purpose:**

- Measures signal variability.
- Quantifies how widely measurements are distributed.
- Indicates changes in vibration amplitude fluctuations.

**Industrial relevance:**

Higher standard deviation values may indicate stronger or more variable vibration behavior.

**Implementation note:** The CSV does not specify whether population or sample standard deviation was used during its original preparation. The exact convention should be verified before attempting to reproduce the feature values.

### 3.5 Root Mean Square (`rms`)

**Definition:** Measures the effective magnitude of the vibration signal.

Formula:

\[
RMS =
\sqrt{
\frac{1}{N}
\sum_{i=1}^{N}x_i^2
}
\]

**Purpose:**

- Quantifies the overall vibration amplitude.
- Gives greater weight to large amplitudes because measurements are squared.
- Provides an indication of vibration energy or intensity.

**Industrial relevance:**

RMS is commonly used in vibration monitoring because an increase in vibration magnitude can indicate changes in mechanical condition.

It is particularly useful for comparing vibration intensity between operating conditions.

### 3.6 Skewness (`skewness`)

**Definition:** Measures the asymmetry of the signal's amplitude distribution.

A common standardized third-moment definition is:

\[
Skewness =
\frac{
\frac{1}{N}\sum_{i=1}^{N}(x_i-\bar{x})^3
}{
\sigma^3
}
\]

**Interpretation:**

- Approximately zero: relatively symmetric distribution.
- Positive: distribution has a longer positive tail.
- Negative: distribution has a longer negative tail.

**Industrial relevance:**

Skewness can help identify asymmetric vibration distributions and changes in the distribution of signal amplitudes.

### 3.7 Kurtosis (`kurtosis`)

**Definition:** Describes the concentration and tail behavior of the amplitude distribution, with sensitivity to extreme observations.

A common Pearson kurtosis definition is:

\[
Kurtosis =
\frac{
\frac{1}{N}\sum_{i=1}^{N}(x_i-\bar{x})^4
}{
\sigma^4
}
\]

Fisher excess kurtosis is:

\[
Kurtosis_{excess} = Kurtosis - 3
\]

**Interpretation:**

- High kurtosis can indicate stronger tail behavior and extreme observations.
- Values near zero in the excess convention correspond to a distribution with normal-like kurtosis.
- The interpretation depends on the convention used.

**Industrial relevance:**

Bearing defects can generate impulsive vibration behavior. Kurtosis can help detect distributions containing unusually large vibration amplitudes.

**Implementation note:** The original CSV preparation does not explicitly document whether Pearson or Fisher excess kurtosis was used. This must be verified before comparing independently calculated values.

### 3.8 Crest Factor (`crest`)

**Definition:** Ratio between the largest absolute vibration amplitude and RMS.

Formula:

\[
Crest =
\frac{\max(|x_i|)}{RMS}
\]

**Purpose:**

- Measures the relationship between peak amplitude and overall vibration level.
- Highlights signals with relatively strong peaks.
- Helps characterize impulsive vibration behavior.

**Industrial relevance:**

A high crest factor may indicate occasional strong vibration peaks even when the overall RMS level is not particularly high.

This can provide useful information about certain bearing defects.

### 3.9 Form Factor (`form`)

**Definition:** Ratio between RMS and the mean absolute amplitude.

Formula:

\[
Form =
\frac{RMS}{
\frac{1}{N}\sum_{i=1}^{N}|x_i|
}
\]

**Purpose:**

- Describes the relationship between effective amplitude and average rectified amplitude.
- Provides information about the shape of the amplitude distribution.

**Industrial relevance:**

Form factor can complement RMS and other statistical indicators when comparing vibration signal characteristics.

---

## 4. Feature Summary Table

| Feature | Statistical property | Main purpose |
|---|---|---|
| max | Positive extreme | Maximum vibration amplitude |
| min | Negative extreme | Minimum vibration amplitude |
| mean | Central tendency | Average signal level |
| sd | Dispersion | Signal variability |
| rms | Effective magnitude | Overall vibration intensity |
| skewness | Asymmetry | Distribution asymmetry |
| kurtosis | Tail behavior | Sensitivity to extreme amplitudes |
| crest | Peak-to-RMS ratio | Relative peak intensity |
| form | RMS-to-mean-absolute ratio | Amplitude distribution shape |

All nine features are numerical inputs to the machine-learning models.

---

## 5. Correlation Analysis

Correlation analysis measures the strength and direction of linear relationships between numerical features.

The Pearson correlation coefficient ranges from -1 to +1.

- +1: perfect positive linear correlation.
- 0: no linear correlation.
- -1: perfect negative linear correlation.

### Observed correlations

| Feature pair | Correlation | Interpretation |
|---|---:|---|
| sd / rms | 0.999998 | Almost perfect positive correlation |
| max / sd | 0.951709 | Very strong positive correlation |
| max / rms | 0.951700 | Very strong positive correlation |
| min / sd | -0.947029 | Very strong negative correlation |
| min / rms | -0.947007 | Very strong negative correlation |
| sd / form | 0.920629 | Very strong positive correlation |
| rms / form | 0.920397 | Very strong positive correlation |
| kurtosis / crest | 0.892333 | Very strong positive correlation |

### Interpretation

The strongest relationship is between standard deviation and RMS.

Their correlation of 0.999998 indicates that they provide almost identical linear information in this dataset.

Other strong relationships suggest overlapping information between amplitude-related features.

This does not mean that correlated features are necessarily useless.

For the initial experiment, all nine features are retained.

Random Forest can generally work with correlated features, although importance can be distributed between related variables.

SVM may also be affected by redundant dimensions, making appropriate scaling and model evaluation important.

Correlation describes association, not causation.

---

## 6. Dataset Quality and Limitations

### 6.1 Balanced classes

The dataset contains 2,300 observations distributed equally across ten classes.

| Class | Observations |
|---|---:|
| Ball_007_1 | 230 |
| Ball_014_1 | 230 |
| Ball_021_1 | 230 |
| IR_007_1 | 230 |
| IR_014_1 | 230 |
| IR_021_1 | 230 |
| OR_007_6_1 | 230 |
| OR_014_6_1 | 230 |
| OR_021_6_1 | 230 |
| Normal_1 | 230 |
| **Total** | **2,300** |

The balanced distribution means that each class contributes equally to the number of observations.

### 6.2 Outliers

Some features contain observations outside their main distributions.

These should not automatically be considered errors.

In vibration analysis, extreme observations may represent meaningful mechanical behavior, such as impulsive vibration caused by bearing defects.

Outlier removal should therefore be based on a justified data-quality investigation rather than automatic filtering.

### 6.3 Missing provenance information

The prepared CSV does not contain explicit source-recording identifiers or chronological window indices.

Consequently, we cannot establish from this CSV alone whether different observations originate from independent recordings.

If multiple windows originate from the same original recording, a random train/test split could place highly similar observations in both sets.

This may lead to overly optimistic performance estimates.

Therefore, a stratified random holdout should be reported as a baseline evaluation, not proof of generalization to unseen recordings or physical motors.

### 6.4 Missing physical sensor metadata

The CSV contains statistical vibration features, not complete sensor telemetry.

It does not directly provide:

- Temperature.
- Electrical current.
- Motor speed as a model input.
- Motor load as a separate numerical input.
- Bearing degradation over time.
- Time until failure.

The sampling frequency and window size are indicated by the dataset context and filename, but are not individual feature columns.

The units and calibration details of the numerical feature values are not explicitly documented in this CSV.

### 6.5 Fault classification versus RUL prediction

This dataset supports a supervised bearing-condition classification task.

It does not provide a complete run-to-failure timeline.

Therefore, the model cannot directly estimate remaining useful life or the number of operating hours before failure.

---

## 7. Machine-Learning Application

The nine numerical features are used as inputs to a supervised multiclass classifier.

### Input

```python
X = df[
    [
        "max",
        "min",
        "mean",
        "sd",
        "rms",
        "skewness",
        "kurtosis",
        "crest",
        "form"
    ]
]
```

### Target

```python
y = df["fault"]
```

### Planned algorithms

**Random Forest**

An ensemble of decision trees used for classification.

It can model nonlinear relationships and does not require feature scaling.

**Support Vector Machine**

A classifier that learns decision boundaries between classes.

An RBF kernel will be investigated, and numerical features will be standardized using `StandardScaler` inside a Scikit-learn Pipeline.

### Evaluation metrics

The models will be evaluated using:

- Accuracy.
- Precision.
- Recall.
- Macro F1-score.
- Classification report.
- Confusion matrix.

Macro F1-score is particularly useful because it gives equal importance to all ten classes.

---

## 8. Future Integration into MotorGuard IoT

The trained model will eventually become part of the backend classification pipeline.

The planned workflow is:

```text
Virtual Industrial Motor
          |
          v
Vibration Telemetry
          |
          v
Window Processing
          |
          v
Statistical Feature Vector
          |
          v
Saved ML Model
          |
          v
Bearing Fault Prediction
          |
          v
Backend Alert and Dashboard
```

The incoming vibration data must be processed using compatible feature definitions and feature ordering.

The model expects the following nine inputs:

```text
max
min
mean
sd
rms
skewness
kurtosis
crest
form
```

Temperature, current and other sensor measurements may be simulated separately in the future IoT architecture.

They must not be represented as measurements contained in this CSV.

---

## 9. Final Technical Summary

The prepared CWRU CSV provides a balanced dataset of 2,300 vibration-window observations, represented by nine statistical features and ten bearing-condition classes.

The features describe amplitude, variability, distribution shape and peak behavior.

The EDA reveals significant differences between several bearing conditions, as well as strong correlations between certain features.

This dataset will be used to develop and evaluate Random Forest and SVM classification models.

The resulting model will serve as the first machine-learning component of MotorGuard IoT and will later be integrated into the simulated industrial monitoring architecture.

**Scope:** Offline bearing fault classification using prepared statistical vibration features.

**Not included:** Raw signal extraction, deep learning, RUL estimation, temperature prediction or real-time IoT communication.