from datetime import datetime
from typing import List, Protocol, Optional
from app.domain.entities import AssignedAssessment
from app.domain.value_objects import AssessmentItem, AssessmentConfig, AssessmentTemplate


class AssignedAssessmentRepositoryPort(Protocol):
    """
    Repository port for the AssignedAssessment aggregate root.
    
    This is the repository for the assessment aggregate.
    It handles persistence of the entire aggregate including:
    - AssignedAssessment 
    - AssessmentSession 
    - AssessmentResponse 
    
    All access to session/response data goes through the aggregate root.
    """
    
    async def get_by_id(self, assigned_id: str) -> Optional[AssignedAssessment]:
        """
        Get an assigned assessment aggregate by ID.
        Loads the full aggregate including active session and its responses.
        """
        ...

    async def get_by_session_id(self, session_id: str) -> Optional[AssignedAssessment]:
        """
        Lookup aggregate by session ID.
        Returns the full aggregate (assignment + session + responses).
        Used when client only has session_id (e.g., SubmitAnswer endpoint).
        """
        ...
    
    async def get_pending_by_test_taker(self, test_taker_id: str, template_id: str) -> Optional[AssignedAssessment]:
        """Get a pending assigned assessment for a test taker and template."""
        ...
 
    async def save(self, assignment: AssignedAssessment) -> None:
        """
        Save the entire aggregate (assignment, session, and responses).
        Handles insert/update of all entities within the aggregate boundary.
        """
        ...
    
    async def create(self, assignment: AssignedAssessment) -> AssignedAssessment:
        """Create a new assigned assessment aggregate."""
        ...


class AssessmentItemRepositoryPort(Protocol):
    """Port for assessment item operations."""
    
    async def get_item(self, item_id: str) -> Optional[AssessmentItem]:
        """Get an assessment item by ID."""
        ...
    
    async def get_items_by_template(self, template_id: str) -> List[AssessmentItem]:
        """Get all items linked to a template."""
        ...
    
    async def get_items_by_skill_areas(
        self, 
        template_id: str,
        skill_areas: List[str], 
        exclude_item_ids: List[str]
    ) -> List[AssessmentItem]:
        """Get available items for specific skill areas that haven't been used."""
        ...


class AssessmentConfigRepositoryPort(Protocol):
    """Port for assessment configuration operations."""
    
    async def get_config(self, config_id: str) -> Optional[AssessmentConfig]:
        """Get assessment configuration by ID."""
        ...
    
    async def get_config_by_template(self, template_id: str) -> Optional[AssessmentConfig]:
        """Get assessment configuration by template ID."""
        ...


class AssessmentTemplateRepositoryPort(Protocol):
    """Port for assessment template operations."""
    
    async def get_template(self, template_id: str) -> Optional[AssessmentTemplate]:
        """Get assessment template by ID."""
        ...
    
    async def get_template_by_type_and_pathway(
        self, 
        assessment_type: str, 
        learning_pathway_id: str
    ) -> Optional[AssessmentTemplate]:
        """Get assessment template by type and learning pathway."""
        ...


class ClockService(Protocol):
    """Port: Time provider (for testability)"""
    def now(self) -> datetime:
        ...


class UnitOfWork(Protocol):
    """Unit of Work protocol for transaction management."""
    
    async def __aenter__(self):
        """Enter async context manager."""
        ...
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager, committing or rolling back as appropriate."""
        ...
    
    async def commit(self):
        """Commit the current transaction."""
        ...
    
    async def rollback(self):
        """Rollback the current transaction."""
        ...
