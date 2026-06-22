from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DriverSummaryOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class TruckOut(BaseModel):
    id: int
    unit_number: str
    fuel_percent: Optional[float]
    previous_fuel_percent: Optional[float]
    latitude: Optional[float]
    longitude: Optional[float]
    previous_latitude: Optional[float]
    previous_longitude: Optional[float]
    odometer_miles: Optional[float]
    speed_mph: Optional[float]
    heading_degrees: Optional[float]
    current_city: Optional[str]
    current_state: Optional[str]
    destination: Optional[str]
    active: bool
    last_samsara_update_at: Optional[datetime]
    last_samsara_sync_at: Optional[datetime]
    samsara_account_name: Optional[str]
    driver: Optional[DriverSummaryOut]

    model_config = ConfigDict(from_attributes=True)


class TruckListOut(BaseModel):
    total: int
    items: list[TruckOut]
