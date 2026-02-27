import json
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from models.user_profile import UserProfile, Skill, InterviewGoal, UserPreferences, SkillLevel
from agents.agent_orchestrator import AgentOrchestrator

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/framework.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def setup_sample_user() -> UserProfile:
    """Create a sample user profile for testing"""
    
    skills = [
        Skill(
            name="Python",
            category="programming",
            current_level=SkillLevel.ADVANCED,
            target_level=SkillLevel.EXPERT,
            confidence_score=0.8
        ),
        Skill(
            name="System Design",
            category="architecture",
            current_level=SkillLevel.INTERMEDIATE,
            target_level=SkillLevel.ADVANCED,
            confidence_score=0.6
        ),
        Skill(
            name="Data Structures",
            category="algorithms",
            current_level=SkillLevel.INTERMEDIATE,
            target_level=SkillLevel.ADVANCED,
            confidence_score=0.7
        ),
        Skill(
            name="Communication",
            category="soft_skills",
            current_level=SkillLevel.ADVANCED,
            target_level=SkillLevel.EXPERT,
            confidence_score=0.75
        )
    ]
    
    interview_goal = InterviewGoal(
        target_role="Senior Software Engineer",
        target_companies=["Google", "Microsoft", "Amazon"],
        timeline_weeks=8,
        interview_types=["technical", "system_design", "behavioral"]
    )
    
    preferences = UserPreferences(
        preferred_learning_style="visual",
        daily_practice_time_minutes=90,
        preferred_session_times=["morning", "evening"],
        difficulty_preference="adaptive",
        feedback_detail_level="detailed"
    )
    
    user = UserProfile(
        user_id="user_001",
        name="John Doe",
        email="john.doe@example.com",
        experience_years=5,
        current_role="Software Engineer",
        skills=skills,
        interview_goal=interview_goal,
        preferences=preferences
    )
    
    return user

def test_gemini_connection():
    """Test Gemini API connection"""
    print("\n" + "="*50)
    print("TESTING GEMINI CONNECTION")
    print("="*50)
    
    try:
        import google.generativeai as genai
        
        # Get API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your-gemini-api-key-here":
            print("✗ GOOGLE_API_KEY not set. Please set it in .env file")
            return False
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # List available models
        models = list(genai.list_models())
        print(f"✓ Connected to Gemini API")
        print(f"✓ Found {len(models)} available models")
        
        # Find a working model
        working_model = None
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                working_model = model.name
                print(f"✓ Found working model: {model.display_name} ({model.name})")
                break
        
        if working_model:
            # Test a simple generation with the working model
            model = genai.GenerativeModel(working_model)
            response = model.generate_content("Hello, Gemini! Reply with 'OK' if you can hear me.")
            
            if response.text:
                print(f"✓ Test generation successful: {response.text.strip()}")
                return True
            else:
                print("✗ No response from Gemini")
                return False
        else:
            print("✗ No suitable model found")
            return False
            
    except Exception as e:
        print(f"✗ Gemini connection failed: {str(e)}")
        return False

# ============= NEW REVOLUTIONARY DEMO FUNCTIONS =============

