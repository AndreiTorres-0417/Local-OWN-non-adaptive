"""Domain entities for the assessment system with business rules and invariants."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple


class SessionStatus:
    """Session status constants."""
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class AssignmentStatus:
    """Assignment status constants."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"


@dataclass
class AssessmentResponse:
    """Child entity representing a test-taker's response to an assessment item."""
    
    id: str
    session_id: str
    item_id: str
    response_data: Dict
    is_correct: Optional[bool]
    raw_score: Optional[Decimal]
    presented_at: datetime
    submitted_at: Optional[datetime]
    time_taken: Optional[int]
    media_key: Optional[str]
    asr_transcript: Optional[str]
    
    def has_valid_response(self, response: Dict) -> bool:
        """Business rule: response must have appropriate data."""
        return bool(response.get("selected_option"))
    
    def calculate_score(self) -> float:
        """Business rule: calculate the score for this response."""
        if self.raw_score is not None:
            return float(self.raw_score)
        return 1.0 if self.is_correct else 0.0
    
    def is_pending(self) -> bool:
        """Business rule: check if response is still pending (not submitted)."""
        return self.submitted_at is None


@dataclass
class AssessmentSession:
    """Child entity representing an active assessment session."""
    
    id: str
    assigned_id: str
    current_ability: Optional[Decimal]
    standard_error: Optional[Decimal]
    questions_answered: int
    status: str
    current_index: Optional[int]
    rubric_snapshot: Optional[Dict]
    template_snapshot: Optional[Dict]
    started_at: datetime
    completed_at: Optional[datetime]
    expires_at: datetime
    responses: List[AssessmentResponse] = field(default_factory=list)
    
    def can_accept_answer(self, now: datetime) -> bool:
        """Business rule: session must be in progress and not time-expired to accept answers."""
        if self.status != SessionStatus.IN_PROGRESS:
            return False
        if self.is_time_expired(now):
            return False
        return True

    def is_time_expired(self, now: datetime) -> bool:
        """Business rule: check if session time has expired."""
        return now > self.expires_at
    
    def is_terminated(self) -> bool:
        """Business rule: session is terminated if not in progress."""
        return self.status != SessionStatus.IN_PROGRESS
    
    def is_complete(self) -> bool:
        """Business rule: check if session is completed."""
        return self.status == SessionStatus.COMPLETED
    
    def has_reached_max_questions(self, max_questions: int) -> bool:
        """Business rule: check if session has reached maximum number of questions."""
        return self.questions_answered >= max_questions
    
    def has_sufficient_precision(self, min_standard_error: float) -> bool:
        """Business rule: check if standard error is below threshold (sufficient precision)."""
        if self.standard_error is None:
            return False
        return float(self.standard_error) <= min_standard_error
    
    def has_reached_min_questions(self, min_questions: int) -> bool:
        """Business rule: check if session has reached minimum number of questions."""
        return self.questions_answered >= min_questions

    def get_pending_response(self) -> Optional[AssessmentResponse]:
        """Get the current pending (unsubmitted) response."""
        for response in self.responses:
            if response.is_pending():
                return response
        return None

    def get_submitted_responses(self) -> List[AssessmentResponse]:
        """Get all submitted responses."""
        return [r for r in self.responses if not r.is_pending()]

    def get_answered_item_ids(self) -> List[str]:
        """Get IDs of all items that have been answered."""
        return [r.item_id for r in self.responses]


