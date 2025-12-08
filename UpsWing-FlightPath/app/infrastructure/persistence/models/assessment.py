import uuid
from enum import Enum
from decimal import Decimal
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import (
    String,
    Integer,
    Boolean,
    Text,
    DECIMAL,
    TIMESTAMP,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
    CHAR,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.infrastructure.persistence.base import Base
if TYPE_CHECKING:
    from app.infrastructure.persistence.models.learning import LearningPathway



class AssessmentType(str, Enum):
    PLACEMENT = "PLACEMENT"
    SPEAKING = "SPEAKING"
    WRITING = "WRITING"

class TestTakerType(str, Enum):
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    ADMIN = "ADMIN"

class AssignmentStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class SessionStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class ResultType(str, Enum):
    PLACEMENT = "P"
    SPEAKING = "S"
    WRITING = "W"

class ActorType(str, Enum):
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    ADMIN = "ADMIN"
    SYSTEM = "SYSTEM"


def new_uuid() -> str:
    return str(uuid.uuid4())



class AssessmentTemplate(Base):
    __tablename__ = "assessment_template"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=new_uuid)
    learning_pathway_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("learning_pathway.id"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    assessment_type: Mapped[AssessmentType] = mapped_column(SQLEnum(AssessmentType), nullable=False)
    rubric: Mapped[Optional[dict]] = mapped_column(JSON)
    meta: Mapped[Optional[dict]] = mapped_column(JSON)
    version: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    published_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    created_by: Mapped[Optional[str]] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    learning_pathway: Mapped["LearningPathway"] = relationship("LearningPathway", back_populates="assessment_templates")
    template_items: Mapped[List["TemplateItem"]] = relationship("TemplateItem", back_populates="template", cascade="all, delete-orphan")
    configs: Mapped[List["AssessmentConfig"]] = relationship("AssessmentConfig", back_populates="template")
    assignments: Mapped[List["AssignedAssessment"]] = relationship("AssignedAssessment", back_populates="template")


class TemplateItem(Base):
    __tablename__ = "template_item"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=new_uuid)
    template_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("assessment_template.id"))
    item_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("assessment_item.id"))
    item_order: Mapped[Optional[int]] = mapped_column(Integer)
    item_meta: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    template: Mapped["AssessmentTemplate"] = relationship("AssessmentTemplate", back_populates="template_items")
    item: Mapped["AssessmentItem"] = relationship("AssessmentItem", back_populates="template_items")


class AssessmentConfig(Base):
    __tablename__ = "assessment_config"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=new_uuid)
    template_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("assessment_template.id"))
    parameters: Mapped[Optional[dict]] = mapped_column(JSON)
    adaptive_params: Mapped[Optional[dict]] = mapped_column(JSON)
    speaking_params: Mapped[Optional[dict]] = mapped_column(JSON)
    writing_params: Mapped[Optional[dict]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    template: Mapped["AssessmentTemplate"] = relationship("AssessmentTemplate", back_populates="configs")


class AssessmentItem(Base):
    __tablename__ = "assessment_item"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=new_uuid)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    item_type: Mapped[str] = mapped_column(String(50))
    skill_area: Mapped[list] = mapped_column(JSON)
    target_proficiency_level: Mapped[str] = mapped_column(String(15))
    parameters: Mapped[dict] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    template_items: Mapped[List["TemplateItem"]] = relationship("TemplateItem", back_populates="item")
    responses: Mapped[List["AssessmentResponse"]] = relationship("AssessmentResponse", back_populates="item")



class AssignedAssessment(Base):
    __tablename__ = "assigned_assessment"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=new_uuid)
    template_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("assessment_template.id"))
    test_taker_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    test_taker_type: Mapped[TestTakerType] = mapped_column(SQLEnum(TestTakerType), nullable=False)
    assigned_by: Mapped[Optional[str]] = mapped_column(String(50))
    assigned_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    due_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    status: Mapped[AssignmentStatus] = mapped_column(SQLEnum(AssignmentStatus), nullable=False, default=AssignmentStatus.PENDING, index=True)
    notes: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    template: Mapped["AssessmentTemplate"] = relationship("AssessmentTemplate", back_populates="assignments")
    sessions: Mapped[List["AssessmentSession"]] = relationship("AssessmentSession", back_populates="assignment", cascade="all, delete-orphan")


