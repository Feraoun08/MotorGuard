from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FactoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    created_at: datetime


class ProductionLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    factory_id: str
    id: str
    name: str


class MotorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    factory_id: str
    id: str
    line_id: str
    name: str
    created_at: datetime


class MotorListResponse(BaseModel):
    items: list[MotorResponse]
    total: int
    limit: int
    offset: int