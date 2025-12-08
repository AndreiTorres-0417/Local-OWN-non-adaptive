from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class AssessmentItem:
    """Value Object representing an assessment item/question."""
    
    id: str
    content: Dict
    item_type: str
    skill_area: List[str]
    target_proficiency_level: str
    parameters: Dict[str, float]
    is_active: bool = True
     
    @property
    def difficulty(self) -> float:
        """IRT parameter: difficulty of the item."""
        return self.parameters.get('difficulty', 0.0)
    
    @property
    def discrimination(self) -> float:
        """IRT parameter: discrimination of the item."""
        return self.parameters.get('discrimination', 1.0)
    
    @property
    def guessing(self) -> float:
        """IRT parameter: guessing parameter of the item."""
        return self.parameters.get('guessing', 0.25)


@dataclass(frozen=True)
class AssessmentTemplate:
    """Value Object representing an assessment template definition."""
    
    id: str
    learning_pathway_id: str
    name: str
    assessment_type: str  
    rubric: Optional[Dict]
    meta: Optional[Dict]
    version: int
    is_active: bool = True
    
    @property
    def is_placement(self) -> bool:
        return self.assessment_type == "PLACEMENT"
    
    @property
    def is_speaking(self) -> bool:
        return self.assessment_type == "SPEAKING"
    
    @property
    def is_writing(self) -> bool:
        return self.assessment_type == "WRITING"
    
    @property
    def proficiency_levels(self) -> List[str]:
        """Get proficiency levels from rubric."""
        if self.rubric and "proficiency_levels" in self.rubric:
            return self.rubric["proficiency_levels"]
        return ["A1", "A2", "B1", "B2", "C1", "C2"]


@dataclass(frozen=True)
class AssessmentConfig:
    """Value Object representing assessment configuration parameters."""
    
    id: str
    template_id: str
    parameters: Optional[Dict]
    adaptive_params: Optional[Dict]
    speaking_params: Optional[Dict]
    writing_params: Optional[Dict]
    is_active: bool = True
    
    @property
    def starting_ability(self) -> float:
        """Get starting ability for adaptive tests."""
        if self.adaptive_params:
            return self.adaptive_params.get("starting_ability", 0.0)
        return 0.0
    
    @property
    def min_questions(self) -> int:
        """Get minimum questions for adaptive tests."""
        if self.adaptive_params:
            return self.adaptive_params.get("min_questions", 5)
        return 5
    
    @property
    def max_questions(self) -> int:
        """Get maximum questions for adaptive tests."""
        if self.adaptive_params:
            return self.adaptive_params.get("max_questions", 25)
        return 25
    
    @property
    def stopping_criterion(self) -> Dict:
        """Get stopping criterion for adaptive tests."""
        if self.adaptive_params:
            return self.adaptive_params.get("stopping_criterion", {"standard_error": 0.3})
        return {"standard_error": 0.3}
    
    @property
    def skill_areas(self) -> List[str]:
        """Get skill areas for adaptive tests."""
        if self.adaptive_params:
            return self.adaptive_params.get("skill_areas", [])
        return []
    
    @property
    def proficiency_range(self) -> Dict:
        """Get proficiency range mapping for adaptive tests."""
        if self.adaptive_params:
            return self.adaptive_params.get("proficiency_range", {})
        return {}
    
    def get_stopping_standard_error(self) -> float:
        """Get the standard error threshold for stopping."""
        return self.stopping_criterion.get("standard_error", 0.3)
    
    def has_valid_question_limits(self) -> bool:
        """Validate question limits."""
        return self.min_questions <= self.max_questions



