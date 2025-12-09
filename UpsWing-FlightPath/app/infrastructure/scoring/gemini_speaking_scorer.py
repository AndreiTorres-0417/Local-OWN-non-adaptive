#NO ACTUAL GEMINI YET, TO BE ADDED

from typing import List, Tuple, Optional

from app.domain.ports import SpeakingScoringPort
from app.domain.entities import AssessmentSession, AssessmentItem, AssessmentResponse


class GeminiSpeakingScorer(SpeakingScoringPort):
    """
    Infrastructure adapter for scoring speaking diagnostics.
    Calls Gemini (or placeholder logic) to evaluate audio + transcript.
    """

    async def score_speaking_session(
        self,
        session: AssessmentSession,
        items: List[AssessmentItem],
        responses: List[AssessmentResponse],
    ) -> Tuple[Optional[str], Optional[float]]:

        # TODO: Replace with actual Gemini call later. 

        # For now, return dummy scores so the pipeline is testable.
        cefr_level = "B1"
        raw_score = 0.62
        return cefr_level, raw_score
