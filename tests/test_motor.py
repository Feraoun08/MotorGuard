
import pytest

from simulator.motor import MotorConfig, VirtualMotor
from simulator.config import MotorState, SamplingMode


def test_motor_initialization():
    motor = VirtualMotor(
        config=MotorConfig(
            motor_id="MOTOR_001",
            name="Test Motor",
            bearing_condition="Normal_1",
        )
    )

    assert motor.motor_id == "MOTOR_001"
    assert motor.name == "Test Motor"
    assert motor.bearing_condition == "Normal_1"
    assert motor.state == MotorState.STOPPED


def test_motor_start_and_stop():
    motor = VirtualMotor(
        config=MotorConfig(
            motor_id="MOTOR_001",
            name="Test Motor",
            bearing_condition="Normal_1",
        )
    )

    motor.start()
    assert motor.state == MotorState.RUNNING

    motor.stop()
    assert motor.state == MotorState.STOPPED


def test_independent_motor_instances():
    motor_1 = VirtualMotor(
        config=MotorConfig(
            motor_id="MOTOR_001",
            name="Motor 1",
            bearing_condition="Normal_1",
        )
    )

    motor_2 = VirtualMotor(
        config=MotorConfig(
            motor_id="MOTOR_002",
            name="Motor 2",
            bearing_condition="Ball_007_1",
        )
    )

    motor_1.start()

    assert motor_1.state == MotorState.RUNNING
    assert motor_2.state == MotorState.STOPPED

    assert motor_1.bearing_condition == "Normal_1"
    assert motor_2.bearing_condition == "Ball_007_1"


def test_invalid_bearing_condition():
    with pytest.raises(ValueError):
        MotorConfig(
            motor_id="MOTOR_001",
            name="Test Motor",
            bearing_condition="INVALID_CONDITION",
        )


def test_sampling_mode_string_conversion():
    config = MotorConfig(
        motor_id="MOTOR_001",
        name="Test Motor",
        bearing_condition="Normal_1",
        sampling_mode="sequential",
    )

    assert config.sampling_mode == SamplingMode.SEQUENTIAL
