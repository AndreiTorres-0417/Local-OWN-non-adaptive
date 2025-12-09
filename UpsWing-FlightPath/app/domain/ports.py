from typing import List, Protocol, Tuple, Optional
from app.domain.entities import AssessmentResponse, AssessmentSession
from app.domain.value_objects import AssessmentItem


class PsychometricModelInterface(Protocol):
    """Domain interface for psychometric model implementations (IRT calculations)."""
    
    async def calculate_information(
        self, 
        ability: float, 
        item: AssessmentItem
    ) -> float:
        """Calculate item information for given ability and item parameters."""
        ...
    
    async def calculate_ability(
        self, 
        responses: List[AssessmentResponse],
        items: List[AssessmentItem]
    ) -> Tuple[float, float]:
        """Calculate ability estimate and standard error from responses."""
        ...
    
    async def estimate_ability_with_item(
        self,
        responses: List[AssessmentResponse],
        items: List[AssessmentItem],
        current_item: AssessmentItem,
        current_response_score: float
    ) -> Tuple[float, float]:
        """Calculate new ability estimate including the current response."""
        ...


# --------------
#  Non-adaptive 
# --------------
class SpeakingScoringPort(Protocol):
    async def score_speaking_session(
        self,
        session: AssessmentSession,
        items: List[AssessmentItem],
        responses: List[AssessmentResponse],
    ) -> Tuple[Optional[str], Optional[float]]:
        """
        Returns (cefr_level, raw_score) for a speaking diagnostic session.
        """
        ...


class WritingScoringPort(Protocol):
    async def score_writing_session(
        self,
        session: AssessmentSession,
        items: List[AssessmentItem],
        responses: List[AssessmentResponse],
    ) -> Tuple[Optional[str], Optional[float]]:
        """
        Returns (cefr_level, raw_score) for a writing diagnostic session.
        """
        ...
