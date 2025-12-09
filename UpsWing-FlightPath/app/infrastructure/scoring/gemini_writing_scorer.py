#NO ACTUAL GEMINI YET, TO BE ADDED

from typing import List, Tuple, Optional

from app.domain.ports import WritingScoringPort
from app.domain.entities import AssessmentSession, AssessmentItem, AssessmentResponse


class GeminiWritingScorer(WritingScoringPort):
    """
    Infrastructure adapter for scoring writing diagnostics.
    Calls Gemini (or placeholder logic) to evaluate grammar, coherence, lexical range.
    """

    async def score_writing_session(
        self,
        session: AssessmentSession,
        items: List[AssessmentItem],
        responses: List[AssessmentResponse],
    ) -> Tuple[Optional[str], Optional[float]]:

        # TODO: Replace with actual Gemini call later.

        # Dummy placeholder so pipeline functions cleanly
        cefr_level = "B2"
        raw_score = 0.75
        return cefr_level, raw_score
