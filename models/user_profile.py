from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from enum import Enum
import json

class SkillLevel(Enum):
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class LearningStyle(Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READ_WRITE = "read_write"

@dataclass
class Skill:
    """Represents a skill with proficiency level"""
    name: str
    category: str  # e.g., "programming", "soft_skills", "domain_knowledge"
    current_level: SkillLevel
    target_level: SkillLevel
    confidence_score: float = 0.0  # 0-1
    last_practiced: Optional[datetime] = None
    practice_count: int = 0

@dataclass
class InterviewGoal:
    """User's interview preparation goal"""
    target_role: str
    target_companies: List[str]
    target_salary_range: Optional[Dict[str, float]] = None
    timeline_weeks: int = 8
    interview_types: List[str] = field(default_factory=lambda: ["technical", "behavioral"])
    priority_skills: List[str] = field(default_factory=list)

@dataclass
class UserPreferences:
    """User preferences for learning"""
    preferred_learning_style: LearningStyle = LearningStyle.VISUAL
    daily_practice_time_minutes: int = 60
    preferred_session_times: List[str] = field(default_factory=lambda: ["morning", "evening"])
    difficulty_preference: str = "adaptive"
    feedback_detail_level: str = "detailed"  # "brief", "detailed", "comprehensive"
    
@dataclass
class PerformanceMetrics:
    """Track user performance metrics"""
    total_sessions: int = 0
    average_score: float = 0.0
    strongest_skill_category: Optional[str] = None
    weakest_skill_category: Optional[str] = None
    consistency_score: float = 0.0  # 0-1
    improvement_rate: float = 0.0  # percentage

@dataclass
class UserProfile:
    """Complete user profile"""
    user_id: str
    name: str
    email: str
    experience_years: int
    current_role: Optional[str] = None
    skills: List[Skill] = field(default_factory=list)
    interview_goal: Optional[InterviewGoal] = None
    preferences: UserPreferences = field(default_factory=UserPreferences)
    performance_metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "experience_years": self.experience_years,
            "current_role": self.current_role,
            "skills": [
                {
                    "name": skill.name,
                    "category": skill.category,
                    "current_level": skill.current_level.value,
                    "target_level": skill.target_level.value,
                    "confidence_score": skill.confidence_score,
                    "practice_count": skill.practice_count
                }
                for skill in self.skills
            ],
            "interview_goal": {
                "target_role": self.interview_goal.target_role,
                "target_companies": self.interview_goal.target_companies,
                "timeline_weeks": self.interview_goal.timeline_weeks,
                "interview_types": self.interview_goal.interview_types
            } if self.interview_goal else None,
            "preferences": {
                "preferred_learning_style": self.preferences.preferred_learning_style.value,
                "daily_practice_time_minutes": self.preferences.daily_practice_time_minutes,
                "preferred_session_times": self.preferences.preferred_session_times,
                "difficulty_preference": self.preferences.difficulty_preference
            },
            "performance_metrics": asdict(self.performance_metrics),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create UserProfile from dictionary"""
        # Implementation for deserialization
        pass