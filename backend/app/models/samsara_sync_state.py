from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SamsaraSyncState(Base):
    __tablename__ = "samsara_sync_state"

    id: Mapped[int] = mapped_column(primary_key=True)
    feed_name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    end_cursor: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_success_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
