#Non adaptive

from fastapi import APIRouter, Depends, HTTPException

from app.application.interactors_diagnostic import (
    StartDiagnosticInteractor,
    SubmitDiagnosticResponsesInteractor,
)
from app.presentation.v1.schemas.diagnostic import (
    StartDiagnosticResponse,
    SubmitDiagnosticRequest,
    SubmitDiagnosticResponse,
)
from app.setup.ioc.container import (
    get_start_diagnostic_interactor,
    get_submit_diagnostic_responses_interactor,
)

router = APIRouter(prefix="/diagnostic", tags=["V1 Diagnostic API"])


@router.post("/{assigned_id}/start", response_model=StartDiagnosticResponse)
async def start_diagnostic(
    assigned_id: str,
    interactor: StartDiagnosticInteractor = Depends(get_start_diagnostic_interactor),
):
    """
    Start a non-adaptive diagnostic assessment (speaking or writing),
    depending on the assessment template type.
    """
    try:
        dto = await interactor.execute(assigned_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return StartDiagnosticResponse.from_dto(dto)


@router.post("/session/{session_id}/submit", response_model=SubmitDiagnosticResponse)
async def submit_diagnostic(
    session_id: str,
    request: SubmitDiagnosticRequest,
    interactor: SubmitDiagnosticResponsesInteractor = Depends(
        get_submit_diagnostic_responses_interactor
    ),
):
    """
    Submit all responses for a diagnostic session and get CEFR level + score.
    """
    dto = await interactor.execute(
        session_id=session_id,
        responses_payload=[r.dict() for r in request.responses],
    )

    return SubmitDiagnosticResponse.from_dto(dto)
