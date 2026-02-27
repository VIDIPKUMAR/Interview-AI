from typing import Dict, Any, List, Optional, Tuple
import json
from datetime import datetime
from .base_agent import BaseAgent
from utils.llm_client import LLMClient
import statistics

class EvaluatorAgent(BaseAgent):
    """Evaluates user performance and provides detailed feedback"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            agent_id="evaluator_001",
            name="Performance Evaluator",
            description="Evaluates interview responses and provides feedback",
            config=config
        )
        self.llm_client = LLMClient(**config.get("llm_config", {}))
        self.evaluation_rubrics = self._load_evaluation_rubrics()
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate user response"""
        self.log(f"Evaluating response for session: {input_data.get('session_id')}")
        
        required_fields = ["user_response", "question", "question_type", "expected_areas"]
        for field in required_fields:
            if field not in input_data:
                return self._create_error_response(f"Missing required field: {field}")
        
        try:
            # Perform multi-dimensional evaluation
            evaluation = self._evaluate_response(
                question=input_data["question"],
                user_response=input_data["user_response"],
                question_type=input_data["question_type"],
                expected_areas=input_data["expected_areas"],
                context=input_data.get("context", {})
            )
            
            # Generate detailed feedback with summary
            feedback = self._generate_feedback(evaluation, input_data["question"])
            
            # Calculate scores
            scores = self._calculate_scores(evaluation)
            
            # Identify improvement areas
            improvement_areas = self._identify_improvement_areas(evaluation)
            
            response = {
                "status": "success",
                "evaluation_id": f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "scores": scores,
                "evaluation_details": evaluation,
                "feedback": feedback,
                "improvement_areas": improvement_areas,
                "recommended_actions": self._generate_recommendations(evaluation),
                "confidence_metrics": self._calculate_confidence_metrics(evaluation)
            }
            
            self.update_memory({
                "action": "evaluated_response",
                "session_id": input_data.get("session_id"),
                "question_type": input_data["question_type"],
                "overall_score": scores["overall"]
            })
            
            return response
            
        except Exception as e:
            self.log(f"Error in evaluation: {str(e)}", "ERROR")
            return self._create_error_response(str(e))
    
    def _evaluate_response(self, question: str, user_response: str, 
                          question_type: str, expected_areas: List[str],
                          context: Dict) -> Dict[str, Any]:
        """Perform comprehensive evaluation"""
        
        rubric = self.evaluation_rubrics.get(question_type, self.evaluation_rubrics["default"])
        
        system_prompt = f"""You are an expert interview evaluator. Evaluate the response based on the following rubric:
        
        Evaluation Rubric for {question_type} questions:
        {json.dumps(rubric, indent=2)}
        
        Provide detailed evaluation for each criterion."""
        
        user_prompt = f"""
        Question: {question}
        
        Expected Key Areas to Cover:
        {', '.join(expected_areas)}
        
        User's Response:
        {user_response}
        
        Context:
        - User Experience: {context.get('experience_years', 'Not specified')} years
        - Target Role: {context.get('target_role', 'Not specified')}
        - Difficulty Level: {context.get('difficulty', 'intermediate')}
        
        Please evaluate the response thoroughly."""
        
        evaluation_schema = {
            "type": "object",
            "properties": {
                "technical_accuracy": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number", "minimum": 0, "maximum": 10},
                        "feedback": {"type": "string"},
                        "strengths": {"type": "array", "items": {"type": "string"}},
                        "weaknesses": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "communication_effectiveness": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number", "minimum": 0, "maximum": 10},
                        "feedback": {"type": "string"},
                        "clarity": {"type": "string"},
                        "structure": {"type": "string"},
                        "conciseness": {"type": "string"}
                    }
                },
                "problem_solving_approach": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number", "minimum": 0, "maximum": 10},
                        "feedback": {"type": "string"},
                        "methodology": {"type": "string"},
                        "efficiency": {"type": "string"},
                        "alternatives_considered": {"type": "string"}
                    }
                },
                "completeness": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number", "minimum": 0, "maximum": 10},
                        "feedback": {"type": "string"},
                        "covered_areas": {"type": "array", "items": {"type": "string"}},
                        "missing_areas": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "innovation_creativity": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number", "minimum": 0, "maximum": 10},
                        "feedback": {"type": "string"},
                        "unique_insights": {"type": "string"},
                        "originality": {"type": "string"}
                    }
                }
            },
            "required": ["technical_accuracy", "communication_effectiveness", "problem_solving_approach", "completeness"]
        }
        
        return self.llm_client.generate_structured_output(
            prompt=user_prompt,
            output_schema=evaluation_schema,
            system_message=system_prompt
        )
    
    def _generate_feedback(self, evaluation: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Generate actionable feedback with summary"""
        
        feedback_prompt = f"""
        Based on this evaluation of the question "{question}":
        {json.dumps(evaluation, indent=2)}
        
        Generate actionable feedback that:
        1. Starts with a brief summary (1-2 sentences)
        2. Acknowledges what was done well
        3. Identifies specific areas for improvement
        4. Provides concrete examples of how to improve
        5. Suggests practice exercises
        6. Gives encouragement and next steps
        
        Structure the feedback for maximum impact and learning."""
        
        feedback_schema = {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "strengths_highlighted": {"type": "array", "items": {"type": "string"}},
                "improvement_areas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "area": {"type": "string"},
                            "issue": {"type": "string"},
                            "suggestion": {"type": "string"},
                            "practice_exercise": {"type": "string"}
                        }
                    }
                },
                "immediate_actions": {"type": "array", "items": {"type": "string"}},
                "long_term_recommendations": {"type": "array", "items": {"type": "string"}},
                "encouragement_message": {"type": "string"}
            },
            "required": ["summary", "strengths_highlighted", "improvement_areas"]
        }
        
        return self.llm_client.generate_structured_output(
            prompt=feedback_prompt,
            output_schema=feedback_schema,
            system_message="You are a supportive and constructive interview coach."
        )
    
    def _calculate_scores(self, evaluation: Dict[str, Any]) -> Dict[str, float]:
        """Calculate various scores from evaluation"""
        
        category_weights = {
            "technical_accuracy": 0.35,
            "communication_effectiveness": 0.25,
            "problem_solving_approach": 0.20,
            "completeness": 0.15,
            "innovation_creativity": 0.05
        }
        
        scores = {}
        weighted_sum = 0
        total_weight = 0
        
        for category, weight in category_weights.items():
            if category in evaluation and isinstance(evaluation[category], dict):
                category_score = evaluation[category].get("score", 0)
                scores[category] = category_score
                weighted_sum += category_score * weight
                total_weight += weight
        
        # Handle case where some categories might be missing
        if total_weight > 0:
            scores["overall"] = round(weighted_sum / total_weight, 2)
        else:
            scores["overall"] = 0.0
        
        scores["normalized_overall"] = round((scores["overall"] / 10) * 100, 1)  # Percentage
        
        return scores
    
    def _identify_improvement_areas(self, evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify key areas for improvement"""
        
        improvement_areas = []
        threshold = 7.0  # Scores below this need improvement
        
        for category, data in evaluation.items():
            if isinstance(data, dict) and "score" in data:
                score = data.get("score", 0)
                if score < threshold:
                    improvement_areas.append({
                        "category": category.replace("_", " ").title(),
                        "current_score": score,
                        "target_score": threshold,
                        "gap": threshold - score,
                        "priority": "high" if score < 5 else "medium"
                    })
        
        # Sort by priority and gap
        improvement_areas.sort(key=lambda x: (x["priority"] == "high", x["gap"]), reverse=True)
        
        return improvement_areas
    
    def _generate_recommendations(self, evaluation: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations based on evaluation"""
        
        recommendations = []
        
        # Technical accuracy recommendations
        if evaluation.get("technical_accuracy", {}).get("score", 0) < 7:
            recommendations.append("Review fundamental concepts and practice with coding challenges")
        
        # Communication recommendations
        if evaluation.get("communication_effectiveness", {}).get("score", 0) < 7:
            recommendations.append("Practice explaining technical concepts to non-technical friends")
        
        # Problem solving recommendations
        if evaluation.get("problem_solving_approach", {}).get("score", 0) < 7:
            recommendations.append("Study different problem-solving frameworks and patterns")
        
        return recommendations
    
    def _calculate_confidence_metrics(self, evaluation: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence metrics for the evaluation"""
        
        # This is a simplified version - in reality, you'd use more sophisticated metrics
        scores = []
        for data in evaluation.values():
            if isinstance(data, dict) and "score" in data:
                scores.append(data.get("score", 0))
        
        if not scores:
            return {"confidence": 0.0, "consistency": 0.0}
        
        mean_score = statistics.mean(scores)
        std_dev = statistics.pstdev(scores)
        
        # Confidence based on score consistency
        consistency = max(0, 1 - (std_dev / 5))  # Normalize
        
        # Overall confidence metric
        confidence = (mean_score / 10) * 0.7 + consistency * 0.3
        
        return {
            "confidence": round(confidence, 3),
            "consistency": round(consistency, 3),
            "score_variability": round(std_dev, 3)
        }
    
    def _load_evaluation_rubrics(self) -> Dict[str, Any]:
        """Load evaluation rubrics for different question types"""
        
        return {
            "technical": {
                "technical_accuracy": {
                    "weight": 0.4,
                    "criteria": ["Correctness", "Depth of knowledge", "Technical terminology"]
                },
                "problem_solving": {
                    "weight": 0.3,
                    "criteria": ["Approach", "Efficiency", "Edge cases"]
                },
                "communication": {
                    "weight": 0.2,
                    "criteria": ["Clarity", "Structure", "Explanation quality"]
                },
                "completeness": {
                    "weight": 0.1,
                    "criteria": ["Coverage", "Depth", "Examples"]
                }
            },
            "behavioral": {
                "structure": {
                    "weight": 0.3,
                    "criteria": ["STAR method usage", "Organization", "Flow"]
                },
                "content": {
                    "weight": 0.4,
                    "criteria": ["Relevance", "Specificity", "Impact demonstration"]
                },
                "delivery": {
                    "weight": 0.2,
                    "criteria": ["Confidence", "Authenticity", "Engagement"]
                },
                "learning": {
                    "weight": 0.1,
                    "criteria": ["Self-awareness", "Growth mindset", "Lessons learned"]
                }
            },
            "default": {
                "quality": {
                    "weight": 0.5,
                    "criteria": ["Accuracy", "Completeness", "Relevance"]
                },
                "communication": {
                    "weight": 0.3,
                    "criteria": ["Clarity", "Organization", "Conciseness"]
                },
                "critical_thinking": {
                    "weight": 0.2,
                    "criteria": ["Analysis", "Synthesis", "Evaluation"]
                }
            }
        }
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "status": "error",
            "error": error_message,
            "timestamp": self._get_timestamp()
        }
