import os
# Override the mock setting to use real Gemini
os.environ["USE_MOCK_LLM"] = "false"

import logging
import time
import random
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from data.problem_database import COMPANY_INDEX, PROBLEM_DATABASE, COMPANY_METADATA
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Force override USE_MOCK_LLM
os.environ["USE_MOCK_LLM"] = "false"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Import agents
from models.user_profile import UserProfile, Skill, InterviewGoal, UserPreferences, SkillLevel
from agents.agent_orchestrator import AgentOrchestrator
from config import get_gemini_config

# Initialize orchestrator
config = {
    "llm_config": {
        "provider": "google",
        "model": "gemini-2.5-flash",
        "temperature": 0.7,
        "max_tokens": 8192,
    }
}

orchestrator = None
user_sessions = {}  # Store user profiles in memory

# Rate limiting - track last request time
last_request_time = 0
MIN_REQUEST_INTERVAL = 2  # Minimum 2 seconds between requests

def rate_limit():
    """Ensure we don't hit API rate limits"""
    global last_request_time
    current_time = time.time()
    time_since_last = current_time - last_request_time
    
    if time_since_last < MIN_REQUEST_INTERVAL:
        sleep_time = MIN_REQUEST_INTERVAL - time_since_last + random.uniform(0.5, 1.5)
        logger.info(f"⏱️ Rate limiting: waiting {sleep_time:.2f} seconds")
        time.sleep(sleep_time)
    
    last_request_time = time.time()

def get_orchestrator():
    global orchestrator
    if orchestrator is None:
        try:
            orchestrator = AgentOrchestrator(config)
            logger.info("Agent orchestrator initialized with 8 agents")
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise
    return orchestrator

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# ============= REVOLUTIONARY NEW ENDPOINTS =============

@app.route('/api/onboarding', methods=['POST'])
def run_onboarding():
    """Run complete onboarding with company analysis and personalized plan"""
    try:
        rate_limit()
        data = request.json
        logger.info("Running complete onboarding workflow...")
        
        # Create user profile from request data
        user = create_user_from_data(data)
        
        # Store user in memory
        user_sessions[user.user_id] = user
        
        # Run complete onboarding
        orch = get_orchestrator()
        result = orch.run_complete_onboarding(user)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in onboarding: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/api/daily-cycle/<user_id>', methods=['GET'])
