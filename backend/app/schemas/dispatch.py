from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.fuel_dispatch import FuelDispatchStatus


class DispatchAssignIn(BaseModel):
    truck_id: int
    station_id: int


class DispatchCancelIn(BaseModel):
    truck_id: int


class DispatchOut(BaseModel):
    id: int
    truck_id: int
    station_id: int
    status: FuelDispatchStatus
    assigned_at: datetime
    completed_at: Optional[datetime]
    missed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    last_distance_to_station_miles: Optional[float]
    minimum_distance_to_station_miles: Optional[float]

    model_config = ConfigDict(from_attributes=True)
