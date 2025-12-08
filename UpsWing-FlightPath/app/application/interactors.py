from decimal import Decimal
import uuid
from app.domain.entities import AssignedAssessment, AssessmentSession, SessionStatus
from app.domain.services.cat_service import CATService
from app.application.ports import (
    AssignedAssessmentRepositoryPort,
    AssessmentItemRepositoryPort,
    AssessmentConfigRepositoryPort,
    AssessmentTemplateRepositoryPort,
    ClockService,
    UnitOfWork
)
from app.application.dto import (
    StartPlacementTestCommand, StartPlacementTestResult,
    SubmitAnswerCommand, SubmitAnswerResult, ProgressDTO
)
from app.application.mappers import map_assessment_item_to_public_dto
from datetime import timedelta
from app.domain.exceptions import (
    SessionNotFoundException, 
    InvalidSessionStateError, 
    InvalidResponseError, 
    AssessmentConfigurationNotFoundException, 
    ItemNotFoundException,
    AssignedAssessmentNotFoundException,
)


class StartPlacementTestInteractor:
    """Use case interactor for starting a placement test."""
    
    def __init__(
        self,
        assigned_repo: AssignedAssessmentRepositoryPort,
        item_repo: AssessmentItemRepositoryPort,
        config_repo: AssessmentConfigRepositoryPort,
        template_repo: AssessmentTemplateRepositoryPort,
        cat_service: CATService,  
        clock_service: ClockService,
        uow: UnitOfWork
    ):
        self.assigned_repo = assigned_repo
        self.item_repo = item_repo
        self.config_repo = config_repo
        self.template_repo = template_repo
        self.cat_service = cat_service
        self.clock_service = clock_service
        self.uow = uow

    async def execute(self, command: StartPlacementTestCommand) -> StartPlacementTestResult:
        async with self.uow:
            assignment = await self.assigned_repo.get_by_id(command.assigned_id)
            if not assignment:
                raise AssignedAssessmentNotFoundException(f"Assigned assessment not found: {command.assigned_id}")

            template = await self.template_repo.get_template(assignment.template_id)
            if not template:
                raise AssessmentConfigurationNotFoundException(f"Template not found: {assignment.template_id}")

            config = await self.config_repo.get_config_by_template(template.id)
            if not config:
                raise AssessmentConfigurationNotFoundException(f"No config found for template: {template.id}")

            if assignment.has_active_session():
                pending_response = assignment.session.get_pending_response()
                if pending_response:
                    question_entity = await self.item_repo.get_item(pending_response.item_id)
                    if not question_entity:
                        raise ItemNotFoundException(f"Assessment Item not found: {pending_response.item_id}")
                    question_dto = map_assessment_item_to_public_dto(question_entity)
                    progress_dto = self._build_progress_dto(assignment, config)
                    return StartPlacementTestResult(
                        session_id=assignment.session.id,
                        first_question=question_dto,
                        progress=progress_dto,
                    )

            now = self.clock_service.now()
            time_limit = config.parameters.get("time_limit_minutes", 120) if config.parameters else 120
            expires_at = now + timedelta(minutes=time_limit)
            
            starting_ability = 0.0
            if config.adaptive_params:
                starting_ability = config.adaptive_params.get("starting_ability", 0.0)

            session = assignment.start_session(
                session_id=str(uuid.uuid4()),
                now=now,
                expires_at=expires_at,
                starting_ability=starting_ability,
                rubric_snapshot=template.rubric,
                template_snapshot={"template_id": template.id, "name": template.name},
            )

            skill_areas = []
            if config.adaptive_params:
                skill_areas = config.adaptive_params.get("skill_areas", [])

            available_items = await self.item_repo.get_items_by_skill_areas(
                template.id, skill_areas, []
            )

            first_question_entity = await self.cat_service.select_next_question(
                ability=starting_ability,
                skill_areas=skill_areas,
                used_item_ids=[],
                available_items=available_items
            )
            
            if not first_question_entity:
                raise ItemNotFoundException("No suitable questions available for assessment start")

            assignment.present_question(
                response_id=str(uuid.uuid4()),
                item_id=first_question_entity.id,
                now=self.clock_service.now(),
            )

            await self.assigned_repo.save(assignment)

            first_question_dto = map_assessment_item_to_public_dto(first_question_entity)
            progress_dto = self._build_progress_dto(assignment, config)

            return StartPlacementTestResult(
                session_id=session.id,
                first_question=first_question_dto,
                progress=progress_dto,
            )

    def _build_progress_dto(self, assignment: AssignedAssessment, config) -> ProgressDTO:
        max_questions = 25
        if config.adaptive_params:
            max_questions = config.adaptive_params.get("max_questions", 25)
        
        return ProgressDTO(
            questions_completed=assignment.get_questions_answered(),
            max_questions=max_questions,
            current_ability=assignment.get_current_ability(),
            standard_error=assignment.get_standard_error(),
        )


