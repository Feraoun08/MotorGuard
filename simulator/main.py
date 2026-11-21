
from simulator.config import SamplingMode
from simulator.motor import MotorConfig, VirtualMotor
from simulator.dataset_provider import DatasetProvider


def main():
    # Load the vibration dataset once.
    dataset_provider = DatasetProvider(random_seed=42)

    # Create a healthy motor.
    motor_1 = VirtualMotor(
        config=MotorConfig(
            motor_id="MOTOR_001",
            name="Conveyor Motor",
            bearing_condition="Normal_1",
            sampling_mode=SamplingMode.RANDOM,
        )
    )

    # Create a faulty motor.
    motor_2 = VirtualMotor(
        config=MotorConfig(
            motor_id="MOTOR_002",
            name="Pump Motor",
            bearing_condition="Ball_007_1",
            sampling_mode=SamplingMode.RANDOM,
        )
    )

    # Create a motor with sequential sampling.
    motor_3 = VirtualMotor(
        config=MotorConfig(
            motor_id="MOTOR_003",
            name="Cooling Fan Motor",
            bearing_condition="IR_014_1",
            sampling_mode=SamplingMode.SEQUENTIAL,
        )
    )

    motors = [motor_1, motor_2, motor_3]

    for motor in motors:
        motor.start()

        measurement = motor.generate_vibration(dataset_provider)

        print("\n" + "=" * 50)
        print(f"Motor: {motor.name}")
        print(f"ID: {motor.motor_id}")
        print(f"State: {motor.state.value}")
        print(f"Configured condition: {motor.bearing_condition}")
        print(f"Ground truth: {measurement.ground_truth}")
        print("Features:")

        for feature, value in measurement.features.items():
            print(f"  {feature}: {value}")

        print("Motor metadata:")
        print(motor_info := motor.to_dict())
        print("=" * 50)


if __name__ == "__main__":
    main()
