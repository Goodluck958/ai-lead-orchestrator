from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class UserRole(str, Enum):
    CLIENT = "client"
    ADMIN = "admin"


class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"


class PipelineRunStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AuditEventType(str, Enum):
    USER_REGISTERED = "user_registered"
    USER_LOGIN = "user_login"
    RESEARCH_STARTED = "research_started"
    RESEARCH_COMPLETED = "research_completed"
    LEAD_QUALIFIED = "lead_qualified"
    MESSAGE_GENERATED = "message_generated"
    MESSAGE_APPROVED = "message_approved"
    MESSAGE_REJECTED = "message_rejected"
    MESSAGE_SENT = "message_sent"
    PIPELINE_FAILED = "pipeline_failed"


class User(Base):
    """
    Persistent LEADFORGE user account.

    A user owns their leads and pipeline runs.
    Admin users can access authorized system-wide monitoring.
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        SQLAlchemyEnum(UserRole),
        default=UserRole.CLIENT,
        nullable=False,
    )

    status: Mapped[UserStatus] = mapped_column(
        SQLAlchemyEnum(UserStatus),
        default=UserStatus.ACTIVE,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    leads: Mapped[list["LeadRecord"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    pipeline_runs: Mapped[list["PipelineRun"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    audit_events: Mapped[list["AuditEvent"]] = relationship(
        back_populates="user",
    )


class LeadRecord(Base):
    """
    Persistent lead belonging to a specific LEADFORGE user.
    """

    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    contact_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    contact_email: Mapped[Optional[str]] = mapped_column(
        String(320),
        nullable=True,
    )

    website: Mapped[Optional[str]] = mapped_column(
        String(2048),
        nullable=True,
    )

    industry: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    qualification_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    qualification_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    personalized_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="discovered",
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    owner: Mapped["User"] = relationship(
        back_populates="leads",
    )

    pipeline_run_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("pipeline_runs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    pipeline_run: Mapped[Optional["PipelineRun"]] = relationship(
        back_populates="leads",
    )

    approval: Mapped[Optional["Approval"]] = relationship(
        back_populates="lead",
        uselist=False,
        cascade="all, delete-orphan",
    )


class PipelineRun(Base):
    """
    Records one execution of the LEADFORGE pipeline.
    """

    __tablename__ = "pipeline_runs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    industry: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    max_leads: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[PipelineRunStatus] = mapped_column(
        SQLAlchemyEnum(PipelineRunStatus),
        default=PipelineRunStatus.RUNNING,
        nullable=False,
        index=True,
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    owner: Mapped["User"] = relationship(
        back_populates="pipeline_runs",
    )

    leads: Mapped[list["LeadRecord"]] = relationship(
        back_populates="pipeline_run",
    )


class Approval(Base):
    """
    Human approval record for AI-generated outreach.
    """

    __tablename__ = "approvals"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    lead_id: Mapped[str] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    status: Mapped[ApprovalStatus] = mapped_column(
        SQLAlchemyEnum(ApprovalStatus),
        default=ApprovalStatus.PENDING,
        nullable=False,
        index=True,
    )

    reviewed_by: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    rejection_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    lead: Mapped["LeadRecord"] = relationship(
        back_populates="approval",
    )


class AuditEvent(Base):
    """
    Immutable-style record of important system activity.
    """

    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    event_type: Mapped[AuditEventType] = mapped_column(
        SQLAlchemyEnum(AuditEventType),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    user: Mapped[Optional["User"]] = relationship(
        back_populates="audit_events",
    )


Index(
    "ix_leads_owner_status",
    LeadRecord.owner_id,
    LeadRecord.status,
)

Index(
    "ix_pipeline_runs_owner_status",
    PipelineRun.owner_id,
    PipelineRun.status,
  )
