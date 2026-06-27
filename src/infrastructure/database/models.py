from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class TenantModel(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    users: Mapped[list[UserModel]] = relationship(back_populates="tenant", lazy="selectin")


class UserModel(Base):
    __tablename__ = "api_users"

    id: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(Uuid, ForeignKey("tenants.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()", onupdate="now()"
    )

    tenant: Mapped[TenantModel] = relationship(back_populates="users", lazy="joined")


class DataProcessingActivityModel(Base):
    __tablename__ = "data_processing_activities"
    __table_args__ = (
        Index("idx_activities_status", "tenant_id", "status"),
    )

    id: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(Uuid, ForeignKey("tenants.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    purpose: Mapped[str] = mapped_column(String(255), nullable=False)
    system_name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_user_id: Mapped[str | None] = mapped_column(
        Uuid, ForeignKey("api_users.id"), nullable=True
    )
    operator_role: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT")
    localization_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="UNKNOWN"
    )
    retention_policy_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cross_border_transfer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()", onupdate="now()"
    )

    legal_bases: Mapped[list[LegalBasisRecordModel]] = relationship(
        back_populates="activity", lazy="selectin", cascade="all, delete-orphan"
    )
    transfers: Mapped[list[TransferRecordModel]] = relationship(
        back_populates="activity", lazy="selectin", cascade="all, delete-orphan"
    )
    localization_assessments: Mapped[list[LocalizationAssessmentModel]] = relationship(
        back_populates="activity", lazy="selectin", cascade="all, delete-orphan"
    )


class LegalBasisRecordModel(Base):
    __tablename__ = "legal_basis_records"

    id: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid4)
    activity_id: Mapped[str] = mapped_column(
        Uuid, ForeignKey("data_processing_activities.id", ondelete="CASCADE"), nullable=False
    )
    basis_type: Mapped[str] = mapped_column(String(64), nullable=False)
    basis_reference: Mapped[str] = mapped_column(Text, nullable=False)
    consent_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    activity: Mapped[DataProcessingActivityModel] = relationship(
        back_populates="legal_bases", lazy="joined"
    )


class ConsentTemplateModel(Base):
    __tablename__ = "consent_templates"
    __table_args__ = (
        Index("uq_template_version", "tenant_id", "name", "version", unique=True),
    )

    id: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(Uuid, ForeignKey("tenants.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    language_code: Mapped[str] = mapped_column(String(8), default="ru", nullable=False)
    channel: Mapped[str] = mapped_column(String(64), nullable=False)
    text_body: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )


class ConsentCaptureModel(Base):
    __tablename__ = "consent_captures"
    __table_args__ = (
        Index("idx_consents_status", "status", "captured_at"),
    )

    id: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(Uuid, ForeignKey("tenants.id"), nullable=False)
    subject_identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    template_id: Mapped[str] = mapped_column(
        Uuid, ForeignKey("consent_templates.id"), nullable=False
    )
    activity_id: Mapped[str | None] = mapped_column(
        Uuid, ForeignKey("data_processing_activities.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    withdrawn_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    source_channel: Mapped[str] = mapped_column(String(64), nullable=False)
    proof_payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    template: Mapped[ConsentTemplateModel] = relationship(lazy="joined")


class DataSubjectRequestModel(Base):
    __tablename__ = "data_subject_requests"
    __table_args__ = (
        Index("idx_dsr_due", "status", "due_at"),
    )

    id: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(Uuid, ForeignKey("tenants.id"), nullable=False)
    request_type: Mapped[str] = mapped_column(String(64), nullable=False)
    subject_identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN")
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    assigned_user_id: Mapped[str | None] = mapped_column(
        Uuid, ForeignKey("api_users.id"), nullable=True
    )
    response_payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    evidence_payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class TransferRecordModel(Base):
    __tablename__ = "transfer_records"
    __table_args__ = (
        Index("idx_transfers_risk", "risk_level", "blocked"),
    )

    id: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid4)
    activity_id: Mapped[str] = mapped_column(
        Uuid, ForeignKey("data_processing_activities.id", ondelete="CASCADE"), nullable=False
    )
    destination_country: Mapped[str] = mapped_column(String(2), nullable=False)
    recipient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    transfer_purpose: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(32), nullable=False)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    activity: Mapped[DataProcessingActivityModel] = relationship(
        back_populates="transfers", lazy="joined"
    )


class LocalizationAssessmentModel(Base):
    __tablename__ = "localization_assessments"

    id: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid4)
    activity_id: Mapped[str] = mapped_column(
        Uuid, ForeignKey("data_processing_activities.id", ondelete="CASCADE"), nullable=False
    )
    first_write_in_russia: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    processor_localization_supported: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    evidence_payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    activity: Mapped[DataProcessingActivityModel] = relationship(
        back_populates="localization_assessments", lazy="joined"
    )


class ProcessorVendorModel(Base):
    __tablename__ = "processor_vendors"

    id: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(Uuid, ForeignKey("tenants.id"), nullable=False)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    inn: Mapped[str | None] = mapped_column(String(12), nullable=True)
    service_type: Mapped[str] = mapped_column(String(128), nullable=False)
    hosts_personal_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    subprocessors_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT")
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    reviews: Mapped[list[ProcessorReviewModel]] = relationship(
        back_populates="vendor", lazy="selectin", cascade="all, delete-orphan"
    )


class ProcessorReviewModel(Base):
    __tablename__ = "processor_reviews"

    id: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid4)
    vendor_id: Mapped[str] = mapped_column(
        Uuid, ForeignKey("processor_vendors.id", ondelete="CASCADE"), nullable=False
    )
    review_status: Mapped[str] = mapped_column(String(32), nullable=False)
    risk_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    localization_supported: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dpa_present: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    questionnaire_payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    evidence_payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    reviewer_id: Mapped[str | None] = mapped_column(
        Uuid, ForeignKey("api_users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    vendor: Mapped[ProcessorVendorModel] = relationship(
        back_populates="reviews", lazy="joined"
    )


class PrivacyIncidentModel(Base):
    __tablename__ = "privacy_incidents"
    __table_args__ = (
        Index("idx_incidents_status", "status", "severity"),
    )

    id: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(Uuid, ForeignKey("tenants.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN")
    system_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reported_by: Mapped[str | None] = mapped_column(
        Uuid, ForeignKey("api_users.id"), nullable=True
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    remediation_owner_id: Mapped[str | None] = mapped_column(
        Uuid, ForeignKey("api_users.id"), nullable=True
    )
    timeline_payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class EvidenceItemModel(Base):
    __tablename__ = "evidence_items"

    id: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(Uuid, ForeignKey("tenants.id"), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str] = mapped_column(Uuid, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_by: Mapped[str | None] = mapped_column(
        Uuid, ForeignKey("api_users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )


class AuditEventModel(Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        Index("idx_audit_resource", "resource_type", "resource_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(Uuid, ForeignKey("tenants.id"), nullable=False)
    actor_user_id: Mapped[str | None] = mapped_column(
        Uuid, ForeignKey("api_users.id"), nullable=True
    )
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str] = mapped_column(Uuid, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
