from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.sql import func
from sqlalchemy import func as sql_func
from sqlalchemy.orm import selectinload
import uuid

from app.application.ports import (
    AssignedAssessmentRepositoryPort,
    AssessmentItemRepositoryPort,
    AssessmentConfigRepositoryPort,
    AssessmentTemplateRepositoryPort,
)
from app.domain.entities import (
    AssignedAssessment, AssessmentSession, AssessmentResponse
)
from app.domain.value_objects import AssessmentItem, AssessmentConfig, AssessmentTemplate
from app.infrastructure.persistence.models.assessment import (
    AssignedAssessment as SQLAssignedAssessment,
    AssessmentSession as SQLAssessmentSession,
    AssessmentItem as SQLAssessmentItem,
    AssessmentResponse as SQLAssessmentResponse,
    AssessmentConfig as SQLAssessmentConfig,
    AssessmentTemplate as SQLAssessmentTemplate,
    TemplateItem as SQLTemplateItem,
    SessionStatus,
)
from app.infrastructure.utils import naive_to_utc_aware


class SQLAssignedAssessmentRepository(AssignedAssessmentRepositoryPort):
    """
    SQL implementation of the AssignedAssessment aggregate repository.
    
    Handles loading and saving the complete aggregate:
    - AssignedAssessment 
    - AssessmentSession 
    - AssessmentResponse 
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, assigned_id: str) -> Optional[AssignedAssessment]:
        """Get the full aggregate by assignment ID."""
        result = await self.session.execute(
            select(SQLAssignedAssessment)
            .options(
                selectinload(SQLAssignedAssessment.sessions)
                .selectinload(SQLAssessmentSession.responses)
            )
            .where(SQLAssignedAssessment.id == assigned_id)
        )
        sql_assignment = result.scalar_one_or_none()
        
        if not sql_assignment:
            return None
        
        return self._to_domain(sql_assignment)

    async def get_by_session_id(self, session_id: str) -> Optional[AssignedAssessment]:
        """Get the full aggregate by session ID (lookup for SubmitAnswer)."""
        result = await self.session.execute(
            select(SQLAssessmentSession)
            .where(SQLAssessmentSession.id == session_id)
        )
        sql_session = result.scalar_one_or_none()
        
        if not sql_session:
            return None
        
        return await self.get_by_id(sql_session.assigned_id)

    async def get_pending_by_test_taker(self, test_taker_id: str, template_id: str) -> Optional[AssignedAssessment]:
        """Get a pending assigned assessment for a test taker and template."""
        result = await self.session.execute(
            select(SQLAssignedAssessment)
            .options(
                selectinload(SQLAssignedAssessment.sessions)
                .selectinload(SQLAssessmentSession.responses)
            )
            .where(
                and_(
                    SQLAssignedAssessment.test_taker_id == test_taker_id,
                    SQLAssignedAssessment.template_id == template_id,
                    SQLAssignedAssessment.status == "PENDING",
                )
            )
        )
        sql_assignment = result.scalar_one_or_none()
        
        if not sql_assignment:
            return None
        
        return self._to_domain(sql_assignment)

    async def save(self, assignment: AssignedAssessment) -> None:
        """
        Save the entire aggregate (assignment, session, and responses).
        Handles both insert and update operations.
        """
        result = await self.session.execute(
            select(SQLAssignedAssessment).where(SQLAssignedAssessment.id == assignment.id)
        )
        existing_assignment = result.scalar_one_or_none()
        
        if existing_assignment:
            existing_assignment.status = assignment.status
            existing_assignment.notes = assignment.notes
        
        if assignment.session:
            await self._save_session(assignment.session)

    async def _save_session(self, session: AssessmentSession) -> None:
        """Save or update session and its responses."""
        result = await self.session.execute(
            select(SQLAssessmentSession).where(SQLAssessmentSession.id == session.id)
        )
        existing_session = result.scalar_one_or_none()
        
        if existing_session:
            existing_session.current_ability = session.current_ability
            existing_session.standard_error = session.standard_error
            existing_session.questions_answered = session.questions_answered
            existing_session.status = session.status
            existing_session.current_index = session.current_index
            existing_session.completed_at = session.completed_at
        else:
            sql_session = SQLAssessmentSession(
                id=session.id,
                assigned_id=session.assigned_id,
                current_ability=session.current_ability,
                standard_error=session.standard_error,
                questions_answered=session.questions_answered,
                status=session.status,
                current_index=session.current_index,
                rubric_snapshot=session.rubric_snapshot,
                template_snapshot=session.template_snapshot,
                started_at=session.started_at,
                completed_at=session.completed_at,
                expires_at=session.expires_at
            )
            self.session.add(sql_session)
        
        for response in session.responses:
            await self._save_response(response)

    async def _save_response(self, response: AssessmentResponse) -> None:
        """Save or update a response."""
        result = await self.session.execute(
            select(SQLAssessmentResponse).where(SQLAssessmentResponse.id == response.id)
        )
        existing_response = result.scalar_one_or_none()
        
        if existing_response:
            existing_response.response_data = response.response_data
            existing_response.is_correct = response.is_correct
            existing_response.raw_score = response.raw_score
            existing_response.submitted_at = response.submitted_at
            existing_response.time_taken = response.time_taken
        else:
            sql_response = SQLAssessmentResponse(
                id=response.id,
                session_id=response.session_id,
                item_id=response.item_id,
                response_data=response.response_data,
                is_correct=response.is_correct,
                raw_score=response.raw_score,
                presented_at=response.presented_at,
                submitted_at=response.submitted_at,
                time_taken=response.time_taken,
                media_key=response.media_key,
                asr_transcript=response.asr_transcript,
            )
            self.session.add(sql_response)

    async def create(self, assignment: AssignedAssessment) -> AssignedAssessment:
        """Create a new assigned assessment aggregate."""
        assignment.id = str(uuid.uuid4())
        sql_assignment = SQLAssignedAssessment(
            id=assignment.id,
            template_id=assignment.template_id,
            test_taker_id=assignment.test_taker_id,
            test_taker_type=assignment.test_taker_type,
            assigned_by=assignment.assigned_by,
            assigned_at=assignment.assigned_at,
            due_at=assignment.due_at,
            status=assignment.status,
            notes=assignment.notes,
        )
        self.session.add(sql_assignment)
        return assignment

    def _to_domain(self, sql_assignment: SQLAssignedAssessment) -> AssignedAssessment:
        """Reconstruct the full aggregate from SQL models."""
        active_session = self._find_active_session(sql_assignment.sessions)
        
        session_domain = None
        if active_session:
            responses_domain = [
                self._response_to_domain(r) for r in active_session.responses
            ]
            session_domain = AssessmentSession(
                id=active_session.id,
                assigned_id=active_session.assigned_id,
                current_ability=active_session.current_ability,
                standard_error=active_session.standard_error,
                questions_answered=active_session.questions_answered,
                status=active_session.status.value,
                current_index=active_session.current_index,
                rubric_snapshot=active_session.rubric_snapshot,
                template_snapshot=active_session.template_snapshot,
                started_at=naive_to_utc_aware(active_session.started_at),
                completed_at=naive_to_utc_aware(active_session.completed_at) if active_session.completed_at else None,
                expires_at=naive_to_utc_aware(active_session.expires_at),
                responses=responses_domain,
            )
        
        return AssignedAssessment(
            id=sql_assignment.id,
            template_id=sql_assignment.template_id,
            test_taker_id=sql_assignment.test_taker_id,
            test_taker_type=sql_assignment.test_taker_type.value,
            assigned_by=sql_assignment.assigned_by,
            assigned_at=naive_to_utc_aware(sql_assignment.assigned_at),
            due_at=naive_to_utc_aware(sql_assignment.due_at) if sql_assignment.due_at else None,
            status=sql_assignment.status.value,
            notes=sql_assignment.notes,
            session=session_domain,
        )

    def _find_active_session(self, sessions: List[SQLAssessmentSession]) -> Optional[SQLAssessmentSession]:
        """Find the active (in-progress) session from the list."""
        for session in sessions:
            if session.status == SessionStatus.IN_PROGRESS:
                return session
        return None

    def _response_to_domain(self, sql_response: SQLAssessmentResponse) -> AssessmentResponse:
        """Convert SQL response to domain entity."""
        return AssessmentResponse(
            id=sql_response.id,
            session_id=sql_response.session_id,
            item_id=sql_response.item_id,
            response_data=sql_response.response_data,
            is_correct=sql_response.is_correct,
            raw_score=sql_response.raw_score,
            presented_at=naive_to_utc_aware(sql_response.presented_at),
            submitted_at=naive_to_utc_aware(sql_response.submitted_at) if sql_response.submitted_at else None,
            time_taken=sql_response.time_taken,
            media_key=sql_response.media_key,
            asr_transcript=sql_response.asr_transcript,
        )


class SQLAssessmentItemRepository(AssessmentItemRepositoryPort):
    """SQL implementation of the assessment item repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_item(self, item_id: str) -> Optional[AssessmentItem]:
        """Get an assessment item by ID."""
        result = await self.session.execute(
            select(SQLAssessmentItem).where(SQLAssessmentItem.id == item_id)
        )
        sql_item = result.scalar_one_or_none()
        
        if not sql_item:
            return None
        
        return self._to_domain(sql_item)

    async def get_items_by_template(self, template_id: str) -> List[AssessmentItem]:
        """Get all items linked to a template."""
        result = await self.session.execute(
            select(SQLAssessmentItem)
            .join(SQLTemplateItem, SQLTemplateItem.item_id == SQLAssessmentItem.id)
            .where(SQLTemplateItem.template_id == template_id)
        )
        sql_items = result.scalars().all()
        return [self._to_domain(item) for item in sql_items]

    async def get_items_by_skill_areas(
        self, 
        template_id: str,
        skill_areas: List[str], 
        exclude_item_ids: List[str]
    ) -> List[AssessmentItem]:
        """Get available items for specific skill areas that haven't been used."""
        skill_areas_json = sql_func.JSON_ARRAY(*skill_areas)
        
        conditions = [
            SQLTemplateItem.template_id == template_id,
            sql_func.JSON_OVERLAPS(SQLAssessmentItem.skill_area, skill_areas_json) == True,
            SQLAssessmentItem.is_active == True,
        ]
        if exclude_item_ids:
            conditions.append(~SQLAssessmentItem.id.in_(exclude_item_ids))

        query = (
            select(SQLAssessmentItem)
            .join(SQLTemplateItem, SQLTemplateItem.item_id == SQLAssessmentItem.id)
            .where(and_(*conditions))
        )
        result = await self.session.execute(query)
        sql_items = result.scalars().all()
        
        return [self._to_domain(item) for item in sql_items]

    def _to_domain(self, sql_item: SQLAssessmentItem) -> AssessmentItem:
        return AssessmentItem(
            id=sql_item.id,
            content=sql_item.content,
            item_type=sql_item.item_type,
            skill_area=sql_item.skill_area,
            target_proficiency_level=sql_item.target_proficiency_level,
            parameters=sql_item.parameters,
            is_active=sql_item.is_active,
        )


