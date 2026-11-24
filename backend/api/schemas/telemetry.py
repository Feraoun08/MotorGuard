
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TelemetryResponse(BaseModel):
    factory_id: str
    line_id: str
    motor_id: str
    timestamp: datetime

    motor_state: str | None = None
    bearing_condition: str | None = None
    ground_truth: str | None = None
    is_simulated: bool | None = None

    vibration: dict[str, float] = Field(default_factory=dict)
    sensors: dict[str, float] = Field(default_factory=dict)
    additional_tags: dict[str, Any] = Field(default_factory=dict)


class TelemetryHistoryResponse(BaseModel):
    factory_id: str
    motor_id: str
    start: datetime
    end: datetime
    count: int
    limit: int
    items: list[TelemetryResponse] = Field(default_factory=list)