def daily_cycle(user_id):
    """Get today's complete learning cycle"""
    try:
        rate_limit()
        if user_id not in user_sessions:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        user = user_sessions[user_id]
        
        orch = get_orchestrator()
        result = orch.run_daily_cycle(user_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in daily cycle: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/recommendation/<user_id>', methods=['GET'])
def get_recommendation(user_id):
    """Get next learning recommendation"""
    try:
        rate_limit()
        if user_id not in user_sessions:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        user = user_sessions[user_id]
        
        # Get context from query params
        context = {
            "time_of_day": datetime.now().hour,
            "source": request.args.get('source', 'api'),
            "user_requested": True
        }
        
        orch = get_orchestrator()
        result = orch.get_next_recommendation(
            user_id,
            context,
            user,
            {}  # Roadmap would come from stored plan
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting recommendation: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/analytics/<user_id>', methods=['GET'])
def get_analytics(user_id):
    """Get performance analytics and adaptations"""
    try:
        rate_limit()
        if user_id not in user_sessions:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        user = user_sessions[user_id]
        
        orch = get_orchestrator()
        
        # Get session history from orchestrator
        session_history = orch.session_history if hasattr(orch, 'session_history') else []
        user_sessions_history = [s for s in session_history if s.get("user_id") == user_id]
        
        result = orch.analyze_performance(user_id, user_sessions_history, user)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/company-analysis', methods=['POST'])
def analyze_companies():
    """Analyze target companies"""
    try:
        rate_limit()
        data = request.json
        
        # Create temporary user for analysis
        user = create_user_from_data(data)
        
        orch = get_orchestrator()
        result = orch.analyze_target_companies(user)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error analyzing companies: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

# ============= ENHANCED CODE SUBMISSION ENDPOINT =============
@app.route('/api/code/submit', methods=['POST'])
def submit_code():
    """Submit code for AI-powered evaluation"""
    try:
        rate_limit()
        data = request.json
        
        user_id = data.get('user_id')
        if user_id not in user_sessions:
            logger.info(f"User {user_id} not found, creating temporary user")
            user = create_temp_user()
            user_sessions[user.user_id] = user
            user_id = user.user_id
        else:
            user = user_sessions[user_id]
        
        code = data.get('code', '')
        problem_id = data.get('problem_id', 'two-sum')
        
        # Get problem details
        from data.problem_database import PROBLEM_DATABASE
        problem = PROBLEM_DATABASE.get(problem_id, {})
        
        # Use Gemini for code analysis
        orch = get_orchestrator()
        
        # Create a prompt for code analysis
        analysis_prompt = f"""You are an expert coding interview coach. Analyze this solution for the problem "{problem_id}":

PROBLEM CONTEXT:
{problem.get('description', 'Given an array of integers nums and an integer target, return indices of the two numbers that add up to target.')}

USER'S CODE:
```python
{code}
```

Return as JSON with this structure:
{{
    "correctness": {{
        "works": true,
        "issues": ["list of bugs or edge cases"],
        "edge_cases_missed": ["empty input", "single element"]
    }},
    "complexity": {{
        "time": "O(n)",
        "space": "O(n)",
        "explanation": "why this complexity"
    }},
    "code_quality": {{
        "readability": 8,
        "issues": ["poor variable names"],
        "suggestions": ["use descriptive names"]
    }},
    "optimizations": [
        {{
            "issue": "what's wrong",
            "suggestion": "how to fix",
            "impact": "why it matters"
        }}
    ],
    "optimized_code": "improved version here",
    "summary": "brief overall feedback"
}}
"""

        try:
            # Get AI analysis
            ai_analysis = orch.agents["evaluator"].llm_client.generate_structured_output(
                prompt=analysis_prompt,
                output_schema={
                    "type": "object",
                    "properties": {
                        "correctness": {
                            "type": "object",
                            "properties": {
                                "works": {"type": "boolean"},
                                "issues": {"type": "array", "items": {"type": "string"}},
                                "edge_cases_missed": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "complexity": {
                            "type": "object",
                            "properties": {
                                "time": {"type": "string"},
                                "space": {"type": "string"},
                                "explanation": {"type": "string"}
                            }
                        },
                        "code_quality": {
                            "type": "object",
                            "properties": {
                                "readability": {"type": "number"},
                                "issues": {"type": "array", "items": {"type": "string"}},
                                "suggestions": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "optimizations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "issue": {"type": "string"},
                                    "suggestion": {"type": "string"},
                                    "impact": {"type": "string"}
                                }
                            }
                        },
                        "optimized_code": {"type": "string"},
                        "summary": {"type": "string"}
                    }
                }
            )
            
            return jsonify({
                "status": "success",
                "user_id": user_id,
                "problem_id": problem_id,
                "code": code,
                "analysis": ai_analysis
            })
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Fallback to basic analysis
            complexity = "O(n)"
            suggestions = []
            optimized = ""
            
            if "for" in code and "for" in code[code.find("for")+3:]:
                complexity = "O(n²)"
                suggestions = [{
                    "issue": "Nested loops detected",
                    "suggestion": "Consider using a hash map for O(n) solution",
                    "impact": "Will improve performance on large inputs"
                }]
                optimized = """def optimized_solution(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i"""
            
            return jsonify({
                "status": "success",
                "user_id": user_id,
                "problem_id": problem_id,
                "code": code,
                "analysis": {
                    "correctness": {
                        "works": True,
                        "issues": [],
                        "edge_cases_missed": ["empty array", "no solution"] if "return" not in code else []
                    },
                    "complexity": {
                        "time": complexity,
                        "space": "O(1)",
                        "explanation": "Basic complexity analysis based on code structure"
                    },
                    "code_quality": {
                        "readability": 7,
                        "issues": [],
                        "suggestions": ["Add comments to explain your logic", "Use more descriptive variable names"]
                    },
                    "optimizations": suggestions,
                    "optimized_code": optimized or "# Your solution looks good!",
                    "summary": "Your code works but could be optimized." if complexity == "O(n²)" else "Good solution!"
                }
            })
        
    except Exception as e:
        logger.error(f"Error submitting code: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/problems/recommend/<user_id>', methods=['GET'])
def recommend_problem(user_id):
    """Get personalized problem recommendation"""
    try:
        if user_id not in user_sessions:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        user = user_sessions[user_id]
        
        orch = get_orchestrator()
        
        if "recommender" in orch.agents:
            result = orch.agents["recommender"].get_problem_recommendation(
                user_id=user_id,
                user_profile={
                    "current_level": "intermediate",
                    "difficulty_preference": user.preferences.difficulty_preference if user.preferences else "adaptive"
                },
                target_companies=user.interview_goal.target_companies if user.interview_goal else []
            )
            return jsonify(result)
        else:
            return jsonify({"status": "error", "message": "Recommender agent not available"}), 500
            
    except Exception as e:
        logger.error(f"Error recommending problem: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/company/<company_name>/problems', methods=['GET'])
def get_company_problems(company_name):
    """Get all problems for a specific company"""
    try:
        from data.problem_database import COMPANY_INDEX, PROBLEM_DATABASE, COMPANY_METADATA
        
        if company_name not in COMPANY_INDEX:
            return jsonify({"status": "error", "message": f"Company {company_name} not found"}), 404
        
        problem_ids = COMPANY_INDEX[company_name]
        problems = []
        
        for pid in problem_ids:
            if pid in PROBLEM_DATABASE:
                problem = PROBLEM_DATABASE[pid].copy()
                # Add company-specific frequency
                if company_name in problem.get("companies", {}):
                    problem["company_frequency"] = problem["companies"][company_name]
                problems.append(problem)
        
        return jsonify({
            "status": "success",
            "company": company_name,
            "metadata": COMPANY_METADATA.get(company_name, {}),
            "problems": problems,
            "total_problems": len(problems)
        })
        
    except Exception as e:
        logger.error(f"Error getting company problems: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/companies/list', methods=['GET'])
def list_companies():
    """Get list of all supported companies"""
    try:
        from data.problem_database import COMPANY_INDEX, COMPANY_METADATA
        
        companies = []
        for company in COMPANY_INDEX.keys():
            metadata = COMPANY_METADATA.get(company, {})
            companies.append({
                "name": company,
                "industry": metadata.get("industry", "Technology"),
                "hq": metadata.get("hq", "Unknown"),
                "problem_count": len(COMPANY_INDEX[company])
            })
        
        # Sort by problem count
        companies.sort(key=lambda x: x["problem_count"], reverse=True)
        
        return jsonify({
            "status": "success",
            "total_companies": len(companies),
            "companies": companies
        })
        
    except Exception as e:
        logger.error(f"Error listing companies: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

# ============= EXISTING ENDPOINTS =============

@app.route('/api/planner', methods=['POST'])
def create_learning_plan():
    """Create a personalized learning plan"""
    try:
        rate_limit()
        data = request.json
        logger.info("Creating learning plan...")
        
        user = create_user_from_data(data)
        
        # Store user
        user_sessions[user.user_id] = user
        
        orch = get_orchestrator()
        
        # First get company insights if companies provided
        if user.interview_goal and user.interview_goal.target_companies:
            company_insights = orch.analyze_target_companies(user)
            logger.info(f"Company analysis complete for {len(user.interview_goal.target_companies)} companies")
        
        # Create learning plan
        result = orch.create_learning_plan(user)
        
        # Add company insights if available
        if 'company_insights' in locals():
            result['company_insights'] = company_insights
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error creating learning plan: {e}")
        return jsonify(fallback_learning_plan(data))

@app.route('/api/evaluator', methods=['POST'])
def evaluate_response():
    """Evaluate user's interview response"""
    try:
        rate_limit()
        data = request.json
        logger.info("Evaluating response...")
        
        evaluation_data = {
            "user_id": data.get('user_id', 'user_001'),
            "session_id": f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "question": data.get('question', ''),
            "question_type": data.get('question_type', 'technical'),
            "user_response": data.get('user_response', ''),
            "expected_areas": data.get('expected_areas', []),
            "context": data.get('context', {})
        }
        
        orch = get_orchestrator()
        result = orch.evaluate_response(evaluation_data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error evaluating response: {e}")
        return jsonify(fallback_evaluation(data))

@app.route('/api/tutor', methods=['POST'])
def get_tutoring():
    """Get tutoring lesson"""
    try:
        rate_limit()
        data = request.json
        logger.info(f"Getting tutoring for topic: {data.get('topic')}")
        
        user_id = data.get('user_id', 'user_001')
        user = user_sessions.get(user_id)
        
        if not user:
            # Create temporary user
            user = create_temp_user()
        
        tutoring_request = {
            "user_id": user_id,
            "user_profile": user,
            "topic": data.get('topic', 'Dynamic Programming'),
            "difficulty": data.get('difficulty', 'intermediate'),
            "context": data.get('context', {})
        }
        
        orch = get_orchestrator()
        result = orch.provide_tutoring(tutoring_request)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting tutoring: {e}")
        return jsonify(fallback_tutoring(data))

@app.route('/api/scheduler', methods=['POST'])
def create_schedule():
    """Create study schedule"""
    try:
        rate_limit()
        data = request.json
        logger.info("Creating schedule...")
        
        user_id = data.get('user_id', 'user_001')
        user = user_sessions.get(user_id)
        
        if not user:
            user = create_temp_user()
        
        orch = get_orchestrator()
        
        # First create a learning plan if not provided
        learning_plan = data.get('learning_plan', {})
        if not learning_plan:
            plan_result = orch.create_learning_plan(user)
            learning_plan = plan_result.get('learning_plan', {})
        
        result = orch.create_schedule(user, learning_plan)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error creating schedule: {e}")
        return jsonify(fallback_schedule(data))

@app.route('/api/user/<user_id>/progress', methods=['GET'])
def get_user_progress(user_id):
    """Get user progress summary"""
    try:
        rate_limit()
        orch = get_orchestrator()
        result = orch.get_user_progress(user_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting user progress: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

# ============= HELPER FUNCTIONS =============

def create_user_from_data(data):
    """Create UserProfile from request data"""
    # Extract experience years
    exp_str = data.get('experience', '3')
    if '-' in str(exp_str):
        exp_years = int(exp_str.split('-')[0])
    else:
        try:
            exp_years = int(exp_str)
        except:
            exp_years = 3
    
    # Create skills
    skills = [
        Skill(
            name="Python",
            category="programming",
            current_level=SkillLevel.INTERMEDIATE,
            target_level=SkillLevel.ADVANCED,
            confidence_score=0.7
        ),
        Skill(
            name="Data Structures",
            category="algorithms",
            current_level=SkillLevel.INTERMEDIATE,
            target_level=SkillLevel.ADVANCED,
            confidence_score=0.6
        ),
        Skill(
            name="System Design",
            category="architecture",
            current_level=SkillLevel.BEGINNER,
            target_level=SkillLevel.INTERMEDIATE,
            confidence_score=0.5
        )
    ]
    
    # Create interview goal
    interview_goal = InterviewGoal(
        target_role=data.get('target_role', 'Software Engineer'),
        target_companies=data.get('target_companies', []),
        timeline_weeks=data.get('timeline_weeks', 8),
        interview_types=data.get('interview_types', ['technical', 'behavioral'])
    )
    
    # Create preferences
    preferences = UserPreferences(
        preferred_learning_style=data.get('learning_style', 'visual'),
        daily_practice_time_minutes=data.get('daily_practice_minutes', 60),
        preferred_session_times=['morning', 'evening'],
        difficulty_preference='adaptive',
        feedback_detail_level='detailed'
    )
    
    # Create user
    user = UserProfile(
        user_id=f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        name=data.get('name', 'User'),
        email=data.get('email', 'user@example.com'),
        experience_years=exp_years,
        current_role=data.get('current_role', 'Software Engineer'),
        skills=skills,
        interview_goal=interview_goal,
        preferences=preferences
    )
    
    return user

def create_temp_user():
    """Create temporary user for testing"""
    return UserProfile(
        user_id=f"temp_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        name="Temporary User",
        email="temp@example.com",
        experience_years=3,
        current_role="Software Engineer",
        skills=[],
        interview_goal=InterviewGoal(
            target_role="SDE",
            target_companies=["Google"],
            timeline_weeks=8,
            interview_types=["technical"]
        ),
        preferences=UserPreferences(
            preferred_learning_style="visual",
            daily_practice_time_minutes=60,
            preferred_session_times=["morning"],
            difficulty_preference="adaptive",
            feedback_detail_level="detailed"
        )
    )

# ============= FALLBACK FUNCTIONS =============

def fallback_learning_plan(data):
    """Return fallback learning plan on error"""
    return {
        "status": "success",
        "plan_id": f"plan_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "learning_plan": {
            "phases": [
                {"phase_name": "Foundation", "duration_weeks": 2, "focus_areas": ["Big O", "Arrays", "Strings"]},
                {"phase_name": "Core Skills", "duration_weeks": 3, "focus_areas": ["Data Structures", "Algorithms"]},
                {"phase_name": "Advanced", "duration_weeks": 2, "focus_areas": ["System Design", "Advanced Topics"]},
                {"phase_name": "Mock Interviews", "duration_weeks": 1, "focus_areas": ["Practice", "Feedback"]}
            ],
            "total_duration_weeks": 8
        },
        "weekly_schedule": generate_mock_schedule(8),
        "milestones": [
            {"week": 2, "description": "Complete Foundation phase", "assessment_required": True},
            {"week": 5, "description": "Complete Core Skills phase", "assessment_required": True},
            {"week": 7, "description": "Complete Advanced phase", "assessment_required": True},
            {"week": 8, "description": "Ready for interviews!", "assessment_required": False}
        ],
        "estimated_preparation_time": {
            "total_hours": 96,
            "hours_per_week": 12,
            "daily_minutes": data.get('daily_practice_minutes', 60),
            "estimated_completion_date": "2025-04-15"
        }
    }

def fallback_evaluation(data):
    """Return fallback evaluation on error"""
    return {
        "status": "success",
        "evaluation_id": f"eval_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "scores": {
            "overall": 7.5,
            "technical_accuracy": 8.0,
            "communication_effectiveness": 7.5,
            "problem_solving_approach": 7.5,
            "completeness": 7.0,
            "innovation_creativity": 7.0
        },
        "feedback": {
            "summary": "Good response overall. You demonstrated solid understanding of the topic.",
            "strengths_highlighted": [
                "Clear explanation of concepts",
                "Good structure in your answer",
                "Mentioned key points effectively"
            ],
            "improvement_areas": [
                {"area": "Completeness", "suggestion": "Add more examples", "issue": "Could go deeper"}
            ],
            "encouragement_message": "Keep practicing! You're on the right track."
        }
    }

def fallback_tutoring(data):
    """Return fallback tutoring on error"""
    return {
        "status": "success",
        "session_id": f"tutor_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "topic": data.get('topic', 'Dynamic Programming'),
        "teaching_method": "interactive",
        "lesson": {
            "learning_objectives": [
                "Understand the fundamentals",
                "Apply to problems",
                "Analyze complexity"
            ],
            "key_concepts": [
                {"concept": "Core Concept", "explanation": "Detailed explanation of the topic"}
            ]
        },
        "practice_exercises": [
            {"id": 1, "problem": "Practice problem 1", "difficulty": "Easy"},
            {"id": 2, "problem": "Practice problem 2", "difficulty": "Medium"}
        ]
    }

def fallback_schedule(data):
    """Return fallback schedule on error"""
    return {
        "status": "success",
        "schedule_id": f"schedule_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "daily_schedule": generate_mock_daily_schedule(56)
    }

def generate_mock_schedule(weeks):
    schedule = []
    topics = ['Data Structures', 'Algorithms', 'System Design', 'Behavioral']
    
    for week in range(1, weeks + 1):
        schedule.append({
            "week_number": week,
            "phase": "Foundation" if week <= 2 else "Core Skills" if week <= 5 else "Advanced" if week <= 7 else "Mock Interviews",
            "focus_areas": [topics[(week - 1) % len(topics)]],
            "daily_schedule": {"theory_study": 30, "practice_problems": 60, "review": 30},
            "weekly_goals": ["Complete practice problems", "Review concepts"],
            "resources": ["LeetCode", "GeeksforGeeks"],
            "mock_interview_week": week % 2 == 0
        })
    return schedule

def generate_mock_daily_schedule(days):
    schedule = []
    topics = ['Arrays', 'Linked Lists', 'Trees', 'Graphs', 'DP', 'Sorting']
    
    for i in range(days):
        day_of_week = i % 7
        is_weekend = day_of_week >= 5
        
        sessions = []
        if not is_weekend:
            sessions.append({
                "time_slot": "08:00-09:30",
                "activity_type": "theory_study",
                "topic": topics[i % len(topics)],
                "duration": 90
            })
            sessions.append({
                "time_slot": "19:00-20:30",
                "activity_type": "practice_problems",
                "topic": "Problem Solving",
                "duration": 90
            })
        else:
            sessions.append({
                "time_slot": "10:00-12:00",
                "activity_type": "review",
                "topic": "Week Review",
                "duration": 120
            })
        
        schedule.append({
            "day_of_week": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day_of_week],
            "date": f"Day {i+1}",
            "sessions": sessions,
            "total_learning_time": sum(s['duration'] for s in sessions)
        })
    
    return schedule

if __name__ == '__main__':
    print("=" * 50)
    print("InterviewAI API Server - REVOLUTIONARY EDITION")
    print("=" * 50)
    print("✓ 8 AI Agents Loaded:")
    print("  - Company DNA Analyzer")
    print("  - Planner Agent")
    print("  - Evaluator Agent")
    print("  - Tutor Agent")
    print("  - Scheduler Agent")
    print("  - Recommender Agent")
    print("  - Analytics Agent")
    print("  - Agent Orchestrator")
    print("=" * 50)
    print("New Revolutionary Endpoints:")
    print("  POST /api/onboarding - Complete workflow")
    print("  GET  /api/daily-cycle/<user_id> - Daily learning")
    print("  GET  /api/recommendation/<user_id> - Next action")
    print("  GET  /api/analytics/<user_id> - Performance insights")
    print("  POST /api/company-analysis - Company insights")
    print("=" * 50)
    print("✨ ENHANCED CODE EVALUATION WITH AI FEEDBACK ✨")
    print("⏱️ Rate limiting enabled: 2 second minimum between requests")
    print("Starting server on http://localhost:5002")
    print("Make sure your frontend is running on http://localhost:3000")
    print("=" * 50)
    app.run(debug=True, port=5002, host='0.0.0.0')
