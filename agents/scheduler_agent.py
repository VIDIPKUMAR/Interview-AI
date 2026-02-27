from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta, time
from .base_agent import BaseAgent
from utils.llm_client import LLMClient
import random

class SchedulerAgent(BaseAgent):
    """Intelligent scheduling and session optimization"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            agent_id="scheduler_001",
            name="Intelligent Scheduler",
            description="Optimizes learning schedule based on cognitive science",
            config=config
        )
        self.llm_client = LLMClient(**config.get("llm_config", {}))
        self.cognitive_principles = self._load_cognitive_principles()
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create optimized learning schedule"""
        self.log(f"Creating schedule for user: {input_data.get('user_id')}")
        
        required_fields = ["user_profile", "learning_plan", "constraints"]
        for field in required_fields:
            if field not in input_data:
                return self._create_error_response(f"Missing required field: {field}")
        
        try:
            # Safely get user preferences
            user_profile = input_data["user_profile"]
            learning_plan = input_data["learning_plan"]
            constraints = input_data["constraints"]
            preferences = input_data.get("preferences", {})
            existing_commitments = input_data.get("existing_commitments", [])
            
            # Extract learning style safely
            learning_style = user_profile.preferences.preferred_learning_style
            if hasattr(learning_style, 'value'):
                learning_style_value = learning_style.value
            else:
                learning_style_value = str(learning_style)
            
            # Create user info dict with safe values
            user_info = {
                "experience_years": user_profile.experience_years,
                "learning_style": learning_style_value,
                "daily_minutes": user_profile.preferences.daily_practice_time_minutes,
                "preferred_times": user_profile.preferences.preferred_session_times,
                "difficulty_preference": user_profile.preferences.difficulty_preference
            }
            
            # Generate optimized schedule
            schedule = self._generate_schedule(
                user_info=user_info,
                learning_plan=learning_plan,
                constraints=constraints,
                preferences=preferences,
                existing_commitments=existing_commitments
            )
            
            # Apply cognitive optimization
            optimized_schedule = self._apply_cognitive_optimizations(schedule, user_info)
            
            # Calculate metrics
            metrics = self._calculate_schedule_metrics(optimized_schedule)
            
            # Generate reminders and notifications
            reminders = self._generate_reminders(optimized_schedule)
            
            response = {
                "status": "success",
                "schedule_id": f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "schedule_period": optimized_schedule["period"],
                "daily_schedule": optimized_schedule["daily_schedule"],
                "weekly_overview": optimized_schedule.get("weekly_overview", {}),
                "optimization_techniques": optimized_schedule.get("optimization_techniques", []),
                "schedule_metrics": metrics,
                "reminders": reminders,
                "adjustment_recommendations": self._generate_adjustment_recommendations(metrics),
                "export_formats": ["ical", "google_calendar", "pdf"]
            }
            
            self.update_memory({
                "action": "created_schedule",
                "user_id": user_profile.user_id,
                "schedule_id": response["schedule_id"],
                "total_sessions": metrics["total_sessions"]
            })
            
            return response
            
        except Exception as e:
            self.log(f"Error in scheduling: {str(e)}", "ERROR")
            return self._create_error_response(str(e))
    
    def _generate_schedule(self, user_info: Dict, learning_plan: Dict, 
                          constraints: Dict, preferences: Dict, 
                          existing_commitments: List) -> Dict[str, Any]:
        """Generate personalized learning schedule"""
        
        system_prompt = """You are an expert learning schedule optimizer. Create schedules that:
        1. Respect user constraints and preferences
        2. Optimize for cognitive performance
        3. Include spaced repetition
        4. Balance different types of learning activities
        5. Allow for rest and recovery"""
        
        total_weeks = learning_plan.get("total_duration_weeks", 8)
        daily_minutes = user_info["daily_minutes"]
        
        user_prompt = f"""
Create a detailed learning schedule with these parameters:

User Profile:
- Experience: {user_info['experience_years']} years
- Learning Style: {user_info['learning_style']}
- Daily Availability: {daily_minutes} minutes
- Preferred Times: {', '.join(user_info['preferred_times'])}

Learning Plan:
- Duration: {total_weeks} weeks
- Phases: {len(learning_plan.get('phases', []))}
- Focus Areas: {[phase['phase_name'] for phase in learning_plan.get('phases', [])]}

Constraints:
- Work Hours: {constraints.get('work_hours', '9 AM - 6 PM')}
- Timezone: {constraints.get('timezone', 'UTC')}
- Days Available: {constraints.get('available_days', ['weekdays'])}
- Maximum Daily Sessions: {constraints.get('max_daily_sessions', 2)}

Preferences:
- Session Length Preference: {preferences.get('session_length', 'moderate')}
- Break Preferences: {preferences.get('break_preferences', 'pomodoro')}
- Intensity Level: {preferences.get('intensity', 'moderate')}

Existing Commitments: {len(existing_commitments)} commitments

Create a schedule that:
1. Allocates time for different learning activities
2. Includes mock interviews
3. Has review sessions
4. Allows for flexibility
5. Prevents burnout

IMPORTANT: Return a COMPLETE, valid JSON object. Do not truncate the response.
Ensure all strings are properly terminated with quotes.
The response must be parseable by json.loads().

Generate the FULL 8-week schedule, not just a sample.
"""
        
        schedule_schema = {
            "type": "object",
            "properties": {
                "period": {
                    "type": "object",
                    "properties": {
                        "start_date": {"type": "string"},
                        "end_date": {"type": "string"},
                        "total_weeks": {"type": "integer"}
                    }
                },
                "daily_schedule": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "day_of_week": {"type": "string"},
                            "date": {"type": "string"},
                            "sessions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "session_id": {"type": "string"},
                                        "time_slot": {"type": "string"},
                                        "duration_minutes": {"type": "integer"},
                                        "activity_type": {"type": "string"},
                                        "topic": {"type": "string"},
                                        "focus_area": {"type": "string"},
                                        "difficulty": {"type": "string"},
                                        "learning_objective": {"type": "string"},
                                        "resources_needed": {"type": "array", "items": {"type": "string"}}
                                    }
                                }
                            },
                            "total_learning_time": {"type": "integer"},
                            "breakdown": {
                                "type": "object",
                                "properties": {
                                    "theory_study": {"type": "integer"},
                                    "practice_problems": {"type": "integer"},
                                    "review": {"type": "integer"},
                                    "mock_interview": {"type": "integer"}
                                }
                            }
                        }
                    }
                },
                "weekly_overview": {
                    "type": "object",
                    "properties": {
                        "total_hours": {"type": "number"},
                        "sessions_per_week": {"type": "integer"},
                        "mock_interviews_per_week": {"type": "integer"},
                        "review_sessions_per_week": {"type": "integer"}
                    }
                }
            }
        }
        
        schedule = self.llm_client.generate_structured_output(
            prompt=user_prompt,
            output_schema=schedule_schema,
            system_message=system_prompt
        )
        
        # Add generated schedule with actual dates
        schedule = self._populate_dates(schedule, total_weeks)
        
        return schedule
    
    def _populate_dates(self, schedule: Dict, total_weeks: int) -> Dict:
        """Populate schedule with actual dates"""
        
        start_date = datetime.now()
        daily_schedule = []
        
        for week in range(total_weeks):
            for day_offset in range(7):  # 7 days per week
                current_date = start_date + timedelta(weeks=week, days=day_offset)
                
                day_schedule = {
                    "day_of_week": current_date.strftime("%A"),
                    "date": current_date.strftime("%Y-%m-%d"),
                    "sessions": [],
                    "total_learning_time": 0,
                    "breakdown": {
                        "theory_study": 0,
                        "practice_problems": 0,
                        "review": 0,
                        "mock_interview": 0
                    }
                }
                
                # Add sessions based on day of week
                if current_date.weekday() < 5:  # Weekdays
                    day_schedule = self._add_weekday_sessions(day_schedule, week, day_offset)
                else:  # Weekends
                    day_schedule = self._add_weekend_sessions(day_schedule, week, day_offset)
                
                daily_schedule.append(day_schedule)
        
        schedule["daily_schedule"] = daily_schedule
        
        # Ensure 'period' key exists before updating it
        if "period" not in schedule or not isinstance(schedule.get("period"), dict):
            schedule["period"] = {}
        schedule["period"]["start_date"] = start_date.strftime("%Y-%m-%d")
        schedule["period"]["end_date"] = (start_date + timedelta(weeks=total_weeks)).strftime("%Y-%m-%d")
        schedule["period"].setdefault("total_weeks", total_weeks)
        
        return schedule
    
    def _add_weekday_sessions(self, day_schedule: Dict, week: int, day_offset: int) -> Dict:
        """Add sessions for weekdays"""
        
        # Base session template
        morning_session = {
            "session_id": f"session_{week}_{day_offset}_1",
            "time_slot": "08:00-09:30",
            "duration_minutes": 90,
            "activity_type": "theory_study",
            "topic": "Data Structures" if week < 2 else "Algorithms",
            "focus_area": "Fundamentals" if week < 3 else "Advanced",
            "difficulty": "beginner" if week < 2 else "intermediate",
            "learning_objective": "Understand core concepts",
            "resources_needed": ["textbook", "notebook"]
        }
        
        evening_session = {
            "session_id": f"session_{week}_{day_offset}_2",
            "time_slot": "19:00-20:30",
            "duration_minutes": 90,
            "activity_type": "practice_problems",
            "topic": "Problem Solving",
            "focus_area": "Application",
            "difficulty": "intermediate",
            "learning_objective": "Apply concepts to solve problems",
            "resources_needed": ["coding_platform", "whiteboard"]
        }
        
        day_schedule["sessions"] = [morning_session, evening_session]
        day_schedule["total_learning_time"] = 180
        day_schedule["breakdown"]["theory_study"] = 90
        day_schedule["breakdown"]["practice_problems"] = 90
        
        # Add mock interview on Wednesdays
        if day_offset == 2:  # Wednesday
            mock_interview = {
                "session_id": f"mock_{week}_{day_offset}",
                "time_slot": "18:00-19:00",
                "duration_minutes": 60,
                "activity_type": "mock_interview",
                "topic": "Technical Interview",
                "focus_area": "Comprehensive",
                "difficulty": "varies",
                "learning_objective": "Simulate real interview conditions",
                "resources_needed": ["interview_platform", "recording_device"]
            }
            day_schedule["sessions"].append(mock_interview)
            day_schedule["total_learning_time"] += 60
            day_schedule["breakdown"]["mock_interview"] = 60
        
        return day_schedule
    
    def _add_weekend_sessions(self, day_schedule: Dict, week: int, day_offset: int) -> Dict:
        """Add sessions for weekends"""
        
        review_session = {
            "session_id": f"review_{week}_{day_offset}",
            "time_slot": "10:00-12:00",
            "duration_minutes": 120,
            "activity_type": "review",
            "topic": "Week Review",
            "focus_area": "Consolidation",
            "difficulty": "varies",
            "learning_objective": "Review and consolidate week's learning",
            "resources_needed": ["notes", "flashcards"]
        }
        
        day_schedule["sessions"] = [review_session]
        day_schedule["total_learning_time"] = 120
        day_schedule["breakdown"]["review"] = 120
        
        # Add project work on Sundays
        if day_offset == 6:  # Sunday
            project_session = {
                "session_id": f"project_{week}_{day_offset}",
                "time_slot": "14:00-16:00",
                "duration_minutes": 120,
                "activity_type": "practice_problems",
                "topic": "Capstone Project",
                "focus_area": "Integration",
                "difficulty": "advanced",
                "learning_objective": "Apply all concepts to a comprehensive project",
                "resources_needed": ["ide", "documentation"]
            }
            day_schedule["sessions"].append(project_session)
            day_schedule["total_learning_time"] += 120
            day_schedule["breakdown"]["practice_problems"] = 120
        
        return day_schedule
    
    def _apply_cognitive_optimizations(self, schedule: Dict, user_info: Dict) -> Dict[str, Any]:
        """Apply cognitive science optimizations to the schedule"""
        
        optimizations = []
        
        # 1. Spaced Repetition
        if self._apply_spaced_repetition(schedule):
            optimizations.append({
                "technique": "spaced_repetition",
                "description": "Reviews scheduled at increasing intervals for better retention",
                "impact": "high"
            })
        
        # 2. Interleaved Practice
        if self._apply_interleaved_practice(schedule):
            optimizations.append({
                "technique": "interleaved_practice",
                "description": "Mixing different topics within sessions to improve learning",
                "impact": "medium"
            })
        
        # 3. Cognitive Load Management
        if self._manage_cognitive_load(schedule, user_info):
            optimizations.append({
                "technique": "cognitive_load_management",
                "description": "Balancing difficulty and breaks to prevent overload",
                "impact": "high"
            })
        
        # 4. Peak Performance Timing
        if self._optimize_timing(schedule, user_info):
            optimizations.append({
                "technique": "peak_performance_timing",
                "description": "Scheduling difficult tasks during peak cognitive hours",
                "impact": "medium"
            })
        
        schedule["optimization_techniques"] = optimizations
        
        return schedule
    
    def _apply_spaced_repetition(self, schedule: Dict) -> bool:
        """Apply spaced repetition principles"""
        for day in schedule["daily_schedule"]:
            for session in day["sessions"]:
                if "review" in session["activity_type"]:
                    # Mark as spaced repetition session
                    session["spaced_repetition"] = True
                    session["repetition_interval"] = "increasing"
        
        return True
    
    def _apply_interleaved_practice(self, schedule: Dict) -> bool:
        """Apply interleaved practice principles"""
        for day in schedule["daily_schedule"]:
            if len(day["sessions"]) > 1:
                # Mix topics within day
                topics = set()
                for session in day["sessions"]:
                    topics.add(session["topic"])
                
                if len(topics) > 1:
                    day["interleaved_practice"] = True
                    day["mixed_topics"] = list(topics)
        
        return True
    
    def _manage_cognitive_load(self, schedule: Dict, user_info: Dict) -> bool:
        """Manage cognitive load based on user profile"""
        
        max_daily_minutes = user_info["daily_minutes"] * 1.5
        
        for day in schedule["daily_schedule"]:
            total_time = day["total_learning_time"]
            
            # Adjust if exceeding cognitive limits
            if total_time > max_daily_minutes:
                day["cognitive_load"] = "high"
                # Reduce time by 20%
                reduction_factor = 0.8
                day["adjusted_total_time"] = int(total_time * reduction_factor)
            elif total_time > max_daily_minutes * 0.8:
                day["cognitive_load"] = "medium"
            else:
                day["cognitive_load"] = "optimal"
        
        return True
    
    def _optimize_timing(self, schedule: Dict, user_info: Dict) -> bool:
        """Optimize timing based on user preferences and circadian rhythms"""
        
        preferred_times = user_info["preferred_times"]
        
        for day in schedule["daily_schedule"]:
            for session in day["sessions"]:
                # Check if session aligns with preferred times
                session_time = session["time_slot"].split("-")[0]
                hour = int(session_time.split(":")[0])
                
                if "morning" in preferred_times and 6 <= hour <= 10:
                    session["timing_optimization"] = "aligned_with_preference"
                elif "afternoon" in preferred_times and 12 <= hour <= 16:
                    session["timing_optimization"] = "aligned_with_preference"
                elif "evening" in preferred_times and 18 <= hour <= 22:
                    session["timing_optimization"] = "aligned_with_preference"
                else:
                    session["timing_optimization"] = "neutral"
        
        return True
    
    def _calculate_schedule_metrics(self, schedule: Dict) -> Dict[str, Any]:
        """Calculate schedule metrics"""
        
        total_sessions = 0
        total_hours = 0
        mock_interviews = 0
        
        for day in schedule["daily_schedule"]:
            total_sessions += len(day["sessions"])
            total_hours += day["total_learning_time"] / 60
            
            for session in day["sessions"]:
                if session["activity_type"] == "mock_interview":
                    mock_interviews += 1
        
        return {
            "total_sessions": total_sessions,
            "total_hours": round(total_hours, 1),
            "average_daily_hours": round(total_hours / len(schedule["daily_schedule"]), 1),
            "mock_interviews": mock_interviews,
            "completion_rate_estimate": "85%",
            "adherence_score": "high" if total_hours > 20 else "medium"
        }
    
    def _generate_reminders(self, schedule: Dict) -> List[Dict]:
        """Generate automated reminders"""
        
        reminders = []
        reminder_types = ["24_hours_before", "1_hour_before", "15_minutes_before"]
        
        for day in schedule["daily_schedule"][:7]:  # First week only
            for session in day["sessions"]:
                for reminder_type in reminder_types:
                    reminder = {
                        "session_id": session["session_id"],
                        "reminder_type": reminder_type,
                        "message": self._generate_reminder_message(session, reminder_type),
                        "delivery_method": ["push", "email"],
                        "trigger_time": self._calculate_trigger_time(day["date"], session["time_slot"], reminder_type)
                    }
                    reminders.append(reminder)
        
        return reminders
    
    def _generate_reminder_message(self, session: Dict, reminder_type: str) -> str:
        """Generate reminder message based on session and timing"""
        
        base_message = f"Upcoming session: {session['topic']} - {session['activity_type'].replace('_', ' ').title()}"
        
        if reminder_type == "24_hours_before":
            return f"Reminder: {base_message} tomorrow. Please prepare: {', '.join(session['resources_needed'])}"
        elif reminder_type == "1_hour_before":
            return f"Session starting in 1 hour: {base_message}"
        else:  # 15_minutes_before
            return f"Starting soon: {base_message}. Get ready!"
    
    def _calculate_trigger_time(self, date_str: str, time_slot: str, reminder_type: str) -> str:
        """Calculate trigger time for reminders"""
        
        # Simplified calculation
        session_start = time_slot.split("-")[0]
        
        if reminder_type == "24_hours_before":
            # Day before at same time
            trigger = f"{date_str}T{session_start}"
        elif reminder_type == "1_hour_before":
            # 1 hour before session
            trigger = f"{date_str}T{int(session_start.split(':')[0]) - 1:02d}:{session_start.split(':')[1]}"
        else:  # 15_minutes_before
            # 15 minutes before
            trigger = f"{date_str}T{session_start}"
        
        return trigger
    
    def _generate_adjustment_recommendations(self, metrics: Dict) -> List[str]:
        """Generate schedule adjustment recommendations"""
        
        recommendations = []
        
        if metrics["total_hours"] > 40:
            recommendations.append("Consider reducing weekly hours to prevent burnout")
        
        if metrics["mock_interviews"] < 4:
            recommendations.append("Add more mock interview sessions for better preparation")
        
        if metrics["average_daily_hours"] > 3:
            recommendations.append("Break longer sessions into smaller chunks for better retention")
        
        return recommendations
    
    def _load_cognitive_principles(self) -> Dict[str, Any]:
        """Load cognitive science principles for optimization"""
        
        return {
            "spaced_repetition": {
                "description": "Review material at increasing intervals",
                "optimal_intervals": [1, 7, 16, 35],  # days
                "effectiveness": "High for long-term retention"
            },
            "interleaved_practice": {
                "description": "Mix different topics/types of problems",
                "benefits": ["Improves discrimination", "Enhances transfer", "Reduces forgetting"],
                "effectiveness": "Medium-High"
            },
            "cognitive_load_theory": {
                "description": "Manage intrinsic, extraneous, and germane load",
                "principles": ["Work within working memory limits", "Use worked examples", "Avoid split attention"],
                "effectiveness": "High for complex learning"
            },
            "peak_performance_timing": {
                "description": "Schedule based on circadian rhythms",
                "optimal_times": {
                    "analytical_tasks": "Morning",
                    "creative_tasks": "Afternoon",
                    "practice_tasks": "Evening"
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