@dataclass
class AssignedAssessment:
    """
    Aggregate Root for the assessment bounded context.
    
    Owns and controls:
    - AssessmentSession (child entity)
    - AssessmentResponse (grandchild entities via session)
    
    All mutations to sessions and responses must flow through this aggregate.
    """
    
    id: str
    template_id: str
    test_taker_id: str
    test_taker_type: str
    assigned_by: Optional[str]
    assigned_at: datetime
    due_at: Optional[datetime]
    status: str
    notes: Optional[str]
    session: Optional[AssessmentSession] = None
    
    
    def can_start(self, now: datetime) -> bool:
        """Business rule: can only start if PENDING and not past due."""
        if self.status != AssignmentStatus.PENDING:
            return False
        if self.due_at and now > self.due_at:
            return False
        return True
    
    def is_expired(self, now: datetime) -> bool:
        """Business rule: check if assignment has expired."""
        if self.due_at is None:
            return False
        return now > self.due_at and self.status != AssignmentStatus.COMPLETED

    def has_active_session(self) -> bool:
        """Check if there's an active session."""
        return self.session is not None and self.session.status == SessionStatus.IN_PROGRESS


    def start_session(
        self,
        session_id: str,
        now: datetime,
        expires_at: datetime,
        starting_ability: float,
        rubric_snapshot: Optional[Dict] = None,
        template_snapshot: Optional[Dict] = None,
    ) -> AssessmentSession:
        """
        Start a new assessment session for this assignment.
        Enforces invariant: can only start if assignment allows it.
        """
        if not self.can_start(now):
            raise ValueError(f"Cannot start session: assignment status is {self.status}")
        
        if self.session is not None and self.session.status == SessionStatus.IN_PROGRESS:
            raise ValueError("An active session already exists for this assignment")
        
        self.session = AssessmentSession(
            id=session_id,
            assigned_id=self.id,
            current_ability=Decimal(str(starting_ability)),
            standard_error=None,
            questions_answered=0,
            status=SessionStatus.IN_PROGRESS,
            current_index=0,
            rubric_snapshot=rubric_snapshot,
            template_snapshot=template_snapshot,
            started_at=now,
            completed_at=None,
            expires_at=expires_at,
            responses=[],
        )
        self.status = AssignmentStatus.IN_PROGRESS
        return self.session

    def present_question(
        self,
        response_id: str,
        item_id: str,
        now: datetime,
    ) -> AssessmentResponse:
        """
        Present a new question by creating a pending response.
        Enforces invariant: must have an active session.
        """
        if self.session is None or self.session.status != SessionStatus.IN_PROGRESS:
            raise ValueError("No active session to present question")
        
        response = AssessmentResponse(
            id=response_id,
            session_id=self.session.id,
            item_id=item_id,
            response_data={},
            is_correct=None,
            raw_score=None,
            presented_at=now,
            submitted_at=None,
            time_taken=None,
            media_key=None,
            asr_transcript=None,
        )
        self.session.responses.append(response)
        return response

    def submit_response(
        self,
        response_data: Dict,
        is_correct: bool,
        score: float,
        time_taken: Optional[int],
        now: datetime,
    ) -> AssessmentResponse:
        """
        Submit an answer for the current pending response.
        Enforces invariants: session must accept answers, must have pending response.
        """
        if self.session is None:
            raise ValueError("No session exists for this assignment")
        
        if not self.session.can_accept_answer(now):
            raise ValueError("Session cannot accept answers")
        
        pending = self.session.get_pending_response()
        if pending is None:
            raise ValueError("No pending response to submit")
        
        if not pending.has_valid_response(response_data):
            raise ValueError("Invalid response data")
        
        pending.response_data = response_data
        pending.is_correct = is_correct
        pending.raw_score = Decimal(str(score))
        pending.time_taken = time_taken
        pending.submitted_at = now
        
        self.session.questions_answered += 1
        
        return pending

    def update_ability_estimate(
        self,
        new_ability: float,
        new_standard_error: Optional[float],
    ) -> None:
        """Update the ability estimate after processing a response."""
        if self.session is None:
            raise ValueError("No session exists for this assignment")
        
        self.session.current_ability = Decimal(str(new_ability))
        self.session.standard_error = Decimal(str(new_standard_error)) if new_standard_error else None

    def complete_assessment(self, now: datetime) -> None:
        """
        Complete the assessment session and assignment.
        Enforces invariant: must have an active session.
        """
        if self.session is None:
            raise ValueError("No session to complete")
        
        self.session.status = SessionStatus.COMPLETED
        self.session.completed_at = now
        self.status = AssignmentStatus.COMPLETED

    def cancel_session(self) -> None:
        """Cancel the current session."""
        if self.session is None:
            raise ValueError("No session to cancel")
        
        self.session.status = SessionStatus.CANCELLED

    def expire_session(self) -> None:
        """Mark session as expired."""
        if self.session is None:
            raise ValueError("No session to expire")
        
        self.session.status = SessionStatus.EXPIRED
        self.status = AssignmentStatus.EXPIRED

    # --- Query methods ---

    def get_current_ability(self) -> float:
        """Get current ability estimate."""
        if self.session is None or self.session.current_ability is None:
            return 0.0
        return float(self.session.current_ability)

    def get_standard_error(self) -> Optional[Decimal]:
        """Get current standard error."""
        if self.session is None:
            return None
        return self.session.standard_error

    def get_questions_answered(self) -> int:
        """Get number of questions answered."""
        if self.session is None:
            return 0
        return self.session.questions_answered

    def is_session_complete(self) -> bool:
        """Check if the session is complete."""
        return self.session is not None and self.session.is_complete()


@dataclass
class Result:
    """Domain entity representing an assessment result."""
    
    id: str
    session_id: str
    proficiency_level: Optional[str]
    validated: bool
    skill_scores: Optional[Dict]
    overall_score: Optional[Decimal]
    result_type: str  
    information_metric: Optional[Dict]
    
    def validate(self) -> None:
        """Business rule: mark result as validated."""
        self.validated = True
    
    def is_placement(self) -> bool:
        return self.result_type == "P"
    
    def is_speaking(self) -> bool:
        return self.result_type == "S"
    
    def is_writing(self) -> bool:
        return self.result_type == "W"


