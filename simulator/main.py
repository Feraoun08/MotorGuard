
import logging
import json

from simulator.dataset_provider import DatasetProvider
from simulator.factory import FactoryEngine
from simulator.motor import MotorConfig, VirtualMotor
from simulator.sensors import SensorSimulator
from simulator.config import SamplingMode
from simulator.scenarios import apply_scenario


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def main():
    
    # 1. Load vibration dataset
    

    dataset_provider = DatasetProvider(
        random_seed=42
    )

    
    # 2. Initialize synthetic sensor simulator
    

    sensor_simulator = SensorSimulator(
        random_seed=42
    )

    
    # 3. Initialize factory engine
    

    factory = FactoryEngine(
        dataset_provider=dataset_provider,
        sensor_simulator=sensor_simulator,
        interval_seconds=2.0,
    )

    
    # 4. Create motors
    

    motor_1 = VirtualMotor(
        config=MotorConfig(
            motor_id="MOTOR_001",
            name="Conveyor Motor",
            bearing_condition="Normal_1",
            factory_id="FACTORY_01",
            line_id="LINE_01",
            sampling_mode=SamplingMode.RANDOM,
        )
    )

    motor_2 = VirtualMotor(
        config=MotorConfig(
            motor_id="MOTOR_002",
            name="Pump Motor",
            bearing_condition="Ball_007_1",
            factory_id="FACTORY_01",
            line_id="LINE_01",
            sampling_mode=SamplingMode.RANDOM,
        )
    )

    motor_3 = VirtualMotor(
        config=MotorConfig(
            motor_id="MOTOR_003",
            name="Cooling Fan",
            bearing_condition="IR_014_1",
            factory_id="FACTORY_01",
            line_id="LINE_02",
            sampling_mode=SamplingMode.SEQUENTIAL,
        )
    )

    
    # 5. Register motors
    

    factory.register_motor(motor_1)
    factory.register_motor(motor_2)
    factory.register_motor(motor_3)

    
    # 6. Start motors
    

    factory.start_motor("MOTOR_001")
    factory.start_motor("MOTOR_002")
    factory.start_motor("MOTOR_003")

    
    # 7. Display generated readings
    

    def display_reading(reading):
        print("\n" + "=" * 70)

        print(
            json.dumps(
                reading,
                indent=4,
                ensure_ascii=False,
            )
        )

        print("=" * 70)

    
    # 8. Run simulation
    

    try:
        factory.run(
            max_cycles=5,
            on_reading=display_reading,
        )

    except KeyboardInterrupt:
        print("\nShutdown requested.")

    finally:
        factory.stop()

    print("\nFactory simulation finished.")


if __name__ == "__main__":
    main()