def demo_company_analyzer(orchestrator: AgentOrchestrator, user: UserProfile):
    """Demonstrate company analyzer agent"""
    
    print("\n" + "="*50)
    print("DEMO: COMPANY DNA ANALYZER AGENT (NEW)")
    print("="*50)
    
    result = orchestrator.analyze_target_companies(user)
    
    if result["status"] == "success":
        print(f"✓ Company analysis completed successfully!")
        print(f"Analysis ID: {result['analysis_id']}")
        
        # Save analysis
        with open(f"exports/company_analysis_{result['analysis_id']}.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"\nCompanies Analyzed: {', '.join(result['company_insights'].keys())}")
        
        for company, insights in result['company_insights'].items():
            print(f"\n{company}:")
            print(f"  Core Topics: {', '.join(insights.get('core_topics', [])[:3])}")
            print(f"  Interview Rounds: {len(insights.get('interview_rounds', []))}")
            print(f"  Success Traits: {', '.join(insights.get('success_traits', [])[:2])}")
        
        print(f"\nPriority Topics (Across Companies):")
        for topic in result.get('priority_topics', [])[:5]:
            print(f"  • {topic['topic']} (Importance: {topic['importance']:.2f})")
        
        print(f"\nCompany-Specific Tips:")
        for company, tips in result.get('company_specific_tips', {}).items():
            if tips:
                print(f"  {company}: {tips[0]}")
    else:
        print(f"✗ Error: {result.get('error')}")

def demo_recommender_agent(orchestrator: AgentOrchestrator, user: UserProfile):
    """Demonstrate recommender agent"""
    
    print("\n" + "="*50)
    print("DEMO: CONTEXT RECOMMENDER AGENT (NEW)")
    print("="*50)
    
    # Simulate context
    context = {
        "time_of_day": 10,  # 10 AM
        "recent_sessions": 3,
        "last_session_time": datetime.now().isoformat(),
        "stuck_on_topic": None
    }
    
    # Simulate recent performance
    recent_performance = {
        "needs_review": False,
        "ready_to_advance": True,
        "weak_topic": None,
        "last_score": 8.5,
        "trend": "improving"
    }
    
    result = orchestrator.get_next_recommendation(
        user.user_id,
        context,
        user,
        {}  # Would pass actual roadmap
    )
    
    if result["status"] == "success":
        print(f"✓ Recommendation generated successfully!")
        print(f"Recommendation ID: {result['recommendation_id']}")
        
        # Save recommendation
        with open(f"exports/recommendation_{result['recommendation_id']}.json", "w") as f:
            json.dump(result, f, indent=2)
        
        primary = result.get('primary_recommendation', {})
        print(f"\nPrimary Recommendation:")
        print(f"  Type: {primary.get('type', 'N/A')}")
        print(f"  Action: {primary.get('action', 'N/A')}")
        print(f"  Topic: {primary.get('topic', 'N/A')}")
        print(f"  Duration: {primary.get('duration_minutes', 0)} minutes")
        print(f"  Confidence: {primary.get('confidence', 0)*100:.0f}%")
        
        print(f"\nReasoning: {result.get('reasoning', 'N/A')}")
        
        print(f"\nAlternative Options:")
        for alt in result.get('alternatives', [])[:2]:
            print(f"  • {alt.get('action')} ({alt.get('duration_minutes')} mins)")
        
        print(f"\nEstimated Impact:")
        impact = result.get('estimated_impact', {})
        print(f"  Expected Outcome: {impact.get('expected_outcome', {})}")
        print(f"  Readiness Impact: {impact.get('readiness_impact', 'N/A')}")
    else:
        print(f"✗ Error: {result.get('error')}")

def demo_analytics_agent(orchestrator: AgentOrchestrator, user: UserProfile):
    """Demonstrate analytics agent"""
    
    print("\n" + "="*50)
    print("DEMO: PERFORMANCE ANALYTICS AGENT (NEW)")
    print("="*50)
    
    # First create some sessions (simulated)
    session_history = [
        {
            "agent": "evaluator",
            "result": {
                "scores": {"overall": 7.5},
                "improvement_areas": [{"category": "Graph Algorithms"}]
            },
            "timestamp": datetime.now().isoformat()
        },
        {
            "agent": "evaluator",
            "result": {
                "scores": {"overall": 8.0},
                "improvement_areas": [{"category": "Dynamic Programming"}]
            },
            "timestamp": datetime.now().isoformat()
        },
        {
            "agent": "evaluator",
            "result": {
                "scores": {"overall": 8.5},
                "improvement_areas": []
            },
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    result = orchestrator.analyze_performance(user.user_id, session_history, user)
    
    if result["status"] == "success":
        print(f"✓ Analytics generated successfully!")
        print(f"Analytics ID: {result['analytics_id']}")
        
        # Save analytics
        with open(f"exports/analytics_{result['analytics_id']}.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"\nPerformance Metrics:")
        metrics = result.get('metrics', {})
        print(f"  Total Sessions: {metrics.get('total_sessions', 0)}")
        print(f"  Total Practice Hours: {metrics.get('total_practice_hours', 0)}")
        print(f"  Average Score: {metrics.get('avg_score', 0)}/10")
        print(f"  Improvement Rate: {metrics.get('improvement_rate', 0)}%")
        print(f"  Consistency: {metrics.get('consistency', 0)}%")
        
        print(f"\nPerformance Patterns:")
        patterns = result.get('performance_patterns', {})
        print(f"  Strong Topics: {', '.join(patterns.get('strong_topics', [])[:3])}")
        print(f"  Weak Topics: {', '.join(patterns.get('weak_topics', [])[:3])}")
        print(f"  Learning Rate: {patterns.get('learning_rate', 0)}%")
        print(f"  Plateau Detected: {patterns.get('plateau_detected', False)}")
        
        print(f"\nSystem Adaptations:")
        adaptations = result.get('adaptations', {})
        for adapt_type, adapt_list in adaptations.items():
            if adapt_list:
                print(f"  {adapt_type.replace('_', ' ').title()}:")
                for a in adapt_list[:2]:
                    print(f"    • {a.get('action')} - {a.get('reason', '')}")
        
        print(f"\nPredictions:")
        predictions = result.get('predictions', {})
        print(f"  Projected Readiness (4 weeks): {predictions.get('projected_readiness_4weeks', 0)}%")
        print(f"  Burnout Risk: {predictions.get('burnout_risk', 'low')}")
        print(f"  Persistent Weak Areas: {', '.join(predictions.get('persistent_weak_areas', []))}")
        
        print(f"\nExecutive Summary:")
        print(f"  {result.get('report', {}).get('executive_summary', 'N/A')}")
    else:
        print(f"✗ Error: {result.get('error')}")

def demo_complete_onboarding(orchestrator: AgentOrchestrator, user: UserProfile):
    """Demonstrate complete onboarding workflow"""
    
    print("\n" + "="*50)
    print("DEMO: COMPLETE ONBOARDING WORKFLOW (REVOLUTIONARY)")
    print("="*50)
    
    result = orchestrator.run_complete_onboarding(user)
    
    if result["status"] == "success":
        print(f"✓ Onboarding completed successfully!")
        print(f"User ID: {result['user_id']}")
        
        print(f"\nCompany Insights Generated: {len(result.get('company_insights', {}).get('company_insights', {}))}")
        print(f"Learning Plan Created: {result.get('learning_plan', {}).get('plan_id', 'N/A')}")
        print(f"First Recommendation Ready: {result.get('first_recommendation', {}).get('status', 'N/A')}")
        
        print(f"\nNext Steps: {result.get('next_steps', 'N/A')}")
        
        # Save onboarding result
        with open(f"exports/onboarding_{user.user_id}.json", "w") as f:
            json.dump(result, f, indent=2)
    else:
        print(f"✗ Error: {result.get('error')}")

def demo_daily_cycle(orchestrator: AgentOrchestrator, user: UserProfile):
    """Demonstrate daily learning cycle"""
    
    print("\n" + "="*50)
    print("DEMO: DAILY LEARNING CYCLE (REVOLUTIONARY)")
    print("="*50)
    
    # Store user in orchestrator's user_sessions
    orchestrator.user_sessions[user.user_id] = user
    
    result = orchestrator.run_daily_cycle(user.user_id)
    
    if result["status"] == "success":
        print(f"✓ Daily cycle completed successfully!")
        print(f"Date: {result['date']}")
        
        print(f"\nToday's Recommendation:")
        rec = result.get('recommendation', {}).get('primary_recommendation', {})
        print(f"  • {rec.get('action')} on {rec.get('topic')}")
        print(f"  • Duration: {rec.get('duration_minutes')} minutes")
        
        print(f"\nToday's Schedule:")
        schedule = result.get('schedule', {}).get('daily_session', {})
        for session in schedule.get('sessions', [])[:2]:
            print(f"  • {session.get('time_slot')}: {session.get('topic')} ({session.get('activity_type')})")
        
        if result.get('analytics'):
            print(f"\nPerformance Analytics Available")
            metrics = result['analytics'].get('metrics', {})
            print(f"  Current Avg Score: {metrics.get('avg_score', 0)}/10")
        
        print(f"\nMotivation: {result.get('motivation', {}).get('quote', 'N/A')}")
        
        # Save daily cycle result
        with open(f"exports/daily_cycle_{user.user_id}_{datetime.now().strftime('%Y%m%d')}.json", "w") as f:
            json.dump(result, f, indent=2)
    else:
        print(f"✗ Error: {result.get('error')}")

# ============= EXISTING DEMO FUNCTIONS (UPDATED) =============

def demo_planner_agent(orchestrator: AgentOrchestrator, user: UserProfile):
    """Demonstrate planner agent functionality"""
    
    print("\n" + "="*50)
    print("DEMO: PLANNER AGENT")
    print("="*50)
    
    result = orchestrator.create_learning_plan(user)
    
    if result["status"] == "success":
        print(f"✓ Learning plan created successfully!")
        print(f"Plan ID: {result['plan_id']}")
        
        # Save the plan
        with open(f"exports/learning_plan_{result['plan_id']}.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"✓ Plan saved to exports/learning_plan_{result['plan_id']}.json")
        
        print(f"\nTotal duration: {result['learning_plan']['total_duration_weeks']} weeks")
        print(f"Phases: {len(result['learning_plan']['phases'])}")
        
        print("\nWeekly Schedule Preview:")
        for i, week in enumerate(result.get("weekly_schedule", [])[:2]):
            print(f"  Week {week['week_number']}: {week['phase']}")
            print(f"    Focus: {', '.join(week['focus_areas'][:2])}")
            print(f"    Daily time: {week['daily_schedule']['total_daily_minutes']} minutes")
        
        print(f"\nEstimated completion: {result['estimated_preparation_time']['estimated_completion_date']}")
    else:
        print(f"✗ Error: {result.get('error')}")

def demo_evaluator_agent(orchestrator: AgentOrchestrator):
    """Demonstrate evaluator agent functionality"""
    
    print("\n" + "="*50)
    print("DEMO: EVALUATOR AGENT")
    print("="*50)
    
    evaluation_data = {
        "user_id": "user_001",
        "session_id": "session_001",
        "question": "Explain how HashMap works in Java and its time complexity for various operations.",
        "question_type": "technical",
        "user_response": """HashMap in Java uses an array of buckets. Each bucket contains a linked list of entries. 
        When you put a key-value pair, it calculates the hash of the key, uses modulo to find the bucket index, 
        and stores it in that bucket's linked list. For get operations, it calculates the hash again, finds the bucket, 
        and traverses the linked list to find the matching key. The average time complexity is O(1) for both get and put, 
        but worst-case is O(n) if all entries end up in the same bucket due to poor hash function or many collisions. 
        In Java 8, when buckets get too large, they convert to tree structures for better performance.""",
        "expected_areas": ["hashing mechanism", "collision resolution", "time complexity", "internal structure"],
        "context": {
            "experience_years": 5,
            "target_role": "Senior Software Engineer",
            "difficulty": "intermediate"
        }
    }
    
    result = orchestrator.evaluate_response(evaluation_data)
    
    if result["status"] == "success":
        print(f"✓ Evaluation completed successfully!")
        print(f"Evaluation ID: {result['evaluation_id']}")
        print(f"Overall Score: {result['scores']['overall']}/10 ({result['scores']['normalized_overall']}%)")
        
        # Save evaluation
        with open(f"exports/evaluation_{result['evaluation_id']}.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"\nCategory Scores:")
        for category, score in result["scores"].items():
            if category not in ["overall", "normalized_overall"]:
                print(f"  {category.replace('_', ' ').title()}: {score}/10")
        
        print(f"\nFeedback Summary: {result['feedback'].get('summary', 'N/A')[:150]}...")
        
        if result.get("improvement_areas"):
            print("\nImprovement Areas:")
            for area in result["improvement_areas"][:2]:
                print(f"  • {area['category']} (Score: {area['current_score']}/10)")
    else:
        print(f"✗ Error: {result.get('error')}")

def demo_tutor_agent(orchestrator: AgentOrchestrator, user: UserProfile):
    """Demonstrate tutor agent functionality"""
    
    print("\n" + "="*50)
    print("DEMO: TUTOR AGENT")
    print("="*50)
    
    tutoring_request = {
        "user_id": user.user_id,
        "user_profile": user,
        "topic": "Dynamic Programming",
        "difficulty": "intermediate",
        "context": {
            "previous_topics": ["Recursion", "Memoization"],
            "strengths": ["Problem decomposition"],
            "weaknesses": ["State transition formulation"]
        }
    }
    
    result = orchestrator.provide_tutoring(tutoring_request)
    
    if result["status"] == "success":
        print(f"✓ Tutoring session created successfully!")
        print(f"Session ID: {result['session_id']}")
        print(f"Topic: {result['topic']}")
        print(f"Teaching Method: {result['teaching_method']}")
        
        # Save tutoring session
        with open(f"exports/tutoring_{result['session_id']}.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"\nLesson Objectives:")
        for obj in result["lesson"]["learning_objectives"][:3]:
            print(f"  • {obj}")
        
        print(f"\nKey Concepts:")
        for concept in result["lesson"]["key_concepts"][:2]:
            print(f"  • {concept['concept']}: {concept['explanation'][:80]}...")
        
        print(f"\nPractice Exercises: {len(result['practice_exercises'])}")
        print(f"Estimated Time: {result['estimated_completion_time']['total_minutes']} minutes")
    else:
        print(f"✗ Error: {result.get('error')}")

def demo_scheduler_agent(orchestrator: AgentOrchestrator, user: UserProfile):
    """Demonstrate scheduler agent functionality"""
    
    print("\n" + "="*50)
    print("DEMO: SCHEDULER AGENT")
    print("="*50)
    
    # First create a learning plan
    plan_result = orchestrator.create_learning_plan(user)
    
    if plan_result["status"] == "success":
        result = orchestrator.create_schedule(user, plan_result["learning_plan"])
        
        if result["status"] == "success":
            print(f"✓ Schedule created successfully!")
            print(f"Schedule ID: {result['schedule_id']}")
            print(f"Period: {result['schedule_period']['start_date']} to {result['schedule_period']['end_date']}")
            
            # Save schedule
            with open(f"exports/schedule_{result['schedule_id']}.json", "w") as f:
                json.dump(result, f, indent=2)
            
            print(f"Total Sessions: {result['schedule_metrics']['total_sessions']}")
            print(f"Total Hours: {result['schedule_metrics']['total_hours']}")
            
            print(f"\nOptimization Techniques Applied:")
            for technique in result["optimization_techniques"][:3]:
                print(f"  • {technique['technique'].replace('_', ' ').title()}")
            
            print(f"\nDaily Schedule (First 3 days):")
            for day in result["daily_schedule"][:3]:
                print(f"\n{day['date']} ({day['day_of_week']}):")
                for session in day["sessions"][:2]:
                    print(f"  {session['time_slot']}: {session['topic']} ({session['activity_type']})")
            
            print(f"\nReminders: {len(result['reminders'])} scheduled")
        else:
            print(f"✗ Error: {result.get('error')}")
    else:
        print(f"✗ Could not create schedule: {plan_result.get('error')}")

def main():
    """Main function to run the Gemini demo"""
    
    print("="*60)
    print("GEMINI-BASED INTERVIEW AI FRAMEWORK - REVOLUTIONARY EDITION")
    print("="*60)
    print("\n8 AGENT SYSTEM LOADED:")
    print("  1. Company DNA Analyzer (NEW)")
    print("  2. Planner Agent")
    print("  3. Evaluator Agent")
    print("  4. Tutor Agent")
    print("  5. Scheduler Agent")
    print("  6. Recommender Agent (NEW)")
    print("  7. Analytics Agent (NEW)")
    print("  8. Agent Orchestrator")
    print("="*60)
    
    # Test Gemini connection first
    if not test_gemini_connection():
        print("\nPlease fix Gemini API connection issues and try again.")
        return
    
    # Gemini configuration
    config = {
        "llm_config": {
            "provider": "google",
            "model": os.getenv("MODEL_NAME", "gemini-1.5-pro"),
            "temperature": 0.7,
            "generation_config": {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": int(os.getenv("MAX_TOKENS", 4096)),
            },
            "safety_settings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
            ]
        },
        "scheduling_constraints": {
            "default_timezone": "UTC",
            "max_daily_sessions": 3,
            "min_session_gap": 30
        }
    }
    
    # Initialize orchestrator
    print("\nInitializing 8-Agent Orchestrator...")
    try:
        orchestrator = AgentOrchestrator(config)
        print("✓ All 8 agents initialized successfully!")
    except Exception as e:
        print(f"✗ Failed to initialize orchestrator: {str(e)}")
        return
    
    # Setup sample user
    print("\nCreating sample user profile...")
    user = setup_sample_user()
    print(f"✓ User profile created: {user.name} ({user.experience_years} years experience)")
    print(f"  Target: {user.interview_goal.target_role} at {', '.join(user.interview_goal.target_companies)}")
    
    # Store user in orchestrator
    orchestrator.user_sessions[user.user_id] = user
    
    # Run all demos
    print("\n" + "="*60)
    print("RUNNING COMPREHENSIVE DEMO")
    print("="*60)
    
    # NEW REVOLUTIONARY AGENTS
    demo_company_analyzer(orchestrator, user)
    demo_recommender_agent(orchestrator, user)
    demo_analytics_agent(orchestrator, user)
    
    # REVOLUTIONARY WORKFLOWS
    demo_complete_onboarding(orchestrator, user)
    demo_daily_cycle(orchestrator, user)
    
    # EXISTING AGENTS
    demo_planner_agent(orchestrator, user)
    demo_evaluator_agent(orchestrator)
    demo_tutor_agent(orchestrator, user)
    demo_scheduler_agent(orchestrator, user)
    
    print("\n" + "="*60)
    print("REVOLUTIONARY DEMO COMPLETED SUCCESSFULLY!")
    print("="*60)
    
    # Export summary
    summary = {
        "framework": "Gemini-based Interview AI - Revolutionary Edition",
        "timestamp": datetime.now().isoformat(),
        "user": user.name,
        "experience_years": user.experience_years,
        "target_role": user.interview_goal.target_role,
        "target_companies": user.interview_goal.target_companies,
        "gemini_model": config["llm_config"]["model"],
        "agents_used": 8,
        "demo_completed": True,
        "files_generated": [
            "company_analysis_*.json",
            "recommendation_*.json", 
            "analytics_*.json",
            "onboarding_*.json",
            "daily_cycle_*.json",
            "learning_plan_*.json",
            "evaluation_*.json",
            "tutoring_*.json",
            "schedule_*.json"
        ]
    }
    
    with open("exports/revolutionary_demo_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n✓ Demo summary saved to 'exports/revolutionary_demo_summary.json'")
    print("\nCheck the 'exports' folder for generated files:")
    print("- company_analysis_*.json - Company DNA insights")
    print("- recommendation_*.json - Next action recommendations")
    print("- analytics_*.json - Performance patterns & adaptations")
    print("- onboarding_*.json - Complete onboarding workflow")
    print("- daily_cycle_*.json - Daily learning cycles")
    print("- Plus all original agent outputs")

if __name__ == "__main__":
    main()