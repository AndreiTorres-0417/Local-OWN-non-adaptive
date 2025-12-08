import uuid
from enum import Enum
from decimal import Decimal
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    String,
    Integer,
    TIMESTAMP,
    ForeignKey,
    DECIMAL,
    CHAR,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.infrastructure.persistence.base import Base
if TYPE_CHECKING:
    from app.infrastructure.persistence.models.assessment import Result


class RecommendationSource(str, Enum):
    AUTO = "AUTO"
    MANUAL = "MANUAL"


def new_uuid() -> str:
    return str(uuid.uuid4())


class RecommendedItem(Base):
    __tablename__ = "recommended_item"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=new_uuid)
    result_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("result.id"))
    content_id: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    content_type: Mapped[str] = mapped_column(String(20), nullable=False)
    target_skill: Mapped[str] = mapped_column(String(50), nullable=False)
    skill_gap_size: Mapped[Optional[Decimal]] = mapped_column(DECIMAL)
    rationale: Mapped[Optional[str]] = mapped_column(String(500))
    priority_order: Mapped[Optional[int]] = mapped_column(Integer)
    source: Mapped[RecommendationSource] = mapped_column(SQLEnum(RecommendationSource), nullable=False, default=RecommendationSource.AUTO)
    overridden_by: Mapped[Optional[str]] = mapped_column(String(50))
    overridden_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    result: Mapped["Result"] = relationship("Result")
