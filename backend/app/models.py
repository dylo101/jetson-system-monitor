from datetime import datetime

from pydantic import BaseModel, Field


class MetricSample(BaseModel):
    timestamp: datetime
    cpu_percent: float = Field(ge=0, le=100)
    memory_percent: float = Field(ge=0, le=100)
    disk_percent: float = Field(ge=0, le=100)
    uptime_seconds: float = Field(ge=0)
    temperature_c: float | None = None
