
from dataclasses import dataclass
from typing import Optional

from simulator.config import (
    BEARING_CONDITIONS,
    DEFAULT_FACTORY_ID,
    DEFAULT_LINE_ID,
    DEFAULT_SAMPLING_MODE,
    MotorState,
    SamplingMode,
)


@dataclass
class MotorConfig:
    motor_id: str
    name: str
    bearing_condition: str

    factory_id: str = DEFAULT_FACTORY_ID
    line_id: str = DEFAULT_LINE_ID
    sampling_mode: SamplingMode = DEFAULT_SAMPLING_MODE

    def __post_init__(self):
        if not self.motor_id.strip():
            raise ValueError("motor_id cannot be empty")

        if not self.name.strip():
            raise ValueError("Motor name cannot be empty")

        if self.bearing_condition not in BEARING_CONDITIONS:
            raise ValueError(
                f"Invalid bearing condition: {self.bearing_condition}"
            )

        if isinstance(self.sampling_mode, str):
            self.sampling_mode = SamplingMode(self.sampling_mode)


@dataclass
class VibrationMeasurement:
    features: dict[str, float]
    ground_truth: str


@dataclass
class VirtualMotor:
    config: MotorConfig

    state: MotorState = MotorState.STOPPED

    current_measurement: Optional[VibrationMeasurement] = None

    def start(self):
        self.state = MotorState.RUNNING

    def stop(self):
        self.state = MotorState.STOPPED

    def set_state(self, new_state: MotorState):
        if not isinstance(new_state, MotorState):
            raise ValueError("new_state must be a MotorState")

        self.state = new_state

    @property
    def motor_id(self) -> str:
        return self.config.motor_id

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def bearing_condition(self) -> str:
        return self.config.bearing_condition

    def generate_vibration(self, dataset_provider) -> VibrationMeasurement:
        """
        Request a vibration sample from the dataset provider
        based on this motor's bearing condition.
        """

        measurement = dataset_provider.sample(
            condition=self.config.bearing_condition,
            sampling_mode=self.config.sampling_mode,
        )

        self.current_measurement = measurement

        return measurement

    def update_measurement(self, measurement: VibrationMeasurement):
        self.current_measurement = measurement

    def to_dict(self) -> dict:
        return {
            "motor_id": self.motor_id,
            "name": self.name,
            "factory_id": self.config.factory_id,
            "line_id": self.config.line_id,
            "bearing_condition": self.bearing_condition,
            "sampling_mode": self.config.sampling_mode.value,
            "state": self.state.value,
        }
