"""add live samsara event state

Revision ID: 0003_live_samsara_events
Revises: 0002_notification_events
Create Date: 2026-06-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_live_samsara_events"
down_revision: Union[str, None] = "0002_notification_events"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("trucks", sa.Column("previous_fuel_percent", sa.Float(), nullable=True))
    op.add_column("trucks", sa.Column("previous_latitude", sa.Float(), nullable=True))
    op.add_column("trucks", sa.Column("previous_longitude", sa.Float(), nullable=True))
    op.add_column("trucks", sa.Column("speed_mph", sa.Float(), nullable=True))
    op.add_column("trucks", sa.Column("heading_degrees", sa.Float(), nullable=True))
    op.add_column("trucks", sa.Column("last_samsara_update_at", sa.DateTime(timezone=True), nullable=True))

    op.add_column("fuel_dispatches", sa.Column("pre_alert_sent_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("fuel_dispatches", sa.Column("final_alert_sent_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("fuel_dispatches", sa.Column("arrived_alert_sent_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("fuel_dispatches", sa.Column("missed_alert_sent_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("fuel_dispatches", sa.Column("last_distance_to_station_miles", sa.Float(), nullable=True))
    op.add_column("fuel_dispatches", sa.Column("minimum_distance_to_station_miles", sa.Float(), nullable=True))

    op.add_column("notification_events", sa.Column("channel", sa.String(length=64), nullable=False, server_default="frontend"))
    op.add_column("notification_events", sa.Column("sent_to", sa.String(length=255), nullable=True))
    op.add_column("notification_events", sa.Column("dedupe_key", sa.String(length=255), nullable=True))
    op.create_index(op.f("ix_notification_events_channel"), "notification_events", ["channel"])
    op.create_index(op.f("ix_notification_events_dedupe_key"), "notification_events", ["dedupe_key"], unique=True)

    op.create_table(
        "samsara_sync_state",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("feed_name", sa.String(length=128), nullable=False),
        sa.Column("end_cursor", sa.Text(), nullable=True),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_message", sa.Text(), nullable=True),
    )
    op.create_index(op.f("ix_samsara_sync_state_feed_name"), "samsara_sync_state", ["feed_name"], unique=True)

    op.create_table(
        "truck_state_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("truck_id", sa.Integer(), nullable=False),
        sa.Column("fuel_percent", sa.Float(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("odometer_miles", sa.Float(), nullable=True),
        sa.Column("speed_mph", sa.Float(), nullable=True),
        sa.Column("distance_to_active_dispatch_miles", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["truck_id"], ["trucks.id"]),
    )
    op.create_index(op.f("ix_truck_state_history_truck_id"), "truck_state_history", ["truck_id"])
    op.create_index(op.f("ix_truck_state_history_created_at"), "truck_state_history", ["created_at"])


def downgrade() -> None:
    op.drop_table("truck_state_history")
    op.drop_table("samsara_sync_state")
    op.drop_index(op.f("ix_notification_events_dedupe_key"), table_name="notification_events")
    op.drop_index(op.f("ix_notification_events_channel"), table_name="notification_events")
    op.drop_column("notification_events", "dedupe_key")
    op.drop_column("notification_events", "sent_to")
    op.drop_column("notification_events", "channel")
    op.drop_column("fuel_dispatches", "minimum_distance_to_station_miles")
    op.drop_column("fuel_dispatches", "last_distance_to_station_miles")
    op.drop_column("fuel_dispatches", "missed_alert_sent_at")
    op.drop_column("fuel_dispatches", "arrived_alert_sent_at")
    op.drop_column("fuel_dispatches", "final_alert_sent_at")
    op.drop_column("fuel_dispatches", "pre_alert_sent_at")
    op.drop_column("trucks", "last_samsara_update_at")
    op.drop_column("trucks", "heading_degrees")
    op.drop_column("trucks", "speed_mph")
    op.drop_column("trucks", "previous_longitude")
    op.drop_column("trucks", "previous_latitude")
    op.drop_column("trucks", "previous_fuel_percent")
