from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from .base_agent import BaseAgent
from utils.llm_client import LLMClient
from models.user_profile import UserProfile, LearningStyle

class TutorAgent(BaseAgent):
    """Provides personalized tutoring and adaptive learning content"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            agent_id="tutor_001",
            name="Personalized Tutor",
            description="Adaptive teaching and content delivery based on learning style",
            config=config
        )
        self.llm_client = LLMClient(**config.get("llm_config", {}))
        self.teaching_methods = self._load_teaching_methods()
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide tutoring based on user needs"""
        self.log(f"Providing tutoring for topic: {input_data.get('topic')}")
        
        required_fields = ["topic", "difficulty", "user_profile"]
        for field in required_fields:
            if field not in input_data:
                return self._create_error_response(f"Missing required field: {field}")
        
        try:
            # Select teaching method based on learning style
            teaching_method = self._select_teaching_method(
                input_data["user_profile"].preferences.preferred_learning_style
            )
            
            # Generate lesson content
            lesson = self._generate_lesson(
                topic=input_data["topic"],
                difficulty=input_data["difficulty"],
                user_profile=input_data["user_profile"],
                teaching_method=teaching_method,
                context=input_data.get("context", {})
            )
            
            # Generate practice exercises
            raw_concepts = lesson.get("key_concepts", [])
            # Defensive: handle if LLM returns a dict instead of a list
            if isinstance(raw_concepts, dict):
                raw_concepts = list(raw_concepts.values())
            elif not isinstance(raw_concepts, list):
                raw_concepts = []
            exercises = self._generate_practice_exercises(
                topic=input_data["topic"],
                difficulty=input_data["difficulty"],
                lesson_concepts=raw_concepts,
                user_profile=input_data["user_profile"]
            )
            
            # Create learning assessment
            assessment = self._create_assessment(
                topic=input_data["topic"],
                lesson_concepts=raw_concepts,
                difficulty=input_data["difficulty"]
            )
            
            response = {
                "status": "success",
                "session_id": f"tutor_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "topic": input_data["topic"],
                "teaching_method": teaching_method,
                "lesson": lesson,
                "practice_exercises": exercises,
                "assessment": assessment,
                "estimated_completion_time": self._estimate_completion_time(lesson, exercises),
                "next_steps": self._suggest_next_steps(input_data["topic"], input_data["user_profile"])
            }
            
            self.update_memory({
                "action": "delivered_tutoring",
                "topic": input_data["topic"],
                "difficulty": input_data["difficulty"],
                "teaching_method": teaching_method
            })
            
            return response
            
        except Exception as e:
            self.log(f"Error in tutoring: {str(e)}", "ERROR")
            return self._create_error_response(str(e))
    
    def _select_teaching_method(self, learning_style: LearningStyle) -> str:
        """Select teaching method based on learning style"""
        
        methods = {
            "visual": [
                "diagram_based",
                "video_explanation", 
                "infographic_summary",
                "mind_mapping"
            ],
            "auditory": [
                "lecture_style",
                "discussion_based",
                "podcast_format",
                "verbal_explanation"
            ],
            "kinesthetic": [
                "interactive_exercises",
                "hands_on_examples",
                "simulation_based",
                "step_by_step_walkthrough"
            ],
            "read_write": [
                "textbook_style",
                "note_taking_focused",
                "written_exercises",
                "article_summary"
            ]
        }
        
        # Safely get style name from enum or string
        if hasattr(learning_style, 'value'):
            style_name = learning_style.value
        else:
            style_name = str(learning_style)
        available_methods = methods.get(style_name, methods["visual"])
        
        # For now, return the first method - could be randomized or selected based on context
        return available_methods[0]
    
    def _generate_lesson(self, topic: str, difficulty: str, 
                        user_profile: UserProfile, teaching_method: str,
                        context: Dict) -> Dict[str, Any]:
        """Generate personalized lesson content"""
        
        system_prompt = f"""You are an expert technical tutor specializing in interview preparation.
        Teaching Method: {teaching_method}
        
        Create engaging, personalized lessons that:
        1. Match the user's learning style
        2. Adapt to their experience level
        3. Focus on practical interview applications
        4. Include real-world examples
        5. Build from fundamentals to advanced concepts"""
        
        user_prompt = f"""
        Create a comprehensive lesson on: {topic}
        
        Difficulty Level: {difficulty}
        User Experience: {user_profile.experience_years} years
        Target Role: {user_profile.interview_goal.target_role if user_profile.interview_goal else 'Not specified'}
        
        Teaching Method: {teaching_method}
        
        Context:
        - Previous topics covered: {context.get('previous_topics', ['None'])}
        - Known strengths: {context.get('strengths', ['Not specified'])}
        - Areas needing improvement: {context.get('weaknesses', ['Not specified'])}
        
        Please structure the lesson to include:
        1. Clear learning objectives
        2. Foundational concepts
        3. Advanced applications
        4. Common interview questions on this topic
        5. Best practices and pitfalls to avoid
        6. Real-world examples
        7. Summary and key takeaways
        
        Adapt the content delivery to the teaching method."""
        
        lesson_schema = {
            "type": "object",
            "properties": {
                "learning_objectives": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "key_concepts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "concept": {"type": "string"},
                            "explanation": {"type": "string"},
                            "importance": {"type": "string"},
                            "example": {"type": "string"}
                        }
                    }
                },
                "content_delivery": {
                    "type": "object",
                    "properties": {
                        "method": {"type": "string"},
                        "format": {"type": "string"},
                        "estimated_time_minutes": {"type": "integer"}
                    }
                },
                "real_world_applications": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "scenario": {"type": "string"},
                            "application": {"type": "string"},
                            "relevance": {"type": "string"}
                        }
                    }
                },
                "common_interview_questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "difficulty": {"type": "string"},
                            "expected_answer_elements": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                },
                "best_practices": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "common_pitfalls": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "pitfall": {"type": "string"},
                            "why_it_happens": {"type": "string"},
                            "how_to_avoid": {"type": "string"}
                        }
                    }
                },
                "summary": {"type": "string"},
                "key_takeaways": {"type": "array", "items": {"type": "string"}}
            }
        }
        
        return self.llm_client.generate_structured_output(
            prompt=user_prompt,
            output_schema=lesson_schema,
            system_message=system_prompt,
            temperature=0.8  # More creative for tutoring
        )
    
    def _generate_practice_exercises(self, topic: str, difficulty: str,
                                   lesson_concepts: List[Dict], user_profile: UserProfile) -> List[Dict]:
        """Generate personalized practice exercises"""
        
        system_prompt = """Create practice exercises that:
        1. Gradually increase in difficulty
        2. Apply concepts from the lesson
        3. Mimic real interview questions
        4. Include hints and solution explanations
        5. Adapt to the user's experience level"""
        
        user_prompt = f"""
        Topic: {topic}
        Difficulty Level: {difficulty}
        User Experience: {user_profile.experience_years} years
        
        Key Concepts from Lesson:
        {json.dumps(lesson_concepts[:3], indent=2)}
        
        Create 3-5 practice exercises that cover:
        1. Basic understanding and recall
        2. Application of concepts
        3. Problem-solving and analysis
        4. Advanced scenarios (for higher difficulty)
        
        For each exercise, provide:
        - Clear problem statement
        - Difficulty rating (easy/medium/hard)
        - Estimated time to solve
        - Hints (if needed)
        - Detailed solution explanation
        - Common mistakes to avoid
        
        Make the exercises relevant to {user_profile.interview_goal.target_role if user_profile.interview_goal else 'technical'} interviews."""
        
        exercises_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "exercise_id": {"type": "string"},
                    "problem_statement": {"type": "string"},
                    "difficulty": {"type": "string"},
                    "estimated_time_minutes": {"type": "integer"},
                    "concepts_tested": {"type": "array", "items": {"type": "string"}},
                    "hints": {"type": "array", "items": {"type": "string"}},
                    "solution_approach": {"type": "string"},
                    "detailed_solution": {"type": "string"},
                    "alternative_solutions": {"type": "array", "items": {"type": "string"}},
                    "common_mistakes": {"type": "array", "items": {"type": "string"}},
                    "follow_up_questions": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
        
        return self.llm_client.generate_structured_output(
            prompt=user_prompt,
            output_schema=exercises_schema,
            system_message=system_prompt
        )
    
    def _create_assessment(self, topic: str, lesson_concepts: List[Dict], difficulty: str) -> Dict[str, Any]:
        """Create assessment to check understanding"""
        
        assessment_prompt = f"""
        Create a comprehensive assessment for the topic: {topic}
        
        Difficulty: {difficulty}
        
        Key Concepts Covered:
        {json.dumps([c['concept'] for c in lesson_concepts], indent=2)}
        
        Create an assessment with:
        1. Multiple choice questions testing fundamental understanding
        2. Short answer questions testing application
        3. Problem-solving questions testing analysis
        4. Scenario-based questions testing synthesis
        
        Include answer key with explanations."""
        
        assessment_schema = {
            "type": "object",
            "properties": {
                "assessment_id": {"type": "string"},
                "total_questions": {"type": "integer"},
                "estimated_time_minutes": {"type": "integer"},
                "questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question_id": {"type": "string"},
                            "question_type": {"type": "string"},
                            "question_text": {"type": "string"},
                            "options": {"type": "array", "items": {"type": "string"}},
                            "correct_answer": {"type": "string"},
                            "explanation": {"type": "string"},
                            "points": {"type": "integer"}
                        }
                    }
                },
                "passing_score": {"type": "integer"},
                "scoring_rubric": {"type": "string"}
            }
        }
        
        return self.llm_client.generate_structured_output(
            prompt=assessment_prompt,
            output_schema=assessment_schema,
            system_message="You are an expert assessment creator."
        )
    
    def _estimate_completion_time(self, lesson: Dict, exercises: Any) -> Dict[str, int]:
        """Estimate completion time for the tutoring session"""
        
        lesson_time = lesson.get("content_delivery", {}).get("estimated_time_minutes", 30)
        
        # Defensive: handle if exercises is not a list
        if not isinstance(exercises, list):
            exercises_list = []
        else:
            exercises_list = exercises
        
        exercise_time = sum(
            ex.get("estimated_time_minutes", 10) if isinstance(ex, dict) else 10
            for ex in exercises_list[:3]  # First 3 exercises
        )
        
        assessment_time = 15  # Fixed assessment time
        
        return {
            "lesson_minutes": lesson_time,
            "exercises_minutes": exercise_time,
            "assessment_minutes": assessment_time,
            "total_minutes": lesson_time + exercise_time + assessment_time
        }
    
    def _suggest_next_steps(self, current_topic: str, user_profile: UserProfile) -> List[Dict]:
        """Suggest next learning steps"""
        
        # This would typically come from the planner agent or learning path
        # For now, generate based on common progression
        
        common_progressions = {
            "data_structures": ["algorithms", "system_design", "optimization"],
            "algorithms": ["problem_solving_patterns", "complexity_analysis", "advanced_topics"],
            "system_design": ["distributed_systems", "scalability", "real_world_case_studies"],
            "behavioral": ["leadership_stories", "conflict_resolution", "cultural_fit"]
        }
        
        next_topics = common_progressions.get(current_topic.lower(), ["advanced_" + current_topic])
        
        return [
            {
                "topic": topic,
                "reason": f"Builds upon {current_topic} concepts",
                "estimated_prep_time": "1-2 hours",
                "priority": "high" if i == 0 else "medium"
            }
            for i, topic in enumerate(next_topics[:2])
        ]
    
    def _load_teaching_methods(self) -> Dict[str, List[str]]:
        """Load available teaching methods"""
        
        return {
            "diagram_based": {
                "description": "Uses visual diagrams and flowcharts",
                "best_for": ["visual learners", "complex systems", "process explanations"]
            },
            "lecture_style": {
                "description": "Traditional lecture format with explanations",
                "best_for": ["auditory learners", "theoretical concepts", "foundational knowledge"]
            },
            "interactive_exercises": {
                "description": "Hands-on practice with immediate feedback",
                "best_for": ["kinesthetic learners", "practical skills", "problem-solving"]
            },
            "textbook_style": {
                "description": "Detailed written explanations with examples",
                "best_for": ["read/write learners", "detailed understanding", "reference material"]
            },
            "socratic_method": {
                "description": "Question-based learning to stimulate critical thinking",
                "best_for": ["conceptual understanding", "deep learning", "critical thinking"]
            },
            "case_study": {
                "description": "Real-world examples and scenarios",
                "best_for": ["practical application", "contextual learning", "decision-making"]
            }
        }
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "status": "error",
            "error": error_message,
            "timestamp": self._get_timestamp()
        }