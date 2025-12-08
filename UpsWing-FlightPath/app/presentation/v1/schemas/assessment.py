from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from enum import Enum
from app.application.dto import AssessmentItemPublicDTO, ProgressDTO, PlacementResultDTO, SpeakingResultDTO, WritingResultDTO, RecommendationItemDTO


class AssessmentType(str, Enum):
    ADAPTIVE = "adaptive"
    DIAGNOSTIC_WRITING = "diagnostic_writing"
    DIAGNOSTIC_SPEAKING = "diagnostic_speaking"


class LearningPathwayType(str, Enum):
    DEFAULT = "Default"
    GENERAL = "General"
    ACADEMIC = "Academic"
    LIFESOCIAL = "Life & Social"
    CAREER = "Career"


class PlacementSubmitAnswerRequest(BaseModel):
    response_data: Dict[str, Any] = Field(..., description="Student's answer data")
    time_taken: Optional[int] = Field(None, description="Time taken in seconds")

    class Config:
        from_attributes = True


class PlacementTestStartResponse(BaseModel):
    session_id: str
    first_question: AssessmentItemPublicDTO
    progress: ProgressDTO

    class Config:
        from_attributes = True


class PlacementTestSubmitAnswerResponse(BaseModel):
    next_question: Optional[AssessmentItemPublicDTO] = None
    progress: ProgressDTO
    assessment_complete: bool = False

    class Config:
        from_attributes = True


class AssessmentCompleteResponse(BaseModel):
    session_id: str
    placement_result: Optional[PlacementResultDTO] = None
    speaking_result: Optional[SpeakingResultDTO] = None
    writing_result: Optional[WritingResultDTO] = None
    recommendations: List[RecommendationItemDTO] = []

