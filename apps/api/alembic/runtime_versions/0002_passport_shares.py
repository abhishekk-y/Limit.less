"""Consent-gated passport snapshots."""

import sqlalchemy as sa
from alembic import op

revision = "0002_passport_shares"
down_revision = "0001_runtime"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "passport_shares",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("token_hash", sa.String(64), unique=True, nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_passport_shares_tenant_id", "passport_shares", ["tenant_id"])
    op.create_index("ix_passport_shares_user_id", "passport_shares", ["user_id"])


def downgrade():
    op.drop_table("passport_shares")
