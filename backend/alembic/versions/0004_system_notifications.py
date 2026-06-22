"""allow system notifications

Revision ID: 0004_system_notifications
Revises: 0003_live_samsara_events
Create Date: 2026-06-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_system_notifications"
down_revision: Union[str, None] = "0003_live_samsara_events"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("notification_events") as batch_op:
        batch_op.alter_column("truck_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("notification_events") as batch_op:
        batch_op.alter_column("truck_id", existing_type=sa.Integer(), nullable=False)
