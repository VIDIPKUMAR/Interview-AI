from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from utils.llm_client import LLMClient
from models.user_profile import UserProfile, InterviewGoal, Skill

class PlannerAgent(BaseAgent):
    """Creates personalized learning paths based on user goals and skills"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            agent_id="planner_001",
            name="Learning Path Planner",
            description="Creates personalized interview preparation plans",
            config=config
        )
        self.llm_client = LLMClient(**config.get("llm_config", {}))
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process planning request"""
        self.log(f"Processing planning request for user: {input_data.get('user_id')}")
        
        user_profile = input_data.get("user_profile")
        if not user_profile:
            return self._create_error_response("User profile is required")
        
        try:
            # Generate personalized learning plan
            learning_plan = self._generate_learning_plan(user_profile)
            
            # Create detailed weekly schedule
            weekly_schedule = self._create_weekly_schedule(learning_plan, user_profile)
            
            # Calculate timeline and milestones
            milestones = self._calculate_milestones(user_profile.interview_goal.timeline_weeks)
            
            response = {
                "status": "success",
                "plan_id": f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "learning_plan": learning_plan,
                "weekly_schedule": weekly_schedule,
                "milestones": milestones,
                "recommendations": self._generate_recommendations(user_profile),
                "estimated_preparation_time": self._estimate_preparation_time(user_profile)
            }
            
            self.update_memory({
                "action": "created_learning_plan",
                "user_id": user_profile.user_id,
                "plan_id": response["plan_id"]
            })
            
            return response
            
        except Exception as e:
            self.log(f"Error in planning: {str(e)}", "ERROR")
            return self._create_error_response(str(e))
    
    def _generate_learning_plan(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Generate personalized learning plan"""
        
        system_prompt = """You are an expert interview preparation coach. Create personalized learning paths for technical interview preparation.
        Consider the user's current skills, target role, timeline, and learning preferences."""
        
        # Safely get values from enums or objects
        learning_style = user_profile.preferences.preferred_learning_style
        if hasattr(learning_style, 'value'):
            learning_style_value = learning_style.value
        else:
            learning_style_value = str(learning_style)
        
        user_prompt = f"""
        Create a comprehensive interview preparation plan for the following user:
        
        Current Role: {user_profile.current_role or 'Not specified'}
        Experience: {user_profile.experience_years} years
        Target Role: {user_profile.interview_goal.target_role}
        Target Companies: {', '.join(user_profile.interview_goal.target_companies)}
        Timeline: {user_profile.interview_goal.timeline_weeks} weeks
        Interview Types: {', '.join(user_profile.interview_goal.interview_types)}
        
        Current Skills:
        {self._format_skills_for_prompt(user_profile.skills)}
        
        Learning Style: {learning_style_value}
        Daily Practice Time: {user_profile.preferences.daily_practice_time_minutes} minutes
        
        Create a phased learning plan with:
        1. Foundation Phase (weeks 1-2)
        2. Core Competency Phase (weeks 3-5)
        3. Advanced & Mock Interview Phase (weeks 6-8)
        4. Final Review & Strategy Phase (last week)
        
        For each phase, include:
        - Key focus areas
        - Recommended resources
        - Practice exercises
        - Success metrics
        """
        
        plan_schema = {
            "type": "object",
            "properties": {
                "phases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "phase_name": {"type": "string"},
                            "duration_weeks": {"type": "integer"},
                            "focus_areas": {"type": "array", "items": {"type": "string"}},
                            "learning_objectives": {"type": "array", "items": {"type": "string"}},
                            "resources": {"type": "array", "items": {"type": "string"}},
                            "practice_exercises": {"type": "array", "items": {"type": "string"}},
                            "success_metrics": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                },
                "total_duration_weeks": {"type": "integer"},
                "key_milestones": {"type": "array", "items": {"type": "string"}}
            }
        }
        
        return self.llm_client.generate_structured_output(
            prompt=user_prompt,
            output_schema=plan_schema,
            system_message=system_prompt
        )
    
    def _create_weekly_schedule(self, learning_plan: Dict, user_profile: UserProfile) -> List[Dict]:
        """Create detailed weekly schedule"""
        weekly_schedule = []
        current_week = 1
        
        for phase in learning_plan.get("phases", []):
            for week_offset in range(phase["duration_weeks"]):
                week_plan = {
                    "week_number": current_week,
                    "phase": phase["phase_name"],
                    "focus_areas": phase["focus_areas"],
                    "daily_schedule": self._create_daily_schedule(
                        week_number=current_week,
                        focus_areas=phase["focus_areas"],
                        user_profile=user_profile
                    ),
                    "weekly_goals": phase.get("learning_objectives", []),
                    "resources": phase.get("resources", []),
                    "mock_interview_week": current_week % 2 == 0  # Every other week
                }
                weekly_schedule.append(week_plan)
                current_week += 1
                
        return weekly_schedule
    
    def _create_daily_schedule(self, week_number: int, focus_areas: List[str], 
                              user_profile: UserProfile) -> Dict[str, Any]:
        """Create daily schedule for a week"""
        daily_minutes = user_profile.preferences.daily_practice_time_minutes
        
        # Safely get learning style
        learning_style = user_profile.preferences.preferred_learning_style
        if hasattr(learning_style, 'value'):
            learning_style_value = learning_style.value
        else:
            learning_style_value = str(learning_style)
        
        # Allocate time based on learning style
        if learning_style_value == "visual":
            schedule = {
                "theory_study": daily_minutes * 0.3,
                "video_tutorials": daily_minutes * 0.4,
                "practice_problems": daily_minutes * 0.3
            }
        elif learning_style_value == "auditory":
            schedule = {
                "podcasts_audio": daily_minutes * 0.4,
                "theory_study": daily_minutes * 0.2,
                "practice_problems": daily_minutes * 0.4
            }
        else:
            schedule = {
                "theory_study": daily_minutes * 0.25,
                "practice_problems": daily_minutes * 0.5,
                "review_revision": daily_minutes * 0.25
            }
        
        return {
            "total_daily_minutes": daily_minutes,
            "time_allocation": schedule,
            "daily_topics": focus_areas[:2] if len(focus_areas) >= 2 else focus_areas,
            "recommended_session_times": user_profile.preferences.preferred_session_times
        }
    
    def _calculate_milestones(self, total_weeks: int) -> List[Dict]:
        """Calculate preparation milestones"""
        milestones = []
        week_intervals = max(1, total_weeks // 4)
        
        for i in range(1, 5):
            week = i * week_intervals
            milestone = {
                "week": week,
                "description": f"Complete Phase {i} preparation",
                "assessment_required": True,
                "success_criteria": f"Score >80% on Phase {i} assessment"
            }
            milestones.append(milestone)
        
        return milestones
    
    def _generate_recommendations(self, user_profile: UserProfile) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Skill gap recommendations
        for skill in user_profile.skills:
            if skill.confidence_score < 0.6:
                recommendations.append(
                    f"Focus on improving {skill.name} (current confidence: {skill.confidence_score:.0%})"
                )
        
        # Timeline recommendations
        if user_profile.interview_goal.timeline_weeks < 4:
            recommendations.append(
                "Consider extending your timeline for more comprehensive preparation"
            )
        
        # Resource recommendations based on target companies
        target_companies_str = str(user_profile.interview_goal.target_companies)
        if "FAANG" in target_companies_str or any(company in target_companies_str for company in ["Google", "Facebook", "Amazon", "Apple", "Netflix"]):
            recommendations.append(
                "Focus on system design and algorithmic problem-solving for FAANG interviews"
            )
        
        return recommendations
    
    def _estimate_preparation_time(self, user_profile: UserProfile) -> Dict[str, Any]:
     
     """Estimate total preparation time needed"""
     daily_mins = user_profile.preferences.daily_practice_time_minutes
     total_weeks = user_profile.interview_goal.timeline_weeks
    
        # Convert to proper types
     daily_mins = float(daily_mins) if daily_mins else 60.0
     total_weeks = int(total_weeks) if total_weeks else 8
    
     total_hours = (daily_mins * 5 * total_weeks) / 60  # 5 days per week
    
     return {
        "total_hours": round(total_hours, 1),
        "hours_per_week": round(total_hours / total_weeks, 1),
        "daily_minutes": int(daily_mins),
        "estimated_completion_date": (
            datetime.now() + timedelta(weeks=total_weeks)
        ).strftime("%Y-%m-%d")
    }
    
    def _format_skills_for_prompt(self, skills: List[Skill]) -> str:
        """Format skills for LLM prompt"""
        skill_strings = []
        for skill in skills:
            # Safely get skill level values
            current_level = skill.current_level
            target_level = skill.target_level
            
            if hasattr(current_level, 'value'):
                current_level_str = current_level.value
            else:
                current_level_str = str(current_level)
                
            if hasattr(target_level, 'value'):
                target_level_str = target_level.value
            else:
                target_level_str = str(target_level)
                
            skill_strings.append(
                f"- {skill.name}: {current_level_str} → {target_level_str} (confidence: {skill.confidence_score:.0%})"
            )
        
        return "\n".join(skill_strings)
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "status": "error",
            "error": error_message,
            "timestamp": self._get_timestamp()
        }
