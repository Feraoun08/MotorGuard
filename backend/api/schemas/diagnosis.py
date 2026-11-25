from datetime import datetime

from pydantic import BaseModel


class DiagnosisResponse(BaseModel):
    factory_id: str
    line_id: str
    motor_id: str

    timestamp: datetime

    predicted_class: str
    confidence: float | None = None

    ground_truth: str | None = None
    is_simulated: bool | None = None