# NON Adaptive

from typing import List, Dict, Any, Optional

from pydantic import BaseModel

from app.application.dto import DiagnosticSessionDTO, DiagnosticResultDTO


class DiagnosticItem(BaseModel):
    """Schema for a single diagnostic item returned to the client."""
    item_id: str
    content: Dict[str, Any]
    skill_area: List[str]
    target_proficiency_level: str


class StartDiagnosticResponse(BaseModel):
    """Schema for starting a diagnostic assessment (speaking/writing)."""
    session_id: str
    assessment_id: str
    items: List[DiagnosticItem]

    @classmethod
    def from_dto(cls, dto: DiagnosticSessionDTO) -> "StartDiagnosticResponse":
        return cls(
            session_id=dto.session_id,
            assessment_id=dto.assessment_id,
            items=[
                DiagnosticItem(
                    item_id=item.item_id,
                    content=item.content,
                    skill_area=item.skill_area,
                    target_proficiency_level=item.target_proficiency_level,
                )
                for item in dto.items
            ],
        )


class SingleDiagnosticResponse(BaseModel):
    """Schema for a single response to a diagnostic item."""
    item_id: str
    response: str  # text (writing) or audio reference (speaking)


class SubmitDiagnosticRequest(BaseModel):
    """Schema for submitting all responses for a diagnostic session."""
    responses: List[SingleDiagnosticResponse]


class SubmitDiagnosticResponse(BaseModel):
    """Schema for the result of a diagnostic assessment."""
    session_id: str
    cefr_level: Optional[str]
    raw_score: Optional[float]

    @classmethod
    def from_dto(cls, dto: DiagnosticResultDTO) -> "SubmitDiagnosticResponse":
        return cls(
            session_id=dto.session_id,
            cefr_level=dto.cefr_level,
            raw_score=dto.raw_score,
        )
