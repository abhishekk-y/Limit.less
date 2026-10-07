"""Initial schema — all SkillSetu X tables

Revision ID: 001_initial
Create Date: 2026-10-06
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')

    # --- Tenants ---
    op.create_table(
        'tenants',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),  # individual, organization, institution
        sa.Column('slug', sa.String(100), unique=True, nullable=False),
        sa.Column('plan', sa.String(50), server_default='free'),
        sa.Column('settings', JSONB, server_default='{}'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Users ---
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('password_hash', sa.String(255)),
        sa.Column('avatar_url', sa.String(500)),
        sa.Column('google_id', sa.String(255)),
        sa.Column('otp_secret', sa.String(64)),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('is_verified', sa.Boolean, server_default='false'),
        sa.Column('preferences', JSONB, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'])
    op.create_index('ix_users_email', 'users', ['email'])

    # --- Skills (global, no tenant_id) ---
    op.create_table(
        'skills',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('canonical_name', sa.String(255), unique=True, nullable=False),
        sa.Column('esco_id', sa.String(50)),
        sa.Column('onet_id', sa.String(50)),
        sa.Column('nco_code', sa.String(50)),
        sa.Column('nsqf_level', sa.Integer),
        sa.Column('category', sa.String(100)),
        sa.Column('aliases', JSONB, server_default='[]'),
        sa.Column('description', sa.Text),
        sa.Column('is_demo', sa.Boolean, server_default='false'),
        sa.Column('version', sa.Integer, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Skill Relations (global) ---
    op.create_table(
        'skill_relations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('source_skill_id', UUID(as_uuid=True), sa.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_skill_id', UUID(as_uuid=True), sa.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False),
        sa.Column('relation_type', sa.String(50), nullable=False),
        sa.Column('weight', sa.Float, server_default='1.0'),
        sa.Column('version', sa.Integer, server_default='1'),
    )

    # --- Roles (global) ---
    op.create_table(
        'roles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('normalized_title', sa.String(255)),
        sa.Column('onet_code', sa.String(50)),
        sa.Column('description', sa.Text),
        sa.Column('category', sa.String(100)),
        sa.Column('is_demo', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Role Skills ---
    op.create_table(
        'role_skills',
        sa.Column('role_id', UUID(as_uuid=True), sa.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('skill_id', UUID(as_uuid=True), sa.ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('importance', sa.String(20), nullable=False),
        sa.Column('typical_level', sa.Integer),
    )

    # --- Person Skills ---
    op.create_table(
        'person_skills',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('skill_id', UUID(as_uuid=True), sa.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False),
        sa.Column('claimed_level', sa.Integer),
        sa.Column('sts_score', sa.Float),
        sa.Column('sts_components', JSONB, server_default='{}'),
        sa.Column('confidence_label', sa.String(20)),
        sa.Column('freshness', sa.Float),
        sa.Column('last_evidenced_at', sa.DateTime(timezone=True)),
        sa.Column('is_verified', sa.Boolean, server_default='false'),
        sa.Column('verified_by', sa.String(50)),
        sa.Column('is_demo', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_person_skills_user', 'person_skills', ['user_id', 'tenant_id'])

    # --- Evidence ---
    op.create_table(
        'evidence',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('skill_id', UUID(as_uuid=True), sa.ForeignKey('skills.id', ondelete='CASCADE')),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('source_url', sa.String(500)),
        sa.Column('title', sa.String(255)),
        sa.Column('description', sa.Text),
        sa.Column('metadata', JSONB, server_default='{}'),
        sa.Column('integrity_score', sa.Float),
        sa.Column('integrity_flags', JSONB, server_default='[]'),
        sa.Column('is_demo', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_evidence_user', 'evidence', ['user_id', 'tenant_id'])

    # --- Opportunities ---
    op.create_table(
        'opportunities',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('organization', sa.String(255)),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('location', sa.String(255)),
        sa.Column('is_remote', sa.Boolean, server_default='false'),
        sa.Column('skills_required', JSONB, server_default='[]'),
        sa.Column('education_required', JSONB, server_default='{}'),
        sa.Column('experience_min', sa.Integer),
        sa.Column('experience_max', sa.Integer),
        sa.Column('salary_min', sa.Float),
        sa.Column('salary_max', sa.Float),
        sa.Column('deadline', sa.DateTime(timezone=True)),
        sa.Column('source', sa.String(100)),
        sa.Column('source_url', sa.String(500)),
        sa.Column('category_rules', JSONB, server_default='{}'),
        sa.Column('documents_required', JSONB, server_default='[]'),
        sa.Column('eligibility_rules', JSONB, server_default='{}'),
        sa.Column('description', sa.Text),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('is_demo', sa.Boolean, server_default='false'),
        sa.Column('posted_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_opportunities_type', 'opportunities', ['type'])
    op.create_index('ix_opportunities_deadline', 'opportunities', ['deadline'])

    # --- Applications ---
    op.create_table(
        'applications',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('opportunity_id', UUID(as_uuid=True), sa.ForeignKey('opportunities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('resume_version_id', UUID(as_uuid=True)),
        sa.Column('status', sa.String(50), server_default='draft'),
        sa.Column('match_score', sa.Float),
        sa.Column('eligibility_status', sa.String(20)),
        sa.Column('eligibility_details', JSONB, server_default='{}'),
        sa.Column('applied_at', sa.DateTime(timezone=True)),
        sa.Column('outcome', sa.String(50)),
        sa.Column('outcome_notes', sa.Text),
        sa.Column('is_demo', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_applications_user', 'applications', ['user_id', 'tenant_id'])

    # --- Resume Versions ---
    op.create_table(
        'resume_versions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('opportunity_id', UUID(as_uuid=True), sa.ForeignKey('opportunities.id')),
        sa.Column('version_number', sa.Integer, server_default='1'),
        sa.Column('content', JSONB, server_default='{}'),
        sa.Column('selected_skills', JSONB, server_default='[]'),
        sa.Column('selected_projects', JSONB, server_default='[]'),
        sa.Column('bullet_variants', JSONB, server_default='{}'),
        sa.Column('pdf_url', sa.String(500)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Vault Documents ---
    op.create_table(
        'vault_documents',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('doc_type', sa.String(50), nullable=False),
        sa.Column('file_url', sa.String(500)),
        sa.Column('encrypted_file_url', sa.String(500)),
        sa.Column('is_verified', sa.Boolean, server_default='false'),
        sa.Column('metadata', JSONB, server_default='{}'),
        sa.Column('consent_given', sa.Boolean, server_default='false'),
        sa.Column('consent_given_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Audit Log ---
    op.create_table(
        'audit_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(100)),
        sa.Column('resource_id', sa.String(100)),
        sa.Column('old_value', JSONB),
        sa.Column('new_value', JSONB),
        sa.Column('ip_address', sa.String(50)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_audit_logs_tenant', 'audit_logs', ['tenant_id', 'created_at'])

    # --- Notifications ---
    op.create_table(
        'notifications',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(50)),
        sa.Column('title', sa.String(255)),
        sa.Column('body', sa.Text),
        sa.Column('channel', sa.String(20), server_default='in_app'),
        sa.Column('is_read', sa.Boolean, server_default='false'),
        sa.Column('metadata', JSONB, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Consent Records ---
    op.create_table(
        'consent_records',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('purpose', sa.String(100), nullable=False),
        sa.Column('granted', sa.Boolean, nullable=False),
        sa.Column('granted_at', sa.DateTime(timezone=True)),
        sa.Column('revoked_at', sa.DateTime(timezone=True)),
        sa.Column('ip_address', sa.String(50)),
    )

    # --- Subscriptions ---
    op.create_table(
        'subscriptions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('plan', sa.String(50), server_default='free'),
        sa.Column('razorpay_subscription_id', sa.String(255)),
        sa.Column('status', sa.String(50), server_default='active'),
        sa.Column('features', JSONB, server_default='{}'),
        sa.Column('usage', JSONB, server_default='{}'),
        sa.Column('trial_ends_at', sa.DateTime(timezone=True)),
        sa.Column('current_period_start', sa.DateTime(timezone=True)),
        sa.Column('current_period_end', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- API Keys ---
    op.create_table(
        'api_keys',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('key_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(100)),
        sa.Column('permissions', JSONB, server_default='[]'),
        sa.Column('rate_limit', sa.Integer, server_default='100'),
        sa.Column('usage_count', sa.Integer, server_default='0'),
        sa.Column('last_used_at', sa.DateTime(timezone=True)),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Skill Missions (global) ---
    op.create_table(
        'skill_missions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('skills_targeted', JSONB, server_default='[]'),
        sa.Column('difficulty', sa.String(20)),
        sa.Column('estimated_hours', sa.Float),
        sa.Column('checklist', JSONB, server_default='[]'),
        sa.Column('project_template', JSONB, server_default='{}'),
        sa.Column('is_demo', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Org Employees ---
    op.create_table(
        'org_employees',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_id', sa.String(100)),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('role_title', sa.String(255)),
        sa.Column('department', sa.String(100)),
        sa.Column('skills', JSONB, server_default='[]'),
        sa.Column('skill_levels', JSONB, server_default='{}'),
        sa.Column('experience_years', sa.Float),
        sa.Column('is_demo', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- RLS Policies ---
    tenant_tables = [
        'users', 'person_skills', 'evidence', 'applications',
        'resume_versions', 'vault_documents', 'audit_logs',
        'notifications', 'consent_records', 'org_employees',
    ]
    for table in tenant_tables:
        op.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY')
        op.execute(
            f"CREATE POLICY tenant_isolation_{table} ON {table} "
            f"USING (tenant_id = current_setting('app.current_tenant_id')::uuid)"
        )


def downgrade() -> None:
    tables = [
        'org_employees', 'skill_missions', 'api_keys', 'subscriptions',
        'consent_records', 'notifications', 'audit_logs', 'vault_documents',
        'resume_versions', 'applications', 'opportunities', 'evidence',
        'person_skills', 'role_skills', 'roles', 'skill_relations',
        'skills', 'users', 'tenants',
    ]
    for table in tables:
        op.drop_table(table)
    op.execute('DROP EXTENSION IF EXISTS "vector"')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
