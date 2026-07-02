from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("inn", sa.String(12), nullable=True),
        sa.Column("domain", sa.String(255), nullable=True),
        sa.Column("settings", postgresql.JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "api_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(64), nullable=False, server_default="viewer"),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true"), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_api_users_tenant_id", "api_users", ["tenant_id"])
    op.create_index("ix_api_users_email", "api_users", ["email"], unique=True)

    op.create_table(
        "data_processing_activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("purpose", sa.Text, nullable=False),
        sa.Column("legal_basis_summary", sa.Text, nullable=True),
        sa.Column("data_categories", postgresql.JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("subject_categories", postgresql.JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("storage_location", sa.String(255), nullable=True),
        sa.Column("retention_days", sa.Integer, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="DRAFT"),
        sa.Column("risk_level", sa.String(50), nullable=True),
        sa.Column("dpo_comment", sa.Text, nullable=True),
        sa.Column("metadata_", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_dpa_tenant_id", "data_processing_activities", ["tenant_id"])
    op.create_index("ix_dpa_status", "data_processing_activities", ["status"])

    op.create_table(
        "legal_basis_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("activity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("data_processing_activities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("basis_type", sa.String(50), nullable=False),
        sa.Column("article_reference", sa.String(100), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("valid_from", sa.Date, nullable=True),
        sa.Column("valid_to", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_lbr_activity_id", "legal_basis_records", ["activity_id"])

    op.create_table(
        "consent_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("purpose", sa.Text, nullable=False),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("body_ru", sa.Text, nullable=False),
        sa.Column("body_en", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true"), nullable=False),
        sa.Column("metadata_", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_ct_tenant_id", "consent_templates", ["tenant_id"])

    op.create_table(
        "consent_captures",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("consent_templates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject_identifier", sa.String(500), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
        sa.Column("given_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("channel", sa.String(100), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("metadata_", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_cc_tenant_id", "consent_captures", ["tenant_id"])
    op.create_index("ix_cc_template_id", "consent_captures", ["template_id"])
    op.create_index("ix_cc_subject", "consent_captures", ["subject_identifier"])

    op.create_table(
        "data_subject_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("request_type", sa.String(64), nullable=False),
        sa.Column("subject_identifier", sa.String(255), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="OPEN"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("assigned_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_users.id"), nullable=True),
        sa.Column("response_payload", postgresql.JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("evidence_payload", postgresql.JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_dsr_tenant_id", "data_subject_requests", ["tenant_id"])
    op.create_index("ix_dsr_status", "data_subject_requests", ["status"])
    op.create_index("idx_dsr_due", "data_subject_requests", ["status", "due_at"])

    op.create_table(
        "transfer_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("activity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("data_processing_activities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("destination_country", sa.String(3), nullable=False),
        sa.Column("destination_org", sa.String(500), nullable=True),
        sa.Column("transfer_mechanism", sa.String(100), nullable=True),
        sa.Column("risk_level", sa.String(50), nullable=True),
        sa.Column("metadata_", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_tr_activity_id", "transfer_records", ["activity_id"])

    op.create_table(
        "localization_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("activity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("data_processing_activities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("primary_db_location", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="PENDING"),
        sa.Column("evidence_ids", postgresql.JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("assessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_la_activity_id", "localization_assessments", ["activity_id"])

    op.create_table(
        "processor_vendors",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("legal_name", sa.String(500), nullable=False),
        sa.Column("inn", sa.String(12), nullable=True),
        sa.Column("service_type", sa.String(255), nullable=True),
        sa.Column("hosts_personal_data", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("subprocessors_used", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="PENDING"),
        sa.Column("metadata_", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_pv_tenant_id", "processor_vendors", ["tenant_id"])

    op.create_table(
        "processor_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("processor_vendors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("review_status", sa.String(50), nullable=False),
        sa.Column("risk_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("localization_supported", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("dpa_present", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("questionnaire_payload", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("evidence_payload", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_pr_vendor_id", "processor_reviews", ["vendor_id"])

    op.create_table(
        "privacy_incidents",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("severity", sa.String(50), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="DETECTED"),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("roskomnadzor_notified", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("metadata_", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_pi_tenant_id", "privacy_incidents", ["tenant_id"])
    op.create_index("ix_pi_severity", "privacy_incidents", ["severity"])

    op.create_table(
        "evidence_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_name", sa.String(500), nullable=False),
        sa.Column("file_type", sa.String(100), nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger, nullable=True),
        sa.Column("storage_path", sa.Text, nullable=False),
        sa.Column("sha256_hash", sa.String(64), nullable=True),
        sa.Column("metadata_", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_ei_tenant_id", "evidence_items", ["tenant_id"])
    op.create_index("ix_ei_resource", "evidence_items", ["resource_type", "resource_id"])

    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(255), nullable=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("payload", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_ae_tenant_id", "audit_events", ["tenant_id"])
    op.create_index("ix_ae_resource", "audit_events", ["resource_type", "resource_id"])
    op.create_index("ix_ae_created_at", "audit_events", ["created_at"])

    op.create_table(
        "retention_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("data_category", sa.String(255), nullable=False),
        sa.Column("retention_days", sa.Integer, nullable=False),
        sa.Column("legal_reference", sa.String(255), nullable=True),
        sa.Column("auto_delete", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_rp_tenant_id", "retention_policies", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("retention_policies")
    op.drop_table("audit_events")
    op.drop_table("evidence_items")
    op.drop_table("privacy_incidents")
    op.drop_table("processor_reviews")
    op.drop_table("processor_vendors")
    op.drop_table("localization_assessments")
    op.drop_table("transfer_records")
    op.drop_table("data_subject_requests")
    op.drop_table("consent_captures")
    op.drop_table("consent_templates")
    op.drop_table("legal_basis_records")
    op.drop_table("data_processing_activities")
    op.drop_table("users")
    op.drop_table("tenants")
