"""
Mock LLM client for testing when API limits are reached
"""

import json
import random
from typing import Dict, Any, List, Optional
import time

class MockGeminiClient:
    """Mock Gemini client that returns predefined responses"""
    
    def __init__(self, model: str = "models/gemini-2.0-flash-lite", **kwargs):
        self.model_name = model
        self.config = kwargs
        
    def generate_completion(self, 
                           prompt: str, 
                           system_message: Optional[str] = None,
                           temperature: float = 0.7,
                           max_tokens: int = 2000,
                           **kwargs) -> str:
        """Generate mock completion"""
        
        # Simulate API delay
        time.sleep(0.1)
        
        # Return different responses based on prompt content
        if "learning plan" in prompt.lower() or "plan" in prompt.lower():
            return json.dumps({
                "phases": [
                    {
                        "phase_name": "Foundation Phase",
                        "duration_weeks": 2,
                        "focus_areas": ["Data Structures", "Algorithms", "Programming Fundamentals"],
                        "learning_objectives": ["Master basic data structures", "Understand algorithm complexity"],
                        "resources": ["LeetCode", "Cracking the Coding Interview"],
                        "practice_exercises": ["Array problems", "String manipulation"],
                        "success_metrics": ["Complete 50 practice problems", "Score >80% on assessments"]
                    },
                    {
                        "phase_name": "Core Competency Phase",
                        "duration_weeks": 3,
                        "focus_areas": ["System Design", "Advanced Algorithms", "Database Design"],
                        "learning_objectives": ["Design scalable systems", "Solve complex algorithm problems"],
                        "resources": ["System Design Primer", "Designing Data-Intensive Applications"],
                        "practice_exercises": ["Design Twitter", "Design URL shortener"],
                        "success_metrics": ["Complete system design mock interviews", "Solve 100+ medium problems"]
                    }
                ],
                "total_duration_weeks": 8,
                "key_milestones": ["Complete foundation phase", "First mock interview", "Final review"]
            }, indent=2)
        
        elif "evaluate" in prompt.lower() or "score" in prompt.lower():
            return json.dumps({
                "technical_accuracy": {
                    "score": 8.5,
                    "feedback": "Good understanding of concepts",
                    "strengths": ["Correct hashmap explanation", "Accurate time complexity"],
                    "weaknesses": ["Could provide more details on collision resolution"]
                },
                "communication_effectiveness": {
                    "score": 7.0,
                    "feedback": "Clear but could be more structured",
                    "clarity": "Good",
                    "structure": "Average",
                    "conciseness": "Good"
                },
                "problem_solving_approach": {
                    "score": 9.0,
                    "feedback": "Excellent problem-solving methodology",
                    "methodology": "Systematic",
                    "efficiency": "Optimal",
                    "alternatives_considered": "Yes"
                },
                "completeness": {
                    "score": 8.0,
                    "feedback": "Covered most key areas",
                    "covered_areas": ["hashing mechanism", "time complexity", "internal structure"],
                    "missing_areas": ["concrete code examples"]
                },
                "innovation_creativity": {
                    "score": 6.5,
                    "feedback": "Standard explanation, could use more unique insights",
                    "unique_insights": "Limited",
                    "originality": "Average"
                }
            }, indent=2)
        
        elif "tutor" in prompt.lower() or "lesson" in prompt.lower():
            return json.dumps({
                "learning_objectives": [
                    "Understand dynamic programming concepts",
                    "Learn memoization vs tabulation",
                    "Solve common DP problems"
                ],
                "key_concepts": [
                    {
                        "concept": "Memoization",
                        "explanation": "Top-down approach storing computed results",
                        "importance": "Reduces time complexity from exponential to polynomial",
                        "example": "Fibonacci sequence with memoization"
                    },
                    {
                        "concept": "Tabulation",
                        "explanation": "Bottom-up approach building solution iteratively",
                        "importance": "Often more memory efficient than memoization",
                        "example": "Fibonacci with tabulation uses O(n) space"
                    }
                ],
                "content_delivery": {
                    "method": "interactive_exercises",
                    "format": "step_by_step_walkthrough",
                    "estimated_time_minutes": 45
                },
                "real_world_applications": [
                    {
                        "scenario": "Stock trading",
                        "application": "Maximum profit with at most k transactions",
                        "relevance": "High for financial software roles"
                    }
                ],
                "common_interview_questions": [
                    {
                        "question": "Given a set of coin denominations and a target amount, find the minimum number of coins needed.",
                        "difficulty": "medium",
                        "expected_answer_elements": ["DP state definition", "recurrence relation", "base cases"]
                    }
                ],
                "best_practices": [
                    "Identify optimal substructure",
                    "Define clear state transitions",
                    "Start with brute force then optimize"
                ],
                "common_pitfalls": [
                    {
                        "pitfall": "Forgetting base cases",
                        "why_it_happens": "Rushing to implement recurrence",
                        "how_to_avoid": "Always define base cases first"
                    }
                ],
                "summary": "Dynamic programming breaks problems into overlapping subproblems",
                "key_takeaways": ["DP has optimal substructure", "Use memoization or tabulation", "Practice pattern recognition"]
            }, indent=2)
        
        elif "schedule" in prompt.lower():
            return json.dumps({
                "period": {
                    "start_date": "2024-02-10",
                    "end_date": "2024-04-06",
                    "total_weeks": 8
                },
                "daily_schedule": [
                    {
                        "day_of_week": "Monday",
                        "date": "2024-02-12",
                        "sessions": [
                            {
                                "session_id": "session_001",
                                "time_slot": "08:00-09:30",
                                "duration_minutes": 90,
                                "activity_type": "theory_study",
                                "topic": "Data Structures",
                                "focus_area": "Arrays & Strings",
                                "difficulty": "beginner",
                                "learning_objective": "Understand array operations and string manipulation",
                                "resources_needed": ["textbook", "coding_platform"]
                            }
                        ],
                        "total_learning_time": 90,
                        "breakdown": {
                            "theory_study": 90,
                            "practice_problems": 0,
                            "review": 0,
                            "mock_interview": 0
                        }
                    }
                ],
                "weekly_overview": {
                    "total_hours": 15,
                    "sessions_per_week": 10,
                    "mock_interviews_per_week": 1,
                    "review_sessions_per_week": 2
                }
            }, indent=2)
        
        elif "exercise" in prompt.lower() or "practice" in prompt.lower():
            return json.dumps([
                {
                    "exercise_id": "ex_001",
                    "problem_statement": "Implement the Fibonacci sequence using dynamic programming.",
                    "difficulty": "easy",
                    "estimated_time_minutes": 15,
                    "concepts_tested": ["memoization", "tabulation"],
                    "hints": ["Start with the base cases", "Use a dictionary to cache results"],
                    "solution_approach": "Use memoization to cache computed Fibonacci numbers",
                    "detailed_solution": "def fib(n, memo={}): if n in memo: return memo[n]; if n <= 1: return n; memo[n] = fib(n-1) + fib(n-2); return memo[n]",
                    "alternative_solutions": ["Iterative tabulation approach"],
                    "common_mistakes": ["Forgetting base cases", "Not initializing memo dict"],
                    "follow_up_questions": ["What is the time complexity?", "Can you do it in O(1) space?"]
                },
                {
                    "exercise_id": "ex_002",
                    "problem_statement": "Find the longest common subsequence of two strings.",
                    "difficulty": "medium",
                    "estimated_time_minutes": 25,
                    "concepts_tested": ["2D DP", "state transitions"],
                    "hints": ["Build a 2D table", "Compare characters at each position"],
                    "solution_approach": "Build a 2D DP table where dp[i][j] = LCS length of first i and j chars",
                    "detailed_solution": "Standard LCS DP solution with O(mn) time and space",
                    "alternative_solutions": ["Space-optimized O(min(m,n)) solution"],
                    "common_mistakes": ["Off-by-one errors in indexing"],
                    "follow_up_questions": ["How to reconstruct the actual subsequence?"]
                }
            ], indent=2)
        
        elif "assessment" in prompt.lower():
            return json.dumps({
                "assessment_id": "assess_001",
                "total_questions": 3,
                "estimated_time_minutes": 15,
                "questions": [
                    {
                        "question_id": "q1",
                        "question_type": "multiple_choice",
                        "question_text": "What is the time complexity of memoized Fibonacci?",
                        "options": ["O(n)", "O(n^2)", "O(2^n)", "O(log n)"],
                        "correct_answer": "O(n)",
                        "explanation": "Each subproblem is solved only once and cached",
                        "points": 1
                    }
                ],
                "passing_score": 70,
                "scoring_rubric": "Each correct answer is worth 1 point"
            }, indent=2)
        
        elif "feedback" in prompt.lower() or "actionable" in prompt.lower():
            return json.dumps({
                "summary": "Good overall response with strong technical accuracy and problem-solving approach.",
                "strengths_highlighted": [
                    "Correct explanation of HashMap internals",
                    "Accurate time complexity analysis",
                    "Mentioned Java 8 tree optimization"
                ],
                "improvement_areas": [
                    {
                        "area": "Collision Resolution",
                        "issue": "Could provide more detail on chaining vs open addressing",
                        "suggestion": "Explain both approaches and their trade-offs",
                        "practice_exercise": "Implement a simple HashMap from scratch"
                    }
                ],
                "immediate_actions": ["Review collision resolution strategies", "Practice implementing data structures"],
                "long_term_recommendations": ["Study Java Collections framework internals"],
                "encouragement_message": "Great job! You have a solid understanding of HashMap internals."
            }, indent=2)
        
        else:
            # Generic response
            return json.dumps({
                "message": "Mock response for testing",
                "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                "status": "success",
                "model": self.model_name
            }, indent=2)
    
    def generate_structured_output(self, prompt, output_schema, system_message=None, **kwargs):
        """Generate structured mock output"""
        response = self.generate_completion(prompt, system_message, **kwargs)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Create a mock response based on schema
            mock_data = {}
            if "properties" in output_schema:
                for prop, prop_schema in output_schema["properties"].items():
                    if prop_schema.get("type") == "string":
                        mock_data[prop] = f"Mock {prop}"
                    elif prop_schema.get("type") == "number":
                        mock_data[prop] = 7.5
                    elif prop_schema.get("type") == "integer":
                        mock_data[prop] = 10
                    elif prop_schema.get("type") == "array":
                        mock_data[prop] = ["item1", "item2", "item3"]
                    elif prop_schema.get("type") == "object":
                        mock_data[prop] = {"key": "value"}
                    elif prop_schema.get("type") == "boolean":
                        mock_data[prop] = True
            return mock_data
    
    def stream_completion(self, prompt, **kwargs):
        """Mock streaming"""
        response = self.generate_completion(prompt, **kwargs)
        for char in response:
            yield char
            time.sleep(0.01)
    
    def count_tokens(self, text):
        """Mock token counting"""
        return len(text.split())

class MockLLMClient:
    """Mock LLM client wrapper"""
    
    def __init__(self, provider="mock", model="mock-model", **kwargs):
        self.provider = provider
        self.client = MockGeminiClient(model=model, **kwargs)
    
    def generate_completion(self, *args, **kwargs):
        return self.client.generate_completion(*args, **kwargs)
    
    def generate_structured_output(self, *args, **kwargs):
        return self.client.generate_structured_output(*args, **kwargs)
    
    def stream_completion(self, *args, **kwargs):
        return self.client.stream_completion(*args, **kwargs)
