from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interactors import (
    StartPlacementTestInteractor,
    SubmitAnswerInteractor,
)
from app.application.interactors_diagnostic import (
    StartDiagnosticInteractor,
    SubmitDiagnosticResponsesInteractor,
)

from app.domain.services.cat_service import CATService
from app.domain.services.diagnostic_service import DiagnosticAssessmentService

from app.infrastructure.persistence.repositories.sql_repositories import (
    SQLAssignedAssessmentRepository,
    SQLAssessmentItemRepository,
    SQLAssessmentConfigRepository,
    SQLAssessmentTemplateRepository,
)
from app.infrastructure.persistence.uow.sql_uow import SQLAlchemyUnitOfWork
from app.infrastructure.adapters import (
    IRTServiceAdapter,
    SystemClockService,
)
from app.infrastructure.persistence.connection import get_session
from app.infrastructure.scoring.gemini_speaking_scorer import GeminiSpeakingScorer
from app.infrastructure.scoring.gemini_writing_scorer import GeminiWritingScorer


# ---------------------------------------------------------------------------
#  Core infrastructure services (shared)
# ---------------------------------------------------------------------------

def get_irt_service_adapter() -> IRTServiceAdapter:
    """Provides the concrete IRT service adapter."""
    return IRTServiceAdapter()


def get_system_clock_service() -> SystemClockService:
    """Provides the concrete system clock service."""
    return SystemClockService()


def get_cat_service(
    psychometric_model: Annotated[IRTServiceAdapter, Depends(get_irt_service_adapter)],
) -> CATService:
    """Builds the CATService using the concrete IRT adapter."""
    return CATService(psychometric_model)


# ---------------------------------------------------------------------------
#  Diagnostic scoring services (non-adaptive)
# ---------------------------------------------------------------------------

def get_speaking_scorer() -> GeminiSpeakingScorer:
    """Provides the Gemini speaking scorer adapter."""
    return GeminiSpeakingScorer()


def get_writing_scorer() -> GeminiWritingScorer:
    """Provides the Gemini writing scorer adapter."""
    return GeminiWritingScorer()


def get_diagnostic_service(
    speaking_scorer: Annotated[GeminiSpeakingScorer, Depends(get_speaking_scorer)],
    writing_scorer: Annotated[GeminiWritingScorer, Depends(get_writing_scorer)],
) -> DiagnosticAssessmentService:
    """Builds the DiagnosticAssessmentService using Gemini-based scorers."""
    return DiagnosticAssessmentService(
        speaking_scorer=speaking_scorer,
        writing_scorer=writing_scorer,
    )


# ---------------------------------------------------------------------------
#  Adaptive placement interactors (existing)
# ---------------------------------------------------------------------------

def get_start_placement_test_interactor(
    db_session: Annotated[AsyncSession, Depends(get_session)],
    cat_service: Annotated[CATService, Depends(get_cat_service)],
    clock_service: Annotated[SystemClockService, Depends(get_system_clock_service)],
) -> StartPlacementTestInteractor:
    """Constructs the interactor for starting a placement test."""
    assigned_repo = SQLAssignedAssessmentRepository(db_session)
    item_repo = SQLAssessmentItemRepository(db_session)
    config_repo = SQLAssessmentConfigRepository(db_session)
    template_repo = SQLAssessmentTemplateRepository(db_session)
    uow = SQLAlchemyUnitOfWork(db_session)

    return StartPlacementTestInteractor(
        assigned_repo=assigned_repo,
        item_repo=item_repo,
        config_repo=config_repo,
        template_repo=template_repo,
        cat_service=cat_service,
        clock_service=clock_service,
        uow=uow,
    )


def get_submit_answer_interactor(
    db_session: Annotated[AsyncSession, Depends(get_session)],
    cat_service: Annotated[CATService, Depends(get_cat_service)],
    clock_service: Annotated[SystemClockService, Depends(get_system_clock_service)],
) -> SubmitAnswerInteractor:
    """Constructs the interactor for submitting an answer."""
    assigned_repo = SQLAssignedAssessmentRepository(db_session)
    item_repo = SQLAssessmentItemRepository(db_session)
    config_repo = SQLAssessmentConfigRepository(db_session)
    template_repo = SQLAssessmentTemplateRepository(db_session)
    uow = SQLAlchemyUnitOfWork(db_session)

    return SubmitAnswerInteractor(
        assigned_repo=assigned_repo,
        item_repo=item_repo,
        config_repo=config_repo,
        template_repo=template_repo,
        cat_service=cat_service,
        clock_service=clock_service,
        uow=uow,
    )


# ---------------------------------------------------------------------------
#  Non-adaptive diagnostic interactors (new)
# ---------------------------------------------------------------------------

def get_start_diagnostic_interactor(
    db_session: Annotated[AsyncSession, Depends(get_session)],
    diagnostic_service: Annotated[
        DiagnosticAssessmentService,
        Depends(get_diagnostic_service),
    ],
    clock_service: Annotated[SystemClockService, Depends(get_system_clock_service)],
) -> StartDiagnosticInteractor:
    """
    Constructs the interactor for starting a non-adaptive diagnostic assessment
    (speaking or writing, depending on the template).
    """
    assigned_repo = SQLAssignedAssessmentRepository(db_session)
    item_repo = SQLAssessmentItemRepository(db_session)
    config_repo = SQLAssessmentConfigRepository(db_session)
    template_repo = SQLAssessmentTemplateRepository(db_session)
    uow = SQLAlchemyUnitOfWork(db_session)

    return StartDiagnosticInteractor(
        assigned_repo=assigned_repo,
        item_repo=item_repo,
        config_repo=config_repo,
        template_repo=template_repo,
        diag_service=diagnostic_service,
        clock_service=clock_service,
        uow=uow,
    )


def get_submit_diagnostic_responses_interactor(
    db_session: Annotated[AsyncSession, Depends(get_session)],
    diagnostic_service: Annotated[
        DiagnosticAssessmentService,
        Depends(get_diagnostic_service),
    ],
    clock_service: Annotated[SystemClockService, Depends(get_system_clock_service)],
) -> SubmitDiagnosticResponsesInteractor:
    """
    Constructs the interactor for submitting responses to a diagnostic assessment
    and triggering scoring.
    """
    assigned_repo = SQLAssignedAssessmentRepository(db_session)
    item_repo = SQLAssessmentItemRepository(db_session)
    config_repo = SQLAssessmentConfigRepository(db_session)
    template_repo = SQLAssessmentTemplateRepository(db_session)
    uow = SQLAlchemyUnitOfWork(db_session)

    return SubmitDiagnosticResponsesInteractor(
        assigned_repo=assigned_repo,
        item_repo=item_repo,
        config_repo=config_repo,
        template_repo=template_repo,
        diag_service=diagnostic_service,
        clock_service=clock_service,
        uow=uow,
    )
