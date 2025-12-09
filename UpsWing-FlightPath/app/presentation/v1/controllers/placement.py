from fastapi import APIRouter, Depends, HTTPException

from app.application.dto import StartPlacementTestCommand, SubmitAnswerCommand
from app.application.interactors import StartPlacementTestInteractor, SubmitAnswerInteractor
from app.setup.ioc.container import get_start_placement_test_interactor, get_submit_answer_interactor

from app.presentation.v1.schemas.assessment import PlacementSubmitAnswerRequest, PlacementTestStartResponse, PlacementTestSubmitAnswerResponse

router = APIRouter(prefix="/placement", tags=["V1 Placement API"])


@router.post("/{assigned_id}/start", response_model=PlacementTestStartResponse)
async def start_test(
    assigned_id: str,
    interactor: StartPlacementTestInteractor = Depends(get_start_placement_test_interactor),
):
    """
    Endpoint: Start a new test session from an assigned assessment
    """
    command = StartPlacementTestCommand(
        assigned_id=assigned_id,
    )
    
    result = await interactor.execute(command)

    return PlacementTestStartResponse(
        session_id=result.session_id,
        first_question=result.first_question,
        progress=result.progress,
    )


@router.post("/{session_id}/answer", response_model=PlacementTestSubmitAnswerResponse)
async def submit_answer(
    session_id: str,
    request: PlacementSubmitAnswerRequest,
    interactor: SubmitAnswerInteractor = Depends(get_submit_answer_interactor)
):
    """
    Endpoint: Submit answer for current question
    """
    command = SubmitAnswerCommand(
        session_id=session_id,
        response_data=request.response_data,
        time_taken=request.time_taken,
    )
    
    result = await interactor.execute(command)

    return PlacementTestSubmitAnswerResponse(
        next_question=result.next_question,
        progress=result.progress,
        assessment_complete=result.is_complete,
    )
