"""Persistent career journey and workspace schema.

Revision ID: 0001_runtime
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_runtime"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "workspaces",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("type", sa.String(32), nullable=False),
        sa.Column("plan", sa.String(32), nullable=False),
        sa.Column("is_demo", sa.Boolean(), nullable=False),
    )
    op.create_table(
        "accounts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(40), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("profile", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_accounts_tenant_id", "accounts", ["tenant_id"])
    op.create_table(
        "workspace_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("kind", sa.String(40), nullable=False),
        sa.Column("key", sa.String(160), nullable=False),
        sa.Column("data", sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "user_id", "kind", "key", name="uq_record_owner_key"),
    )
    for column in ("tenant_id", "user_id", "kind"):
        op.create_index(f"ix_workspace_records_{column}", "workspace_records", [column])
    op.create_table(
        "refresh_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("family", sa.String(36), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    for column in ("user_id", "family"):
        op.create_index(f"ix_refresh_sessions_{column}", "refresh_sessions", [column])
    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_events_tenant_id", "audit_events", ["tenant_id"])
    if op.get_bind().dialect.name == "postgresql":
        # Authentication tables are accessed by the trusted auth service; all
        # private workspace records additionally enforce transaction-local RLS.
        op.execute("ALTER TABLE workspace_records ENABLE ROW LEVEL SECURITY")
        op.execute("ALTER TABLE workspace_records FORCE ROW LEVEL SECURITY")
        op.execute(
            "CREATE POLICY tenant_records ON workspace_records USING (tenant_id = current_setting('app.current_tenant_id', true)) WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true))"
        )


def downgrade():
    for table in ("audit_events", "refresh_sessions", "workspace_records", "accounts", "workspaces"):
        op.drop_table(table)
