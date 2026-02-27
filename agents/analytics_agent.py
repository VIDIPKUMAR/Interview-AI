from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from utils.llm_client import LLMClient
import statistics

class AnalyticsAgent(BaseAgent):
    """Tracks performance and adapts the entire system"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            agent_id="analytics_001",
            name="Performance Analytics Engine",
            description="Analyzes patterns and adapts learning strategy",
            config=config
        )
        self.llm_client = LLMClient(**config.get("llm_config", {}))
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process performance data and generate adaptations"""
        self.log(f"Analyzing performance for user: {input_data.get('user_id')}")
        
        user_id = input_data.get("user_id")
        session_history = input_data.get("session_history", [])
        current_profile = input_data.get("user_profile")
        
        try:
            # Analyze performance patterns
            patterns = self._analyze_patterns(session_history)
            
            # Calculate metrics
            metrics = self._calculate_metrics(session_history)
            
            # Generate adaptations
            adaptations = self._generate_adaptations(patterns, metrics, current_profile)
            
            # Predict future performance
            predictions = self._generate_predictions(metrics, patterns)
            
            # Generate comprehensive report
            report = self._generate_report(metrics, patterns, predictions)
            
            response = {
                "status": "success",
                "analytics_id": f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "performance_patterns": patterns,
                "metrics": metrics,
                "adaptations": adaptations,
                "predictions": predictions,
                "report": report,
                "recommended_focus": self._get_recommended_focus(patterns, metrics)
            }
            
            self.update_memory({
                "action": "analyzed_performance",
                "user_id": user_id,
                "patterns_found": len(patterns)
            })
            
            return response
            
        except Exception as e:
            self.log(f"Error in analytics: {str(e)}", "ERROR")
            return self._create_error_response(str(e))
    
    def _analyze_patterns(self, session_history: List[Dict]) -> Dict[str, Any]:
        """Analyze performance patterns over time"""
        
        if not session_history:
            return {"error": "No session data available"}
        
        # Extract evaluation sessions
        eval_sessions = [
            s for s in session_history 
            if s.get("agent") == "evaluator" and s.get("result", {}).get("scores")
        ]
        
        if not eval_sessions:
            return {"error": "No evaluation data available"}
        
        # Analyze accuracy trends
        accuracy_trend = []
        speed_trend = []
        topic_mastery = {}
        error_patterns = []
        
        for session in eval_sessions[-20:]:  # Last 20 sessions
            result = session.get("result", {})
            scores = result.get("scores", {})
            
            # Accuracy trend
            accuracy_trend.append(scores.get("overall", 0))
            
            # Speed trend (could be stored in session)
            speed_trend.append(result.get("time_taken", 30))
            
            # Topic mastery
            topic = session.get("topic", "unknown")
            if topic not in topic_mastery:
                topic_mastery[topic] = []
            topic_mastery[topic].append(scores.get("overall", 0))
            
            # Error patterns
            improvement_areas = result.get("improvement_areas", [])
            for area in improvement_areas:
                error_patterns.append(area.get("category", "unknown"))
        
        # Calculate topic averages
        topic_averages = {}
        for topic, scores in topic_mastery.items():
            if scores:
                topic_averages[topic] = sum(scores) / len(scores)
        
        # Find most common errors
        from collections import Counter
        error_counter = Counter(error_patterns)
        most_common_errors = error_counter.most_common(5)
        
        # Detect learning rate
        if len(accuracy_trend) >= 5:
            initial_avg = sum(accuracy_trend[:3]) / 3
            recent_avg = sum(accuracy_trend[-3:]) / 3
            learning_rate = (recent_avg - initial_avg) / initial_avg if initial_avg > 0 else 0
        else:
            learning_rate = 0
        
        # Detect plateaus
        plateau_detected = False
        if len(accuracy_trend) >= 7:
            last_7 = accuracy_trend[-7:]
            if max(last_7) - min(last_7) < 5:  # Less than 5% variation
                plateau_detected = True
        
        return {
            "accuracy_trend": accuracy_trend[-10:] if len(accuracy_trend) > 10 else accuracy_trend,
            "speed_trend": speed_trend[-10:] if len(speed_trend) > 10 else speed_trend,
            "topic_mastery": topic_averages,
            "strong_topics": [t for t, s in topic_averages.items() if s >= 8],
            "weak_topics": [t for t, s in topic_averages.items() if s < 6],
            "most_common_errors": [{"error": e, "count": c} for e, c in most_common_errors],
            "learning_rate": round(learning_rate * 100, 1),
            "plateau_detected": plateau_detected,
            "consistency_score": self._calculate_consistency(accuracy_trend)
        }
    
    def _calculate_consistency(self, scores: List[float]) -> float:
        """Calculate performance consistency"""
        if len(scores) < 3:
            return 0.5
        
        # Lower standard deviation means more consistent
        std_dev = statistics.pstdev(scores) if len(scores) > 1 else 0
        max_std = 3.0  # Assuming scores 0-10
        
        consistency = max(0, 1 - (std_dev / max_std))
        return round(consistency * 100, 1)
    
    def _calculate_metrics(self, session_history: List[Dict]) -> Dict[str, Any]:
        """Calculate key performance metrics"""
        
        eval_sessions = [
            s for s in session_history 
            if s.get("agent") == "evaluator" and s.get("result", {}).get("scores")
        ]
        
        if not eval_sessions:
            return {
                "total_sessions": len(session_history),
                "avg_score": 0,
                "total_practice_hours": 0
            }
        
        # Calculate metrics
        total_sessions = len(eval_sessions)
        avg_score = sum(s["result"]["scores"]["overall"] for s in eval_sessions) / total_sessions
        
        # Practice time (assuming each session ~30 mins)
        total_practice_hours = (total_sessions * 30) / 60
        
        # Improvement rate
        if total_sessions >= 2:
            first_score = eval_sessions[0]["result"]["scores"]["overall"]
            last_score = eval_sessions[-1]["result"]["scores"]["overall"]
            improvement = last_score - first_score
            improvement_rate = (improvement / first_score * 100) if first_score > 0 else 0
        else:
            improvement = 0
            improvement_rate = 0
        
        # Session frequency
        if len(eval_sessions) >= 2:
            first_date = datetime.fromisoformat(eval_sessions[0]["timestamp"])
            last_date = datetime.fromisoformat(eval_sessions[-1]["timestamp"])
            days_diff = (last_date - first_date).days
            if days_diff > 0:
                frequency = total_sessions / days_diff
            else:
                frequency = total_sessions
        else:
            frequency = 1
        
        return {
            "total_sessions": total_sessions,
            "total_practice_hours": round(total_practice_hours, 1),
            "avg_score": round(avg_score, 1),
            "highest_score": max(s["result"]["scores"]["overall"] for s in eval_sessions),
            "lowest_score": min(s["result"]["scores"]["overall"] for s in eval_sessions),
            "improvement": round(improvement, 1),
            "improvement_rate": round(improvement_rate, 1),
            "session_frequency": round(frequency, 1),
            "consistency": self._calculate_consistency([s["result"]["scores"]["overall"] for s in eval_sessions])
        }
    
    def _generate_adaptations(self, patterns: Dict, metrics: Dict, 
                             current_profile: Any) -> Dict[str, Any]:
        """Generate system adaptations based on performance"""
        
        adaptations = {
            "roadmap_adjustments": [],
            "difficulty_adjustments": [],
            "focus_shifts": [],
            "schedule_adjustments": []
        }
        
        # Adapt based on weak topics
        weak_topics = patterns.get("weak_topics", [])
        if weak_topics:
            for topic in weak_topics[:3]:
                adaptations["focus_shifts"].append({
                    "action": "add_more_practice",
                    "topic": topic,
                    "reason": f"Performance below target (score < 6)",
                    "additional_hours": 3,
                    "resources": ["video_tutorials", "practice_problems"]
                })
        
        # Adapt based on plateau
        if patterns.get("plateau_detected"):
            adaptations["roadmap_adjustments"].append({
                "action": "introduce_variety",
                "reason": "Performance plateau detected",
                "suggestion": "Try different learning methods or harder problems"
            })
        
        # Adapt based on learning rate
        learning_rate = patterns.get("learning_rate", 0)
        if learning_rate > 20:
            adaptations["difficulty_adjustments"].append({
                "action": "increase_difficulty",
                "reason": f"Learning rapidly ({learning_rate}% improvement)",
                "new_difficulty": "advanced"
            })
        elif learning_rate < 5 and metrics.get("total_sessions", 0) > 5:
            adaptations["difficulty_adjustments"].append({
                "action": "decrease_difficulty",
                "reason": "Slow progress detected",
                "new_difficulty": "intermediate",
                "additional_support": "more_foundational_content"
            })
        
        # Adapt based on error patterns
        common_errors = patterns.get("most_common_errors", [])
        if common_errors:
            top_error = common_errors[0]
            adaptations["focus_shifts"].append({
                "action": "target_error_pattern",
                "error_type": top_error["error"],
                "occurrence_count": top_error["count"],
                "suggested_intervention": f"Focused practice on avoiding {top_error['error']}"
            })
        
        # Adapt based on consistency
        consistency = metrics.get("consistency", 100)
        if consistency < 50:
            adaptations["schedule_adjustments"].append({
                "action": "improve_consistency",
                "reason": "Inconsistent performance",
                "suggestion": "Establish regular practice routine",
                "recommended_sessions_per_week": 5
            })
        
        return adaptations
    
    def _generate_predictions(self, metrics: Dict, patterns: Dict) -> Dict[str, Any]:
        """Generate performance predictions"""
        
        # Predict readiness score
        current_avg = metrics.get("avg_score", 0)
        improvement_rate = metrics.get("improvement_rate", 0)
        sessions_per_week = metrics.get("session_frequency", 3)
        
        # Project forward 4 weeks
        projected_sessions = sessions_per_week * 4
        projected_improvement = (improvement_rate / 100) * projected_sessions * 0.5  # Diminishing returns
        projected_score = min(10, current_avg + projected_improvement)
        
        # Predict weak areas that will persist
        weak_topics = patterns.get("weak_topics", [])
        persistent_weak = weak_topics[:2] if weak_topics else []
        
        # Predict burnout risk
        total_hours = metrics.get("total_practice_hours", 0)
        sessions = metrics.get("total_sessions", 0)
        avg_session_length = (total_hours * 60) / sessions if sessions > 0 else 30
        
        if avg_session_length > 90 and sessions_per_week > 5:
            burnout_risk = "high"
        elif avg_session_length > 60 and sessions_per_week > 4:
            burnout_risk = "medium"
        else:
            burnout_risk = "low"
        
        # Predict interview readiness
        readiness = min(100, (projected_score / 10) * 100)
        
        return {
            "projected_readiness_4weeks": round(readiness, 1),
            "projected_score_4weeks": round(projected_score, 1),
            "persistent_weak_areas": persistent_weak,
            "burnout_risk": burnout_risk,
            "estimated_sessions_to_target": self._estimate_sessions_to_target(current_avg, 8.5),
            "confidence_interval": {
                "lower": max(0, projected_score - 1.5),
                "upper": min(10, projected_score + 1.5)
            }
        }
    
    def _estimate_sessions_to_target(self, current: float, target: float) -> int:
        """Estimate sessions needed to reach target"""
        if current >= target:
            return 0
        
        # Assume 0.2 point improvement per session on average
        improvement_needed = target - current
        sessions_needed = int(improvement_needed / 0.2)
        
        return sessions_needed
    
    def _get_recommended_focus(self, patterns: Dict, metrics: Dict) -> List[Dict]:
        """Get recommended focus areas"""
        
        recommendations = []
        
        # Focus on weak topics
        for topic in patterns.get("weak_topics", [])[:3]:
            recommendations.append({
                "area": topic,
                "type": "weak_topic",
                "priority": "high",
                "suggested_action": f"Dedicate 3 sessions to {topic} this week"
            })
        
        # Focus on error patterns
        for error in patterns.get("most_common_errors", [])[:2]:
            recommendations.append({
                "area": f"Avoiding {error['error']}",
                "type": "error_pattern",
                "priority": "medium",
                "suggested_action": f"Practice problems that target {error['error']} issues"
            })
        
        # Focus on consistency if needed
        if metrics.get("consistency", 100) < 60:
            recommendations.append({
                "area": "Consistency",
                "type": "behavioral",
                "priority": "medium",
                "suggested_action": "Set fixed practice times and stick to schedule"
            })
        
        return recommendations
    
    def _generate_report(self, metrics: Dict, patterns: Dict, 
                        predictions: Dict) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        # Format report for different audiences
        return {
            "executive_summary": self._generate_executive_summary(metrics, patterns, predictions),
            "detailed_analysis": {
                "metrics": metrics,
                "patterns": {k: v for k, v in patterns.items() if k not in ["accuracy_trend", "speed_trend"]},
                "predictions": predictions
            },
            "visualization_data": {
                "accuracy_trend": patterns.get("accuracy_trend", []),
                "topic_heatmap": self._create_topic_heatmap(patterns.get("topic_mastery", {})),
                "error_distribution": patterns.get("most_common_errors", [])
            },
            "achievements": self._identify_achievements(metrics, patterns),
            "next_milestones": self._get_next_milestones(metrics)
        }
    
    def _generate_executive_summary(self, metrics: Dict, patterns: Dict, 
                                   predictions: Dict) -> str:
        """Generate executive summary in natural language"""
        
        summary_parts = []
        
        # Overall status
        if metrics.get("avg_score", 0) >= 8:
            summary_parts.append("Excellent progress! You're performing at a high level.")
        elif metrics.get("avg_score", 0) >= 6:
            summary_parts.append("Good progress! You're on the right track.")
        else:
            summary_parts.append("You're making progress, but there's room for improvement.")
        
        # Improvement
        if metrics.get("improvement_rate", 0) > 15:
            summary_parts.append(f"Your improvement rate of {metrics['improvement_rate']}% is impressive.")
        
        # Weak areas
        weak = patterns.get("weak_topics", [])
        if weak:
            summary_parts.append(f"Focus areas: {', '.join(weak[:3])}.")
        
        # Predictions
        if predictions.get("projected_readiness_4weeks", 0) > 80:
            summary_parts.append("You're on track to be interview-ready in 4 weeks.")
        
        return " ".join(summary_parts)
    
    def _create_topic_heatmap(self, topic_mastery: Dict) -> List[Dict]:
        """Create heatmap data for topic mastery visualization"""
        
        heatmap = []
        for topic, score in topic_mastery.items():
            heatmap.append({
                "topic": topic,
                "score": round(score, 1),
                "intensity": self._score_to_intensity(score)
            })
        
        # Sort by score
        heatmap.sort(key=lambda x: x["score"], reverse=True)
        
        return heatmap
    
    def _score_to_intensity(self, score: float) -> str:
        """Convert score to intensity for visualization"""
        if score >= 8:
            return "high"
        elif score >= 6:
            return "medium"
        elif score >= 4:
            return "low"
        else:
            return "critical"
    
    def _identify_achievements(self, metrics: Dict, patterns: Dict) -> List[Dict]:
        """Identify achievements and milestones reached"""
        
        achievements = []
        
        # Session count achievement
        if metrics.get("total_sessions", 0) >= 50:
            achievements.append({
                "title": "Practice Warrior",
                "description": "Completed 50+ practice sessions",
                "icon": "🏆"
            })
        elif metrics.get("total_sessions", 0) >= 25:
            achievements.append({
                "title": "Dedicated Learner",
                "description": "Completed 25+ practice sessions",
                "icon": "⭐"
            })
        
        # Score achievement
        if metrics.get("highest_score", 0) >= 9:
            achievements.append({
                "title": "Excellence Achieved",
                "description": "Scored 9+ on an evaluation",
                "icon": "🎯"
            })
        
        # Improvement achievement
        if metrics.get("improvement_rate", 0) > 30:
            achievements.append({
                "title": "Fast Learner",
                "description": f"Improved by {metrics['improvement_rate']}%",
                "icon": "🚀"
            })
        
        # Topic mastery achievements
        strong_topics = patterns.get("strong_topics", [])
        if len(strong_topics) >= 3:
            achievements.append({
                "title": "Topic Master",
                "description": f"Mastered {len(strong_topics)} topics",
                "icon": "📚"
            })
        
        return achievements
    
    def _get_next_milestones(self, metrics: Dict) -> List[Dict]:
        """Get next milestones to aim for"""
        
        milestones = []
        
        # Next session milestone
        current_sessions = metrics.get("total_sessions", 0)
        next_session_milestone = ((current_sessions // 10) + 1) * 10
        milestones.append({
            "milestone": f"Complete {next_session_milestone} sessions",
            "current": current_sessions,
            "target": next_session_milestone,
            "progress": round((current_sessions / next_session_milestone) * 100, 1)
        })
        
        # Next score milestone
        current_avg = metrics.get("avg_score", 0)
        if current_avg < 7:
            target = 7
        elif current_avg < 8:
            target = 8
        elif current_avg < 9:
            target = 9
        else:
            target = 9.5
        
        milestones.append({
            "milestone": f"Achieve {target} average score",
            "current": current_avg,
            "target": target,
            "progress": round((current_avg / target) * 100, 1) if target > 0 else 0
        })
        
        return milestones
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "status": "error",
            "error": error_message,
            "timestamp": self._get_timestamp()
        }