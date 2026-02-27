from typing import Dict, Any, List, Optional
import json
import os 
from datetime import datetime
from .base_agent import BaseAgent
from .planner_agent import PlannerAgent
from .evaluator_agent import EvaluatorAgent
from .tutor_agent import TutorAgent
from .scheduler_agent import SchedulerAgent
from .company_analyzer_agent import CompanyAnalyzerAgent
from .analytics_agent import AnalyticsAgent
from .recommender_agent import RecommenderAgent
from models.user_profile import UserProfile
import logging
import random

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Orchestrates communication and workflow between all agents"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents = {}
        self.session_history = []
        self.user_sessions = {}
        
        # Initialize all agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all agents with Gemini"""
        
        # Gemini configuration - using actual model name from your list
        gemini_config = {
            "provider": "google",
            "model": "models/gemini-2.5-flash",  # Using actual model name
            "temperature": 0.7,
            "generation_config": {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 4096,  # INCREASED for complex responses
            },
            "safety_settings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
        
        # Initialize ALL 8 agents
        self.agents["planner"] = PlannerAgent({"llm_config": gemini_config})
        self.agents["evaluator"] = EvaluatorAgent({"llm_config": gemini_config})
        self.agents["tutor"] = TutorAgent({"llm_config": gemini_config})
        self.agents["scheduler"] = SchedulerAgent({"llm_config": gemini_config})
        
        # NEW AGENTS
        self.agents["company_analyzer"] = CompanyAnalyzerAgent({"llm_config": gemini_config})
        self.agents["analytics"] = AnalyticsAgent({"llm_config": gemini_config})
        self.agents["recommender"] = RecommenderAgent({"llm_config": gemini_config})
        
        logger.info("All 8 agents initialized successfully")
    
    def create_learning_plan(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Create complete learning plan using planner agent"""
        
        logger.info(f"Creating learning plan for user: {user_profile.user_id}")
        
        # Prepare input for planner
        planner_input = {
            "user_id": user_profile.user_id,
            "user_profile": user_profile,
            "timestamp": datetime.now().isoformat()
        }
        
        # Get learning plan
        plan_result = self.agents["planner"].process(planner_input)
        
        if plan_result["status"] == "success":
            # Create schedule based on plan
            schedule_result = self.create_schedule(user_profile, plan_result["learning_plan"])
            
            # Combine results
            combined_result = {
                **plan_result,
                "schedule": schedule_result if schedule_result["status"] == "success" else None
            }
            
            # Store in session history
            self._store_session(
                user_id=user_profile.user_id,
                agent="planner",
                action="create_learning_plan",
                result=combined_result
            )
            
            return combined_result
        else:
            return plan_result
    
    def create_schedule(self, user_profile: UserProfile, learning_plan: Dict) -> Dict[str, Any]:
        """Create optimized schedule using scheduler agent"""
        
        logger.info(f"Creating schedule for user: {user_profile.user_id}")
        
        scheduler_input = {
            "user_id": user_profile.user_id,
            "user_profile": user_profile,
            "learning_plan": learning_plan,
            "constraints": self.config.get("scheduling_constraints", {}),
            "preferences": user_profile.preferences.__dict__ if hasattr(user_profile.preferences, '__dict__') else {},
            "timestamp": datetime.now().isoformat()
        }
        
        schedule_result = self.agents["scheduler"].process(scheduler_input)
        
        self._store_session(
            user_id=user_profile.user_id,
            agent="scheduler",
            action="create_schedule",
            result=schedule_result
        )
        
        return schedule_result
    
    def evaluate_response(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate user response using evaluator agent"""
        
        logger.info(f"Evaluating response for session: {evaluation_data.get('session_id')}")
        
        evaluation_result = self.agents["evaluator"].process(evaluation_data)
        
        if evaluation_result["status"] == "success":
            # Store evaluation
            self._store_session(
                user_id=evaluation_data.get("user_id"),
                agent="evaluator",
                action="evaluate_response",
                result=evaluation_result
            )
            
            # Check if tutoring is needed based on scores
            if evaluation_result["scores"]["overall"] < 7.0:
                tutoring_recommendation = self._generate_tutoring_recommendation(
                    evaluation_data, evaluation_result
                )
                evaluation_result["tutoring_recommendation"] = tutoring_recommendation
        
        return evaluation_result
    
    def provide_tutoring(self, tutoring_request: Dict[str, Any]) -> Dict[str, Any]:
        """Provide personalized tutoring using tutor agent"""
        
        logger.info(f"Providing tutoring for topic: {tutoring_request.get('topic')}")
        
        tutoring_result = self.agents["tutor"].process(tutoring_request)
        
        self._store_session(
            user_id=tutoring_request.get("user_id"),
            agent="tutor",
            action="provide_tutoring",
            result=tutoring_result
        )
        
        return tutoring_result
    
    def get_daily_session(self, user_id: str, date: str = None) -> Dict[str, Any]:
        """Get today's learning session"""
        
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # In a real implementation, this would fetch from the user's schedule
        # For now, generate a mock session
        
        mock_session = {
            "date": date,
            "sessions": [
                {
                    "time_slot": "08:00-09:30",
                    "topic": "Data Structures",
                    "activity_type": "theory_study",
                    "description": "Review arrays, linked lists, and hash tables",
                    "resources": ["textbook_chapter_3", "online_lectures"]
                },
                {
                    "time_slot": "19:00-20:30",
                    "topic": "Algorithm Problems",
                    "activity_type": "practice_problems",
                    "description": "Solve 3 medium difficulty problems on LeetCode",
                    "resources": ["leetcode_platform", "whiteboard"]
                }
            ],
            "total_time_minutes": 180,
            "focus_area": "Fundamentals"
        }
        
        return {
            "status": "success",
            "daily_session": mock_session,
            "motivational_quote": self._get_motivational_quote(),
            "progress_tip": "Remember to take short breaks between sessions"
        }
    
    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's progress summary"""
        
        user_sessions = [
            session for session in self.session_history 
            if session.get("user_id") == user_id
        ]
        
        if not user_sessions:
            return {"status": "error", "message": "No sessions found for user"}
        
        # Calculate metrics
        total_sessions = len(user_sessions)
        evaluation_sessions = [
            s for s in user_sessions 
            if s.get("agent") == "evaluator" and s.get("result", {}).get("scores")
        ]
        
        avg_score = 0
        if evaluation_sessions:
            avg_score = sum(
                s["result"]["scores"]["overall"] 
                for s in evaluation_sessions
            ) / len(evaluation_sessions)
        
        return {
            "status": "success",
            "user_id": user_id,
            "total_sessions": total_sessions,
            "evaluation_sessions": len(evaluation_sessions),
            "average_score": round(avg_score, 2),
            "last_session": user_sessions[-1]["timestamp"] if user_sessions else None,
            "recommended_actions": self._get_recommended_actions(user_sessions)
        }
    
    # ============= NEW METHODS FOR REVOLUTIONARY FEATURES =============
    
    def analyze_target_companies(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Analyze target companies using company analyzer agent"""
        
        logger.info(f"Analyzing target companies for user: {user_profile.user_id}")
        
        input_data = {
            "user_id": user_profile.user_id,
            "target_companies": user_profile.interview_goal.target_companies if user_profile.interview_goal else [],
            "target_role": user_profile.interview_goal.target_role if user_profile.interview_goal else "SDE",
            "timestamp": datetime.now().isoformat()
        }
        
        result = self.agents["company_analyzer"].process(input_data)
        
        self._store_session(
            user_id=user_profile.user_id,
            agent="company_analyzer",
            action="analyze_companies",
            result=result
        )
        
        return result

    def analyze_performance(self, user_id: str, session_history: List[Dict], user_profile: UserProfile) -> Dict[str, Any]:
        """Analyze performance and generate adaptations"""
        
        logger.info(f"Analyzing performance for user: {user_id}")
        
        input_data = {
            "user_id": user_id,
            "session_history": session_history,
            "user_profile": user_profile,
            "timestamp": datetime.now().isoformat()
        }
        
        result = self.agents["analytics"].process(input_data)
        
        self._store_session(
            user_id=user_id,
            agent="analytics",
            action="analyze_performance",
            result=result
        )
        
        return result

    def get_next_recommendation(self, user_id: str, current_context: Dict, 
                               user_profile: UserProfile, roadmap: Dict) -> Dict[str, Any]:
        """Get next learning recommendation"""
        
        logger.info(f"Getting next recommendation for user: {user_id}")
        
        # Get recent performance
        user_sessions = [s for s in self.session_history if s.get("user_id") == user_id]
        
        input_data = {
            "user_id": user_id,
            "current_context": current_context,
            "user_profile": user_profile,
            "recent_performance": self._extract_recent_performance(user_sessions),
            "roadmap": roadmap,
            "timestamp": datetime.now().isoformat()
        }
        
        result = self.agents["recommender"].process(input_data)
        
        self._store_session(
            user_id=user_id,
            agent="recommender",
            action="get_recommendation",
            result=result
        )
        
        return result

    def run_complete_onboarding(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Run complete onboarding workflow with all agents"""
        
        logger.info(f"Running complete onboarding for user: {user_profile.user_id}")
        
        # Step 1: Analyze target companies
        company_analysis = self.analyze_target_companies(user_profile)
        
        if company_analysis["status"] != "success":
            return company_analysis
        
        # Step 2: Create learning plan (incorporating company insights)
        plan_result = self.create_learning_plan(user_profile)
        
        if plan_result["status"] != "success":
            return plan_result
        
        # Step 3: Run initial performance analysis
        initial_analytics = self.analyze_performance(
            user_profile.user_id, 
            self.session_history,
            user_profile
        )
        
        # Step 4: Get first recommendation
        first_recommendation = self.get_next_recommendation(
            user_profile.user_id,
            {"stage": "onboarding", "completed": False},
            user_profile,
            plan_result.get("learning_plan", {})
        )
        
        return {
            "status": "success",
            "onboarding_complete": True,
            "user_id": user_profile.user_id,
            "company_insights": company_analysis,
            "learning_plan": plan_result,
            "initial_analytics": initial_analytics,
            "first_recommendation": first_recommendation,
            "next_steps": "Begin with your first recommended session"
        }

    def run_daily_cycle(self, user_id: str) -> Dict[str, Any]:
        """Run complete daily learning cycle"""
        
        logger.info(f"Running daily cycle for user: {user_id}")
        
        # Get user profile and sessions
        user_profile = self.user_sessions.get(user_id)
        if not user_profile:
            return {"status": "error", "message": "User not found"}
        
        user_sessions = [s for s in self.session_history if s.get("user_id") == user_id]
        
        # Step 1: Get current context
        current_context = {
            "time_of_day": datetime.now().hour,
            "recent_sessions": len(user_sessions[-3:]) if user_sessions else 0,
            "last_session_time": user_sessions[-1]["timestamp"] if user_sessions else None
        }
        
        # Step 2: Get recommendation for today
        recommendation = self.get_next_recommendation(
            user_id,
            current_context,
            user_profile,
            {}  # Would pass actual roadmap
        )
        
        # Step 3: Get today's schedule
        daily_session = self.get_daily_session(user_id)
        
        # Step 4: Analyze performance if there's data
        analytics = None
        if user_sessions:
            analytics = self.analyze_performance(user_id, user_sessions, user_profile)
        
        return {
            "status": "success",
            "user_id": user_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "recommendation": recommendation,
            "schedule": daily_session,
            "analytics": analytics,
            "motivation": self._get_motivational_quote()
        }

    def _extract_recent_performance(self, user_sessions: List[Dict]) -> Dict[str, Any]:
        """Extract recent performance metrics"""
        
        eval_sessions = [
            s for s in user_sessions[-5:] 
            if s.get("agent") == "evaluator" and s.get("result", {}).get("scores")
        ]
        
        if not eval_sessions:
            return {
                "needs_review": False,
                "ready_to_advance": False,
                "weak_topic": None
            }
        
        last_eval = eval_sessions[-1]
        scores = last_eval.get("result", {}).get("scores", {})
        overall = scores.get("overall", 0)
        
        # Determine needs
        needs_review = overall < 6
        ready_to_advance = overall > 8
        
        # Find weak topic
        improvement_areas = last_eval.get("result", {}).get("improvement_areas", [])
        weak_topic = improvement_areas[0].get("category") if improvement_areas else None
        
        return {
            "needs_review": needs_review,
            "ready_to_advance": ready_to_advance,
            "weak_topic": weak_topic,
            "last_score": overall,
            "trend": "improving" if len(eval_sessions) > 1 and eval_sessions[-1]["result"]["scores"]["overall"] > eval_sessions[-2]["result"]["scores"]["overall"] else "stable"
        }
    
    # ============= EXISTING HELPER METHODS =============
    
    def _generate_tutoring_recommendation(self, evaluation_data: Dict, 
                                        evaluation_result: Dict) -> Dict[str, Any]:
        """Generate tutoring recommendation based on evaluation"""
        
        weak_areas = evaluation_result.get("improvement_areas", [])
        
        if not weak_areas:
            return None
        
        # Get the highest priority weak area
        top_weak_area = weak_areas[0]
        
        return {
            "recommended": True,
            "reason": f"Low score in {top_weak_area['category']}",
            "topic": top_weak_area["category"].lower(),
            "priority": top_weak_area["priority"],
            "estimated_time": "60 minutes",
            "suggested_method": "interactive_exercises"
        }
    
    def _store_session(self, user_id: str, agent: str, action: str, result: Dict):
        """Store session in history"""
        
        session_record = {
            "session_id": f"session_{len(self.session_history) + 1:06d}",
            "user_id": user_id,
            "agent": agent,
            "action": action,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        self.session_history.append(session_record)
        
        # Keep only last 1000 sessions
        if len(self.session_history) > 1000:
            self.session_history = self.session_history[-1000:]
    
    def _get_motivational_quote(self) -> Dict[str, str]:
        """Get motivational quote"""
        
        quotes = [
            {
                "quote": "The only way to do great work is to love what you do.",
                "author": "Steve Jobs"
            },
            {
                "quote": "Success is not final, failure is not fatal: it is the courage to continue that counts.",
                "author": "Winston Churchill"
            },
            {
                "quote": "The future depends on what you do today.",
                "author": "Mahatma Gandhi"
            },
            {
                "quote": "Don't watch the clock; do what it does. Keep going.",
                "author": "Sam Levenson"
            },
            {
                "quote": "Your only limit is your mind.",
                "author": "Unknown"
            }
        ]
        
        return random.choice(quotes)
    
    def _get_recommended_actions(self, user_sessions: List[Dict]) -> List[str]:
        """Get recommended actions based on user sessions"""
        
        recommendations = []
        
        # Check if user needs more practice
        eval_sessions = [s for s in user_sessions if s["agent"] == "evaluator"]
        if len(eval_sessions) < 3:
            recommendations.append("Schedule more mock interview sessions")
        
        # Check last session date
        if user_sessions:
            last_session = datetime.fromisoformat(user_sessions[-1]["timestamp"])
            days_since = (datetime.now() - last_session).days
            
            if days_since > 2:
                recommendations.append(f"Resume practice - it's been {days_since} days")
        
        # Check for variety
        agent_counts = {}
        for session in user_sessions[-10:]:  # Last 10 sessions
            agent = session["agent"]
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
        
        if "tutor" not in agent_counts:
            recommendations.append("Try a tutoring session for difficult topics")
        
        # Add analytics recommendation if available
        if "analytics" in agent_counts:
            recommendations.append("Check your performance analytics for insights")
        
        return recommendations[:3]