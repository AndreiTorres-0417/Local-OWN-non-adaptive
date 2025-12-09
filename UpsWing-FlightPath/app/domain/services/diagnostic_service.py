
# Diagnostic (non-adaptive) assessment domain service.

# This service handles the core business logic for non-adaptive diagnostic assessments
# (speaking and writing). It does NOT deal with database persistence; it only operates
# on domain entities and delegates scoring to the speaking / writing scoring ports.


from typing import List, Optional, Tuple

from app.domain.entities import AssessmentSession, AssessmentResponse
from app.domain.value_objects import AssessmentItem, AssessmentConfig, AssessmentMode
from app.domain.ports import SpeakingScoringPort, WritingScoringPort


class DiagnosticAssessmentService:
    """
    Domain service for non-adaptive diagnostic assessments.

    Responsibilities:
    - For a completed diagnostic session (speaking or writing),
      call the appropriate scoring port.
    - Return CEFR level and raw score to the application layer.
    """

    def __init__(
        self,
        speaking_scorer: SpeakingScoringPort,
        writing_scorer: WritingScoringPort,
    ) -> None:
        self._speaking_scorer = speaking_scorer
        self._writing_scorer = writing_scorer

    async def score_session(
        self,
        session: AssessmentSession,
        items: List[AssessmentItem],
        responses: List[AssessmentResponse],
        config: AssessmentConfig,
    ) -> Tuple[Optional[str], Optional[float]]:
        """
        Score a completed diagnostic session and return (cefr_level, raw_score).

        The caller (application interactor) is responsible for:
        - Creating / updating the AssessmentSession and AssessmentResponse entities.
        - Ensuring that all responses for the session are present in `responses`.
        - Persisting any changes to the database after scoring.
        """

        # Decide which scorer to use based on mode / template type.
        # For now we rely on AssessmentMode; the application layer
        # should ensure the correct mode is provided in config.
        mode = getattr(config, "mode", None)

        if mode == AssessmentMode.DIAGNOSTIC_SPEAKING:
            cefr_level, raw_score = await self._speaking_scorer.score_speaking_session(
                session=session,
                items=items,
                responses=responses,
            )
            return cefr_level, raw_score

        if mode == AssessmentMode.DIAGNOSTIC_WRITING:
            cefr_level, raw_score = await self._writing_scorer.score_writing_session(
                session=session,
                items=items,
                responses=responses,
            )
            return cefr_level, raw_score

        # If mode is not set or not diagnostic, we do not score here.
        raise ValueError(f"Unsupported or missing diagnostic mode on config: {mode}")
