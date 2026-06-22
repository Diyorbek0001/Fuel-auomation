from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import utcnow


class TruckStateHistory(Base):
    __tablename__ = "truck_state_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    truck_id: Mapped[int] = mapped_column(ForeignKey("trucks.id"), index=True)
    fuel_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    odometer_miles: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    speed_mph: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    distance_to_active_dispatch_miles: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    truck: Mapped["Truck"] = relationship()
