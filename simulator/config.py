
from enum import Enum
from pathlib import Path


# PROJECT PATHS


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    PROJECT_ROOT
    /  "feature_time_48k_2048_load_1.csv"
)


# ML FEATURE CONTRACT


FEATURE_COLUMNS = [
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

TARGET_COLUMN = "fault"


# BEARING CONDITIONS


BEARING_CONDITIONS = [
    "Ball_007_1",
    "Ball_014_1",
    "Ball_021_1",
    "IR_007_1",
    "IR_014_1",
    "IR_021_1",
    "OR_007_6_1",
    "OR_014_6_1",
    "OR_021_6_1",
    "Normal_1",
]



# MOTOR STATES


class MotorState(str, Enum):
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    WARNING = "WARNING"
    FAULT = "FAULT"



# SAMPLING MODES


class SamplingMode(str, Enum):
    RANDOM = "random"
    SEQUENTIAL = "sequential"



# DEFAULT CONFIGURATION


DEFAULT_FACTORY_ID = "FACTORY_01"
DEFAULT_LINE_ID = "LINE_01"
DEFAULT_SAMPLING_MODE = SamplingMode.RANDOM
