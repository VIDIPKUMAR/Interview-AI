from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from .base_agent import BaseAgent
from utils.llm_client import LLMClient

class RecommenderAgent(BaseAgent):
    """Context-aware recommender for next learning actions and problems"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            agent_id="recommender_001",
            name="Context Recommender",
            description="Suggests what to study next based on context and recommends problems",
            config=config
        )
        self.llm_client = LLMClient(**config.get("llm_config", {}))
        self.recommendation_history = []  # Track past recommendations
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend next learning actions"""
        self.log(f"Generating recommendations for user: {input_data.get('user_id')}")
        
        try:
            current_context = input_data.get("current_context", {})
            user_profile = input_data.get("user_profile")
            recent_performance = input_data.get("recent_performance", {})
            roadmap = input_data.get("roadmap", {})
            
            # Determine recommendation type
            recommendation = self._generate_recommendation(
                context=current_context,
                performance=recent_performance,
                user_profile=user_profile,
                roadmap=roadmap
            )
            
            # Get alternative options
            alternatives = self._generate_alternatives(recommendation, roadmap)
            
            response = {
                "status": "success",
                "recommendation_id": f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "primary_recommendation": recommendation,
                "alternatives": alternatives,
                "reasoning": self._generate_reasoning(recommendation, current_context, recent_performance),
                "estimated_impact": self._estimate_impact(recommendation, user_profile)
            }
            
            self.update_memory({
                "action": "generated_recommendation",
                "type": recommendation.get("type"),
                "confidence": recommendation.get("confidence")
            })
            
            return response
            
        except Exception as e:
            self.log(f"Error in recommendation: {str(e)}", "ERROR")
            return self._create_error_response(str(e))
    
    def _generate_recommendation(self, context: Dict, performance: Dict,
                                user_profile: Any, roadmap: Dict) -> Dict[str, Any]:
        """Generate primary recommendation"""
        
        # Check for immediate needs
        if performance.get("needs_review", False):
            return self._create_review_recommendation(performance)
        
        # Check for stuck state
        if context.get("stuck_on_topic"):
            return self._create_unblock_recommendation(context)
        
        # Check for optimal advancement
        if performance.get("ready_to_advance", False):
            return self._create_advance_recommendation(performance, roadmap)
        
        # Default: follow roadmap
        return self._create_follow_roadmap_recommendation(context, roadmap)
    
    def _create_review_recommendation(self, performance: Dict) -> Dict[str, Any]:
        """Create review recommendation"""
        return {
            "type": "review",
            "action": "Review weak concepts",
            "topic": performance.get("weak_topic", "previous material"),
            "confidence": 0.9,
            "duration_minutes": 30,
            "format": "mixed",
            "resources": [
                {"type": "video", "topic": performance.get("weak_topic"), "duration": 10},
                {"type": "practice", "count": 3, "difficulty": "easy"}
            ],
            "success_criteria": "Score >80% on quick assessment"
        }
    
    def _create_unblock_recommendation(self, context: Dict) -> Dict[str, Any]:
        """Create recommendation for unblocking"""
        return {
            "type": "unblock",
            "action": "Get unstuck",
            "topic": context.get("stuck_on_topic"),
            "confidence": 0.85,
            "duration_minutes": 45,
            "format": "tutorial",
            "resources": [
                {"type": "visual_explanation", "topic": context.get("stuck_on_topic")},
                {"type": "step_by_step", "complexity": "simplified"},
                {"type": "practice", "count": 2, "difficulty": "beginner"}
            ],
            "success_criteria": "Able to explain concept and solve basic problem"
        }
    
    def _create_advance_recommendation(self, performance: Dict, roadmap: Dict) -> Dict[str, Any]:
        """Create advancement recommendation"""
        next_topic = self._find_next_topic(performance.get("current_topic"), roadmap)
        
        return {
            "type": "advance",
            "action": "Learn new concept",
            "topic": next_topic,
            "confidence": 0.8,
            "duration_minutes": 60,
            "format": "structured",
            "resources": [
                {"type": "concept_intro", "topic": next_topic, "duration": 20},
                {"type": "examples", "count": 3},
                {"type": "practice", "count": 3, "difficulty": "medium"}
            ],
            "success_criteria": "Solve 2/3 practice problems correctly"
        }
    
    def _create_follow_roadmap_recommendation(self, context: Dict, roadmap: Dict) -> Dict[str, Any]:
        """Create recommendation to follow roadmap"""
        # Get current day's planned topic
        today = datetime.now().strftime("%Y-%m-%d")
        planned_topic = self._get_planned_topic(today, roadmap)
        
        return {
            "type": "follow_plan",
            "action": "Continue with planned study",
            "topic": planned_topic or "next scheduled topic",
            "confidence": 0.7,
            "duration_minutes": 90,
            "format": "mixed",
            "resources": [
                {"type": "study", "topic": planned_topic},
                {"type": "practice", "count": 3}
            ],
            "success_criteria": "Complete planned session"
        }
    
    def _generate_alternatives(self, primary: Dict, roadmap: Dict) -> List[Dict]:
        """Generate alternative recommendations"""
        
        alternatives = []
        
        # Alternative: lighter session
        alternatives.append({
            "type": "light",
            "action": "Light review session",
            "topic": "previous topics",
            "duration_minutes": 30,
            "format": "quick_review",
            "resources": [{"type": "flashcards", "count": 20}]
        })
        
        # Alternative: deeper dive
        if primary.get("topic"):
            alternatives.append({
                "type": "deep",
                "action": "Deep dive",
                "topic": primary.get("topic"),
                "duration_minutes": 120,
                "format": "comprehensive",
                "resources": [{"type": "advanced", "topic": primary.get("topic")}]
            })
        
        # Alternative: different format
        if primary.get("format") != "video":
            alternatives.append({
                "type": "video",
                "action": "Video tutorial",
                "topic": primary.get("topic"),
                "duration_minutes": 45,
                "format": "video",
                "resources": [{"type": "video_lecture", "duration": 30}]
            })
        
        return alternatives[:3]
    
    def _generate_reasoning(self, recommendation: Dict, context: Dict, 
                           performance: Dict) -> str:
        """Generate reasoning for recommendation"""
        
        if recommendation["type"] == "review":
            return f"Based on your performance, you'd benefit from reviewing {recommendation['topic']} to strengthen your foundation."
        
        elif recommendation["type"] == "unblock":
            return f"You've been working on {recommendation['topic']} for a while. Let's try a different approach to get unstuck."
        
        elif recommendation["type"] == "advance":
            return f"You've mastered the prerequisites. Now's the perfect time to tackle {recommendation['topic']}."
        
        else:
            return f"Following your learning plan keeps you on track for your target date."
    
    def _estimate_impact(self, recommendation: Dict, user_profile: Any) -> Dict[str, Any]:
        """Estimate impact of following recommendation"""
        
        base_impact = {
            "review": {"score_improvement": "+0.5", "confidence_boost": "medium"},
            "unblock": {"progress_unblocked": True, "momentum_restored": "high"},
            "advance": {"topic_progress": "+1", "skill_acquisition": "new_concept"},
            "follow_plan": {"consistency_maintained": True, "on_track": True}
        }
        
        impact_type = base_impact.get(recommendation["type"], {})
        
        return {
            "expected_outcome": impact_type,
            "time_investment": f"{recommendation.get('duration_minutes', 60)} minutes",
            "readiness_impact": "+2%" if recommendation["type"] in ["advance", "review"] else "+1%"
        }
    
    # ============= NEW METHODS FOR PROBLEM RECOMMENDATION =============
    
    def get_problem_recommendation(self, user_id: str, user_profile: Dict, 
                                   target_companies: List[str]) -> Dict[str, Any]:
        """
        Get personalized problem recommendation based on user profile and target companies
        """
        self.log(f"Getting problem recommendation for user: {user_id}")
        
        try:
            from .problem_router import ProblemRouter
            router = ProblemRouter()
            
            # Get user's weak areas from history
            weak_areas = self._identify_weak_areas(user_id)
            
            # Get recommendation from router
            recommendation = router.get_recommendation(
                user_profile=user_profile,
                weak_areas=weak_areas,
                target_companies=target_companies,
                difficulty_pref=user_profile.get("difficulty_preference", "adaptive")
            )
            
            # Track recommendation for analytics
            self._track_recommendation(user_id, recommendation)
            
            return {
                "status": "success",
                "user_id": user_id,
                "recommendation": recommendation,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.log(f"Error in problem recommendation: {str(e)}", "ERROR")
            return self._create_error_response(str(e))
    
    def _identify_weak_areas(self, user_id: str) -> List[str]:
        """Identify user's weak areas from performance history"""
        
        # Check memory for recent evaluations
        weak_areas = set()
        
        for memory in self.memory[-10:]:  # Check last 10 memories
            if memory.get("action") == "evaluated_response":
                improvement_areas = memory.get("improvement_areas", [])
                for area in improvement_areas:
                    if isinstance(area, dict):
                        weak_areas.add(area.get("category", "").lower())
                    elif isinstance(area, str):
                        weak_areas.add(area.lower())
        
        # If no weak areas found, return defaults based on common challenging topics
        if not weak_areas:
            return ["dynamic-programming", "graphs", "trees"]
        
        return list(weak_areas)[:3]  # Return top 3 weak areas
    
    def _track_recommendation(self, user_id: str, recommendation: Dict):
        """Track recommendation for analytics"""
        
        self.update_memory({
            "action": "problem_recommended",
            "user_id": user_id,
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat()
        })
    
    def _find_next_topic(self, current_topic: str, roadmap: Dict) -> str:
        """Find next topic in roadmap"""
        # Simplified - would need actual roadmap structure
        common_progressions = {
            "arrays": "strings",
            "strings": "linked_lists",
            "linked_lists": "trees",
            "trees": "graphs",
            "graphs": "dynamic_programming",
            "dynamic-programming": "advanced_dp",
            "hash-table": "hash-map",
            "stack": "queue",
            "recursion": "backtracking"
        }
        
        return common_progressions.get(current_topic, "next_scheduled_topic")
    
    def _get_planned_topic(self, date: str, roadmap: Dict) -> Optional[str]:
        """Get planned topic for date from roadmap"""
        # This would extract from actual roadmap structure
        # For now, return placeholder
        if roadmap and "phases" in roadmap:
            # Logic to get topic for specific date
            pass
        return "data_structures"
    
    def get_recommendation_history(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get past recommendations for a user"""
        
        history = []
        for memory in self.memory[-50:]:  # Check last 50 memories
            if memory.get("action") == "problem_recommended" and memory.get("user_id") == user_id:
                history.append({
                    "timestamp": memory.get("timestamp"),
                    "recommendation": memory.get("recommendation")
                })
        
        return history[-limit:]  # Return most recent
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "status": "error",
            "error": error_message,
            "timestamp": self._get_timestamp()
        }