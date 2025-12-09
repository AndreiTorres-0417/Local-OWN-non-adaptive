#NON ADAPTIVE

from dataclasses import dataclass
from typing import List, Dict, Any

from app.domain.value_objects import AssessmentMode
from app.domain.services.diagnostic_service import DiagnosticAssessmentService
from app.application.ports import (
    AssignedAssessmentRepository,
    AssessmentSessionRepository,
    AssessmentResponseRepository,
    AssessmentItemRepository,
)
from app.application.dto import DiagnosticSessionDTO, DiagnosticResultDTO


@dataclass
class StartDiagnosticInteractor:
    assigned_repo: AssignedAssessmentRepository
    session_repo: AssessmentSessionRepository
    item_repo: AssessmentItemRepository

    async def execute(self, assigned_id: str) -> DiagnosticSessionDTO:
        """
        Creates (or resumes) a diagnostic session and returns all items at once.
        """
        assigned = await self.assigned_repo.get_by_id(assigned_id)
        template = assigned.template
        config = assigned.config

        # Determine mode from template:
        if template.is_speaking:
            mode = AssessmentMode.DIAGNOSTIC_SPEAKING
        elif template.is_writing:
            mode = AssessmentMode.DIAGNOSTIC_WRITING
        else:
            raise ValueError("Template is not diagnostic (speaking or writing).")

        # Start a new session
        session = await self.session_repo.create_new(
            assigned_assessment_id=assigned.id,
            mode=mode.value,
        )

        # Fetch all items for this assessment (non-adaptive)
        items = await self.item_repo.get_items_for_assigned_assessment(assigned.id)

        return DiagnosticSessionDTO.from_domain(session, items)


@dataclass
class SubmitDiagnosticResponsesInteractor:
    assigned_repo: AssignedAssessmentRepository
    session_repo: AssessmentSessionRepository
    response_repo: AssessmentResponseRepository
    item_repo: AssessmentItemRepository
    diag_service: DiagnosticAssessmentService

    async def execute(
        self,
        session_id: str,
        responses_payload: List[Dict[str, Any]],
    ) -> DiagnosticResultDTO:
        """
        Handle response submission + scoring for a diagnostic test.
        """

        # Load session + assigned
        session = await self.session_repo.get_by_id(session_id)
        assigned = await self.assigned_repo.get_by_id(session.assigned_assessment_id)
        template = assigned.template

        # Determine diagnostic mode
        if template.is_speaking:
            mode = AssessmentMode.DIAGNOSTIC_SPEAKING
        elif template.is_writing:
            mode = AssessmentMode.DIAGNOSTIC_WRITING
        else:
            raise ValueError("Template is not diagnostic.")

        # Convert user payload into AssessmentResponse entities
        responses = await self.response_repo.create_many(
            session_id=session.id,
            responses_payload=responses_payload
        )

        # Fetch all items
        items = await self.item_repo.get_items_for_assigned_assessment(assigned.id)

        # Score using domain service
        cefr_level, raw_score = await self.diag_service.score_session(
            session=session,
            items=items,
            responses=responses,
            mode=mode,
        )

        # Mark session completed
        await self.session_repo.mark_completed(
            session_id=session.id,
            cefr_level=cefr_level,
            raw_score=raw_score,
        )

        return DiagnosticResultDTO(
            session_id=session.id,
            cefr_level=cefr_level,
            raw_score=raw_score,
        )
