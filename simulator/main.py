import logging

from simulator.telemetry import serialize_telemetry
from simulator.dataset_provider import DatasetProvider
from simulator.factory import FactoryEngine
from simulator.motor import MotorConfig, VirtualMotor
from simulator.sensors import SensorSimulator
from simulator.config import SamplingMode

from communication.mqtt_config import MQTTConfig
from communication.mqtt_publisher import MQTTPublisher
from communication.mqtt_factory_adapter import MQTTFactoryAdapter


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("motor_guard.main")


def display_reading(reading: dict):
    """Display telemetry locally when MQTT is unavailable."""

    print("\n" + "=" * 70)
    print("MOTORGARD - LOCAL TELEMETRY")
    print("=" * 70)

    print(serialize_telemetry(reading))


def main():
   
    # 1. INITIALIZE SIMULATOR
   

    dataset_provider = DatasetProvider(random_seed=42)

    sensor_simulator = SensorSimulator(random_seed=42)

    factory = FactoryEngine(
        dataset_provider=dataset_provider,
        sensor_simulator=sensor_simulator,
        interval_seconds=2.0,
    )

   
    # 2. CREATE MOTORS
   

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

   
    # 3. REGISTER MOTORS
   

    factory.register_motor(motor_1)
    factory.register_motor(motor_2)
    factory.register_motor(motor_3)

   
    # 4. START MOTORS
   

    factory.start_motor("MOTOR_001")
    factory.start_motor("MOTOR_002")
    factory.start_motor("MOTOR_003")

   
    # 5. INITIALIZE MQTT
   

    publisher = None
    mqtt_adapter = None
    mqtt_available = False

    try:
        mqtt_config = MQTTConfig.from_env()

        publisher = MQTTPublisher(mqtt_config)

        mqtt_available = publisher.connect()

        if mqtt_available:
            mqtt_adapter = MQTTFactoryAdapter(publisher)

            logger.info("MQTT integration enabled.")
        else:
            logger.warning(
                "MQTT unavailable. Simulator will run in local mode."
            )

    except Exception:
        logger.exception(
            "MQTT initialization failed. Running simulator locally."
        )

        mqtt_available = False

   
    # 6. FACTORY CALLBACK
   

    def handle_reading(reading: dict):
        if mqtt_available and mqtt_adapter is not None:
            mqtt_adapter(reading)
        else:
            display_reading(reading)

   
    # 7. RUN SIMULATION
   

    try:
        logger.info("Starting MotorGuard factory simulation...")

        factory.run(
            max_cycles=5,
            on_reading=handle_reading,
        )

    except KeyboardInterrupt:
        logger.info("Shutdown requested by user.")

    finally:
        # Stop the simulator
        factory.stop()

        # Stop MQTT cleanly if it was initialized
        if publisher is not None:
            publisher.disconnect()

   
    # 8. SUMMARY
   

    if mqtt_adapter is not None:
        logger.info(
            "MQTT publication statistics: %s",
            mqtt_adapter.get_statistics(),
        )

    logger.info("Factory simulation finished.")


if __name__ == "__main__":
    main()