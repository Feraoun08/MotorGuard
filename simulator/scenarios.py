
from dataclasses import dataclass
from enum import Enum

from simulator.config import BEARING_CONDITIONS


class ScenarioType(str, Enum):
    HEALTHY = "healthy"
    BALL_FAULT = "ball_fault"
    INNER_RACE_FAULT = "inner_race_fault"
    OUTER_RACE_FAULT = "outer_race_fault"


@dataclass(frozen=True)
class FaultScenario:
    name: str
    scenario_type: ScenarioType
    bearing_condition: str
    description: str


SCENARIOS = {
    "healthy": FaultScenario(
        name="Healthy operation",
        scenario_type=ScenarioType.HEALTHY,
        bearing_condition="Normal_1",
        description="Motor operates with healthy bearing observations.",
    ),

    "ball_007": FaultScenario(
        name="Ball defect - 0.007 inch",
        scenario_type=ScenarioType.BALL_FAULT,
        bearing_condition="Ball_007_1",
        description="Simulates observations associated with a ball defect.",
    ),

    "ball_014": FaultScenario(
        name="Ball defect - 0.014 inch",
        scenario_type=ScenarioType.BALL_FAULT,
        bearing_condition="Ball_014_1",
        description="Simulates observations associated with a larger ball defect.",
    ),

    "ball_021": FaultScenario(
        name="Ball defect - 0.021 inch",
        scenario_type=ScenarioType.BALL_FAULT,
        bearing_condition="Ball_021_1",
        description="Simulates observations associated with a larger ball defect.",
    ),

    "inner_007": FaultScenario(
        name="Inner race defect - 0.007 inch",
        scenario_type=ScenarioType.INNER_RACE_FAULT,
        bearing_condition="IR_007_1",
        description="Simulates observations associated with an inner race defect.",
    ),

    "inner_014": FaultScenario(
        name="Inner race defect - 0.014 inch",
        scenario_type=ScenarioType.INNER_RACE_FAULT,
        bearing_condition="IR_014_1",
        description="Simulates observations associated with an inner race defect.",
    ),

    "inner_021": FaultScenario(
        name="Inner race defect - 0.021 inch",
        scenario_type=ScenarioType.INNER_RACE_FAULT,
        bearing_condition="IR_021_1",
        description="Simulates observations associated with an inner race defect.",
    ),

    "outer_007": FaultScenario(
        name="Outer race defect - 0.007 inch",
        scenario_type=ScenarioType.OUTER_RACE_FAULT,
        bearing_condition="OR_007_6_1",
        description="Simulates observations associated with an outer race defect.",
    ),

    "outer_014": FaultScenario(
        name="Outer race defect - 0.014 inch",
        scenario_type=ScenarioType.OUTER_RACE_FAULT,
        bearing_condition="OR_014_6_1",
        description="Simulates observations associated with an outer race defect.",
    ),

    "outer_021": FaultScenario(
        name="Outer race defect - 0.021 inch",
        scenario_type=ScenarioType.OUTER_RACE_FAULT,
        bearing_condition="OR_021_6_1",
        description="Simulates observations associated with an outer race defect.",
    ),
}


def get_scenario(scenario_name: str) -> FaultScenario:
    """Return a scenario by its configured name."""

    if scenario_name not in SCENARIOS:
        available = ", ".join(SCENARIOS.keys())

        raise ValueError(
            f"Unknown scenario '{scenario_name}'. "
            f"Available scenarios: {available}"
        )

    scenario = SCENARIOS[scenario_name]

    if scenario.bearing_condition not in BEARING_CONDITIONS:
        raise ValueError(
            f"Scenario references invalid bearing condition: "
            f"{scenario.bearing_condition}"
        )

    return scenario


def list_scenarios() -> list[FaultScenario]:
    """Return all available scenarios."""

    return list(SCENARIOS.values())


def apply_scenario(motor, scenario_name: str):
    """
    Change a motor's configured bearing scenario.

    This is a controlled simulation change, not a physical
    degradation model.
    """

    scenario = get_scenario(scenario_name)

    motor.config.bearing_condition = scenario.bearing_condition

    return scenario