class AssessmentSession(Base):
    __tablename__ = "assessment_session"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=new_uuid)
    assigned_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("assigned_assessment.id"))
    current_ability: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(8, 4))
    standard_error: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(8, 4))
    questions_answered: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[SessionStatus] = mapped_column(SQLEnum(SessionStatus), nullable=False, default=SessionStatus.IN_PROGRESS, index=True)
    current_index: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    rubric_snapshot: Mapped[Optional[dict]] = mapped_column(JSON)
    template_snapshot: Mapped[Optional[dict]] = mapped_column(JSON)
    started_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    assignment: Mapped["AssignedAssessment"] = relationship("AssignedAssessment", back_populates="sessions")
    responses: Mapped[List["AssessmentResponse"]] = relationship("AssessmentResponse", back_populates="session", cascade="all, delete-orphan")
    results: Mapped[List["Result"]] = relationship("Result", back_populates="session", cascade="all, delete-orphan")


class AssessmentResponse(Base):
    __tablename__ = "assessment_response"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=new_uuid)
    session_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("assessment_session.id"))
    item_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("assessment_item.id"))
    response_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean)
    raw_score: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2))
    presented_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    submitted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    time_taken: Mapped[Optional[int]] = mapped_column(Integer)
    media_key: Mapped[Optional[str]] = mapped_column(String(255))
    asr_transcript: Mapped[Optional[str]] = mapped_column(String(4000))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    session: Mapped["AssessmentSession"] = relationship("AssessmentSession", back_populates="responses")
    item: Mapped["AssessmentItem"] = relationship("AssessmentItem", back_populates="responses")



class Result(Base):
    __tablename__ = "result"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=new_uuid)
    session_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("assessment_session.id"))
    proficiency_level: Mapped[Optional[str]] = mapped_column(String(10))
    validated: Mapped[bool] = mapped_column(Boolean, default=False)
    skill_scores: Mapped[Optional[dict]] = mapped_column(JSON)
    overall_score: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2))
    result_type: Mapped[ResultType] = mapped_column(SQLEnum(ResultType), nullable=False)
    information_metric: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    session: Mapped["AssessmentSession"] = relationship("AssessmentSession", back_populates="results")
    placement_result: Mapped[Optional["PlacementResult"]] = relationship("PlacementResult", back_populates="result", uselist=False)
    speaking_result: Mapped[Optional["SpeakingResult"]] = relationship("SpeakingResult", back_populates="result", uselist=False)
    writing_result: Mapped[Optional["WritingResult"]] = relationship("WritingResult", back_populates="result", uselist=False)


class PlacementResult(Base):
    __tablename__ = "placement_result"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=new_uuid)
    result_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("result.id"))
    average_response_time: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(8, 2))
    total_items: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    result: Mapped["Result"] = relationship("Result", back_populates="placement_result")


class SpeakingResult(Base):
    __tablename__ = "speaking_result"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=new_uuid)
    result_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("result.id"))
    transcript: Mapped[Optional[str]] = mapped_column(Text)
    criteria_scores: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    result: Mapped["Result"] = relationship("Result", back_populates="speaking_result")


class WritingResult(Base):
    __tablename__ = "writing_result"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=new_uuid)
    result_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("result.id"))
    essay_text: Mapped[Optional[str]] = mapped_column(Text)
    criteria_scores: Mapped[Optional[dict]] = mapped_column(JSON)
    word_count: Mapped[Optional[int]] = mapped_column(Integer)
    essay_type: Mapped[Optional[str]] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    result: Mapped["Result"] = relationship("Result", back_populates="writing_result")



class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=new_uuid)
    actor_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    actor_type: Mapped[ActorType] = mapped_column(SQLEnum(ActorType), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[Optional[str]] = mapped_column(CHAR(36))
    details: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
