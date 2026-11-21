
import pytest

from simulator.config import MotorState, SamplingMode
from simulator.motor import MotorConfig, VirtualMotor, VibrationMeasurement
from simulator.sensors import SensorSimulator
from simulator.factory import FactoryEngine
from simulator.scenarios import (
    get_scenario,
    apply_scenario,
)


FEATURES = {
    "max": 0.35,
    "min": -0.42,
    "mean": 0.018,
    "sd": 0.12,
    "rms": 0.124,
    "skewness": -0.11,
    "kurtosis": -0.04,
    "crest": 2.9,
    "form": 6.95,
}


class FakeDatasetProvider:
    """Fake provider for testing the engine without a CSV."""

    def sample(self, condition, sampling_mode):
        return VibrationMeasurement(
            features=FEATURES.copy(),
            ground_truth=condition,
        )


def create_motor(
    motor_id="MOTOR_001",
    condition="Normal_1",
):
    return VirtualMotor(
        config=MotorConfig(
            motor_id=motor_id,
            name=f"Test Motor {motor_id}",
            bearing_condition=condition,
            sampling_mode=SamplingMode.RANDOM,
        )
    )



# SENSOR TESTS


def test_stopped_motor_sensor_values():
    sensors = SensorSimulator(random_seed=42)

    reading = sensors.generate(
        motor_state=MotorState.STOPPED,
    )

    assert reading.current == 0.0
    assert reading.rpm == 0.0
    assert reading.temperature > 0


def test_running_motor_sensor_values():
    sensors = SensorSimulator(random_seed=42)

    reading = sensors.generate(
        motor_state=MotorState.RUNNING,
    )

    assert reading.temperature > 0
    assert reading.current > 0
    assert reading.rpm > 0


def test_faulty_motor_sensor_values():
    sensors = SensorSimulator(random_seed=42)

    reading = sensors.generate(
        motor_state=MotorState.RUNNING,
        is_faulty=True,
    )

    assert reading.temperature > 0
    assert reading.current > 0
    assert reading.rpm >= 0


def test_sensor_reading_serialization():
    sensors = SensorSimulator(random_seed=42)

    reading = sensors.generate(
        motor_state=MotorState.RUNNING,
    )

    data = reading.to_dict()

    assert "temperature" in data
    assert "current" in data
    assert "rpm" in data



# SCENARIO TESTS


def test_healthy_scenario():
    scenario = get_scenario("healthy")

    assert scenario.bearing_condition == "Normal_1"


def test_ball_fault_scenario():
    scenario = get_scenario("ball_007")

    assert scenario.bearing_condition == "Ball_007_1"


def test_inner_race_scenario():
    scenario = get_scenario("inner_014")

    assert scenario.bearing_condition == "IR_014_1"


def test_outer_race_scenario():
    scenario = get_scenario("outer_021")

    assert scenario.bearing_condition == "OR_021_6_1"


def test_unknown_scenario():
    with pytest.raises(ValueError):
        get_scenario("unknown_scenario")


def test_apply_scenario_to_motor():
    motor = create_motor(
        condition="Normal_1",
    )

    scenario = apply_scenario(
        motor,
        "ball_007",
    )

    assert motor.bearing_condition == "Ball_007_1"
    assert scenario.bearing_condition == "Ball_007_1"



# FACTORY TESTS


def test_factory_register_motor():
    factory = FactoryEngine(
        dataset_provider=FakeDatasetProvider(),
    )

    motor = create_motor()

    factory.register_motor(motor)

    assert "MOTOR_001" in factory.motors


def test_factory_duplicate_motor_registration():
    factory = FactoryEngine(
        dataset_provider=FakeDatasetProvider(),
    )

    motor = create_motor()

    factory.register_motor(motor)

    with pytest.raises(ValueError):
        factory.register_motor(motor)


def test_factory_motor_start_stop():
    factory = FactoryEngine(
        dataset_provider=FakeDatasetProvider(),
    )

    motor = create_motor()

    factory.register_motor(motor)

    factory.start_motor("MOTOR_001")

    assert motor.state == MotorState.RUNNING

    factory.stop_motor("MOTOR_001")

    assert motor.state == MotorState.STOPPED


def test_factory_generates_reading():
    factory = FactoryEngine(
        dataset_provider=FakeDatasetProvider(),
    )

    motor = create_motor(
        condition="Normal_1",
    )

    factory.register_motor(motor)
    factory.start_motor("MOTOR_001")

    reading = factory.generate_motor_reading(motor)

    assert reading["motor_id"] == "MOTOR_001"
    assert reading["motor_state"] == "RUNNING"
    assert len(reading["vibration"]) == 9

    assert "temperature" in reading["sensors"]
    assert "current" in reading["sensors"]
    assert "rpm" in reading["sensors"]

    assert reading["simulation"]["is_simulated"] is True


def test_factory_run_once():
    factory = FactoryEngine(
        dataset_provider=FakeDatasetProvider(),
    )

    motor_1 = create_motor(
        "MOTOR_001",
        "Normal_1",
    )

    motor_2 = create_motor(
        "MOTOR_002",
        "Ball_007_1",
    )

    factory.register_motor(motor_1)
    factory.register_motor(motor_2)

    factory.start_motor("MOTOR_001")
    factory.start_motor("MOTOR_002")

    results = factory.run_once()

    assert len(results) == 2


def test_stopped_motors_are_skipped():
    factory = FactoryEngine(
        dataset_provider=FakeDatasetProvider(),
    )

    motor = create_motor()

    factory.register_motor(motor)

    # Motor remains STOPPED.
    results = factory.run_once()

    assert results == []


def test_factory_scenario_change():
    factory = FactoryEngine(
        dataset_provider=FakeDatasetProvider(),
    )

    motor = create_motor()

    factory.register_motor(motor)

    scenario = factory.change_scenario(
        "MOTOR_001",
        "inner_007",
    )

    assert scenario.bearing_condition == "IR_007_1"
    assert motor.bearing_condition == "IR_007_1"


def test_factory_unknown_motor():
    factory = FactoryEngine(
        dataset_provider=FakeDatasetProvider(),
    )

    with pytest.raises(ValueError):
        factory.get_motor("UNKNOWN")