class SubmitAnswerInteractor:
    """Use case interactor for submitting answers in a placement test."""
    
    def __init__(
        self,
        assigned_repo: AssignedAssessmentRepositoryPort,
        item_repo: AssessmentItemRepositoryPort,
        config_repo: AssessmentConfigRepositoryPort,
        template_repo: AssessmentTemplateRepositoryPort,
        cat_service: CATService,  
        clock_service: ClockService,
        uow: UnitOfWork
    ):
        self.assigned_repo = assigned_repo
        self.item_repo = item_repo
        self.config_repo = config_repo
        self.template_repo = template_repo
        self.cat_service = cat_service
        self.clock_service = clock_service
        self.uow = uow

    async def execute(self, command: SubmitAnswerCommand) -> SubmitAnswerResult:
        async with self.uow:
            now = self.clock_service.now()

            assignment = await self.assigned_repo.get_by_session_id(command.session_id)
            if not assignment or not assignment.session:
                raise SessionNotFoundException(f"Assessment session not found: {command.session_id}")

            if not assignment.session.can_accept_answer(now):
                raise InvalidSessionStateError(f"Session {command.session_id} cannot accept answers")

            pending_response = assignment.session.get_pending_response()
            if not pending_response:
                raise SessionNotFoundException(f"No pending response for session {command.session_id}")

            if not pending_response.has_valid_response(command.response_data):
                raise InvalidResponseError("Invalid response data provided")

            item_entity = await self.item_repo.get_item(pending_response.item_id)
            if not item_entity:
                raise ItemNotFoundException(f"Assessment item not found: {pending_response.item_id}")

            config = await self.config_repo.get_config_by_template(assignment.template_id)
            if not config:
                raise AssessmentConfigurationNotFoundException("No assessment configuration found")

            score, is_correct = await self.cat_service.score_response(item_entity, command.response_data)

            previous_responses = assignment.session.get_submitted_responses()
            previous_items = []
            for response in previous_responses:
                item = await self.item_repo.get_item(response.item_id)
                if item:
                    previous_items.append(item)

            assignment.submit_response(
                response_data=command.response_data,
                is_correct=is_correct,
                score=score,
                time_taken=command.time_taken,
                now=now,
            )

            new_ability, standard_error = await self.cat_service.process_response(
                responses=previous_responses,
                items=previous_items,
                current_item=item_entity,
                current_response_score=score
            )

            assignment.update_ability_estimate(new_ability, standard_error)

            should_complete = self.cat_service.check_termination_criteria(
                session=assignment.session,
                config=config,
            )

            if should_complete:
                assignment.complete_assessment(now)
                await self.assigned_repo.save(assignment)
                
                progress_dto = self._build_progress_dto(assignment, config, new_ability, standard_error)
                return SubmitAnswerResult(
                    next_question=None,
                    progress=progress_dto,
                    is_complete=True,
                    is_correct=is_correct,
                )

            return await self._select_next_question(
                assignment, config, new_ability, standard_error, is_correct
            )

    async def _select_next_question(
        self, assignment: AssignedAssessment, config, new_ability, standard_error, is_correct
    ) -> SubmitAnswerResult:
        """Select and present the next question."""
        answered_ids = assignment.session.get_answered_item_ids()

        skill_areas = []
        if config.adaptive_params:
            skill_areas = config.adaptive_params.get("skill_areas", [])

        available_items = await self.item_repo.get_items_by_skill_areas(
            assignment.template_id, skill_areas, answered_ids
        )

        next_question_entity = await self.cat_service.select_next_question(
            ability=new_ability,
            skill_areas=skill_areas,
            used_item_ids=answered_ids,
            available_items=available_items
        )

        if next_question_entity:
            assignment.present_question(
                response_id=str(uuid.uuid4()),
                item_id=next_question_entity.id,
                now=self.clock_service.now(),
            )
            
            await self.assigned_repo.save(assignment)

            next_question_dto = map_assessment_item_to_public_dto(next_question_entity)
            progress_dto = self._build_progress_dto(assignment, config, new_ability, standard_error)

            return SubmitAnswerResult(
                next_question=next_question_dto,
                progress=progress_dto,
                is_complete=False,
                is_correct=is_correct,
            )
        else:
            now = self.clock_service.now()
            assignment.complete_assessment(now)
            await self.assigned_repo.save(assignment)

            progress_dto = self._build_progress_dto(assignment, config, new_ability, standard_error)
            return SubmitAnswerResult(
                next_question=None,
                progress=progress_dto,
                is_complete=True,
                is_correct=is_correct,
            )

    def _build_progress_dto(self, assignment: AssignedAssessment, config, ability, standard_error) -> ProgressDTO:
        max_questions = 25
        if config.adaptive_params:
            max_questions = config.adaptive_params.get("max_questions", 25)

        return ProgressDTO(
            questions_completed=assignment.get_questions_answered(),
            max_questions=max_questions,
            current_ability=ability,
            standard_error=Decimal(str(standard_error)) if standard_error else None,
        )
