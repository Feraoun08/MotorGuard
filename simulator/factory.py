
import logging
import time
from datetime import datetime, timezone
from threading import Event
from typing import Callable, Optional

from simulator.config import MotorState
from simulator.sensors import SensorSimulator
from simulator.scenarios import apply_scenario


logger = logging.getLogger("motor_guard.factory")


class FactoryEngine:
    """
    Manages multiple virtual motors and generates measurements.

    """

    def __init__(
        self,
        dataset_provider,
        sensor_simulator: Optional[SensorSimulator] = None,
        interval_seconds: float = 2.0,
    ):
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")

        self.dataset_provider = dataset_provider

        self.sensor_simulator = (
            sensor_simulator or SensorSimulator()
        )

        self.interval_seconds = interval_seconds

        self.motors = {}

        self._stop_event = Event()
        self._running = False

   
    # MOTOR MANAGEMENT
   

    def register_motor(self, motor):
        """Register a motor with the factory."""

        if motor.motor_id in self.motors:
            raise ValueError(
                f"Motor already registered: {motor.motor_id}"
            )

        self.motors[motor.motor_id] = motor

        logger.info(
            "Motor registered: %s",
            motor.motor_id,
        )

    def unregister_motor(self, motor_id: str):
        """Remove a motor from the factory."""

        if motor_id not in self.motors:
            raise ValueError(
                f"Motor not registered: {motor_id}"
            )

        del self.motors[motor_id]

        logger.info(
            "Motor removed: %s",
            motor_id,
        )

    def get_motor(self, motor_id: str):
        """Retrieve a registered motor."""

        try:
            return self.motors[motor_id]
        except KeyError:
            raise ValueError(
                f"Motor not found: {motor_id}"
            ) from None

   
    # MOTOR CONTROL
   

    def start_motor(self, motor_id: str):
        motor = self.get_motor(motor_id)
        motor.start()

    def stop_motor(self, motor_id: str):
        motor = self.get_motor(motor_id)
        motor.stop()

    def change_scenario(
        self,
        motor_id: str,
        scenario_name: str,
    ):
        """
        Change the bearing scenario of a registered motor
        during simulation.
        """

        motor = self.get_motor(motor_id)

        scenario = apply_scenario(
            motor,
            scenario_name,
        )

        logger.info(
            "Scenario changed for %s: %s",
            motor_id,
            scenario.name,
        )

        return scenario

   
    # MEASUREMENT GENERATION
   

    def generate_motor_reading(self, motor):
        """
        Generate vibration and synthetic sensor measurements
        for one motor.
        """

        vibration = motor.generate_vibration(
            self.dataset_provider
        )

        is_faulty = (
            motor.bearing_condition != "Normal_1"
        )

        sensors = self.sensor_simulator.generate(
            motor_state=motor.state,
            is_faulty=is_faulty,
        )

        timestamp = datetime.now(timezone.utc).isoformat()

        return {
            "timestamp": timestamp,
            "motor_id": motor.motor_id,
            "motor_name": motor.name,
            "factory_id": motor.config.factory_id,
            "line_id": motor.config.line_id,
            "motor_state": motor.state.value,
            "bearing_condition": motor.bearing_condition,
            "vibration": vibration.features,
            "ground_truth": vibration.ground_truth,
            "sensors": sensors.to_dict(),
            "simulation": {
                "is_simulated": True,
                "vibration_source": "CWRU_PREPARED_CSV",
                "additional_sensor_source": "SYNTHETIC",
            },
        }

    def run_once(self) -> list[dict]:
        """
        Execute one factory cycle.

        Each motor is processed independently. An error in one
        motor will not prevent the others from generating readings.
        """

        results = []

        for motor in list(self.motors.values()):

            if motor.state == MotorState.STOPPED:
                continue

            try:
                reading = self.generate_motor_reading(motor)

                results.append(reading)

            except Exception:
                logger.exception(
                    "Measurement generation failed for motor %s",
                    motor.motor_id,
                )

        return results

   
    # SIMULATION LOOP
   

    def run(
        self,
        max_cycles: Optional[int] = None,
        on_reading: Optional[Callable[[dict], None]] = None,
    ):
        """
        Run the factory continuously.

        max_cycles=None means run until stop() is called
        or Ctrl+C is pressed.

        on_reading can be a callback for processing each
        measurement.
        """

        if self._running:
            raise RuntimeError(
                "Factory simulation is already running."
            )

        self._running = True
        self._stop_event.clear()

        cycle = 0

        logger.info("Factory simulation started.")

        try:
            while not self._stop_event.is_set():

                cycle += 1

                readings = self.run_once()

                for reading in readings:

                    if on_reading is not None:
                        try:
                            on_reading(reading)
                        except Exception:
                            logger.exception(
                                "Reading callback failed for %s",
                                reading.get("motor_id"),
                            )
                    else:
                        print(reading)

                if max_cycles is not None and cycle >= max_cycles:
                    break

                self._stop_event.wait(
                    self.interval_seconds
                )

        finally:
            self._running = False

            logger.info(
                "Factory simulation stopped after %s cycles.",
                cycle,
            )

    def stop(self):
        """Request a graceful shutdown."""

        self._stop_event.set()

    @property
    def is_running(self) -> bool:
        return self._running
