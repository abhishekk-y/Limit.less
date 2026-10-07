"""Persist shared provider request budgets."""

import sqlalchemy as sa
from alembic import op

revision = "0003_provider_daily_usage"
down_revision = "0002_passport_shares"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "provider_daily_usage",
        sa.Column("provider", sa.String(40), primary_key=True),
        sa.Column("usage_day", sa.String(10), primary_key=True),
        sa.Column("calls", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade():
    op.drop_table("provider_daily_usage")
