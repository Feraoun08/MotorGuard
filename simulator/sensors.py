
import random
from dataclasses import dataclass

from simulator.config import MotorState


@dataclass
class SensorReading:
    temperature: float
    current: float
    rpm: float

    def to_dict(self) -> dict:
        return {
            "temperature": round(self.temperature, 2),
            "current": round(self.current, 3),
            "rpm": round(self.rpm, 2),
        }


@dataclass
class SensorConfig:
    # Normal operating values
    normal_temperature: float = 45.0
    normal_current: float = 4.8
    normal_rpm: float = 1750.0

    # Healthy operating fluctuation
    temperature_variation: float = 1.5
    current_variation: float = 0.25
    rpm_variation: float = 15.0

    # Fault-related increases
    faulty_temperature_increase: float = 8.0
    faulty_current_increase: float = 1.2
    faulty_rpm_variation: float = 45.0

    # Stopped motor values
    stopped_temperature: float = 30.0
    stopped_current: float = 0.0
    stopped_rpm: float = 0.0


class SensorSimulator:
    """
    Generates synthetic sensor measurements
    """

    def __init__(
        self,
        config: SensorConfig | None = None,
        random_seed: int | None = None,
    ):
        self.config = config or SensorConfig()
        self.random = random.Random(random_seed)

    def _variation(self, center: float, variation: float) -> float:
        return self.random.uniform(center - variation, center + variation)

    def generate(
        self,
        motor_state: MotorState,
        is_faulty: bool = False,
    ) -> SensorReading:

        
        # STOPPED
        
        if motor_state == MotorState.STOPPED:
            temperature = self._variation(
                self.config.stopped_temperature,
                1.0,
            )

            return SensorReading(
                temperature=temperature,
                current=self.config.stopped_current,
                rpm=self.config.stopped_rpm,
            )

        
        # FAULT
        
        if motor_state == MotorState.FAULT:
            temperature = self._variation(
                self.config.normal_temperature
                + self.config.faulty_temperature_increase,
                2.0,
            )

            current = self._variation(
                self.config.normal_current
                + self.config.faulty_current_increase,
                0.5,
            )

            # A severe simulated fault can stop the shaft.
            rpm = self.random.choice([
                0.0,
                self._variation(
                    self.config.normal_rpm,
                    self.config.faulty_rpm_variation,
                ),
            ])

            return SensorReading(
                temperature=temperature,
                current=max(0.0, current),
                rpm=max(0.0, rpm),
            )

        
        # RUNNING / WARNING
        
        temperature_center = self.config.normal_temperature
        current_center = self.config.normal_current
        rpm_variation = self.config.rpm_variation

        if is_faulty:
            temperature_center += (
                self.config.faulty_temperature_increase
            )

            current_center += (
                self.config.faulty_current_increase
            )

            rpm_variation = self.config.faulty_rpm_variation

        if motor_state == MotorState.WARNING:
            temperature_center += 3.0
            current_center += 0.5
            rpm_variation += 10.0

        temperature = self._variation(
            temperature_center,
            self.config.temperature_variation,
        )

        current = self._variation(
            current_center,
            self.config.current_variation,
        )

        rpm = self._variation(
            self.config.normal_rpm,
            rpm_variation,
        )

        return SensorReading(
            temperature=temperature,
            current=max(0.0, current),
            rpm=max(0.0, rpm),
        )
