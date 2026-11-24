from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MaintenanceCreate(BaseModel):
    maintenance_type: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str = Field(
        min_length=1,
        max_length=2000,
    )

    performed_at: datetime


class MaintenanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    factory_id: str
    motor_id: str
    maintenance_type: str
    description: str
    performed_at: datetime
    created_at: datetime