class SQLAssessmentConfigRepository(AssessmentConfigRepositoryPort):
    """SQL implementation of the assessment config repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_config(self, config_id: str) -> Optional[AssessmentConfig]:
        """Get assessment configuration by ID."""
        result = await self.session.execute(
            select(SQLAssessmentConfig).where(SQLAssessmentConfig.id == config_id)
        )
        sql_config = result.scalar_one_or_none()
        
        if not sql_config:
            return None
        
        return self._to_domain(sql_config)
    
    async def get_config_by_template(self, template_id: str) -> Optional[AssessmentConfig]:
        """Get assessment configuration by template ID."""
        result = await self.session.execute(
            select(SQLAssessmentConfig).where(
                and_(
                    SQLAssessmentConfig.template_id == template_id,
                    SQLAssessmentConfig.is_active == True
                )
            )
        )
        sql_config = result.scalar_one_or_none()
        
        if not sql_config:
            return None
        
        return self._to_domain(sql_config)

    def _to_domain(self, sql_config: SQLAssessmentConfig) -> AssessmentConfig:
        return AssessmentConfig(
            id=sql_config.id,
            template_id=sql_config.template_id,
            parameters=sql_config.parameters,
            adaptive_params=sql_config.adaptive_params,
            speaking_params=sql_config.speaking_params,
            writing_params=sql_config.writing_params,
            is_active=sql_config.is_active,
        )


class SQLAssessmentTemplateRepository(AssessmentTemplateRepositoryPort):
    """SQL implementation of the assessment template repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_template(self, template_id: str) -> Optional[AssessmentTemplate]:
        """Get assessment template by ID."""
        result = await self.session.execute(
            select(SQLAssessmentTemplate).where(SQLAssessmentTemplate.id == template_id)
        )
        sql_template = result.scalar_one_or_none()
        
        if not sql_template:
            return None
        
        return self._to_domain(sql_template)

    async def get_template_by_type_and_pathway(
        self, 
        assessment_type: str, 
        learning_pathway_id: str
    ) -> Optional[AssessmentTemplate]:
        """Get assessment template by type and learning pathway."""
        result = await self.session.execute(
            select(SQLAssessmentTemplate).where(
                and_(
                    SQLAssessmentTemplate.assessment_type == assessment_type,
                    SQLAssessmentTemplate.learning_pathway_id == learning_pathway_id,
                    SQLAssessmentTemplate.is_active == True
                )
            )
        )
        sql_template = result.scalar_one_or_none()
        
        if not sql_template:
            return None
        
        return self._to_domain(sql_template)

    def _to_domain(self, sql_template: SQLAssessmentTemplate) -> AssessmentTemplate:
        return AssessmentTemplate(
            id=sql_template.id,
            learning_pathway_id=sql_template.learning_pathway_id,
            name=sql_template.name,
            assessment_type=sql_template.assessment_type.value,
            rubric=sql_template.rubric,
            meta=sql_template.meta,
            version=sql_template.version or 1,
            is_active=sql_template.is_active,
        )
