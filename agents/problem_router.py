from typing import Dict, Any, List, Optional
import random
from data.problem_database import PROBLEM_DATABASE, TOPIC_INDEX, COMPANY_INDEX, COMPANY_METADATA

class ProblemRouter:
    """Routes users to appropriate problems based on their profile with multi-company intelligence"""
    
    def __init__(self):
        self.problem_db = PROBLEM_DATABASE
        self.company_index = COMPANY_INDEX
        self.topic_index = TOPIC_INDEX
        self.company_metadata = COMPANY_METADATA
        
    def get_recommendation(self, user_profile: Dict, weak_areas: List[str], 
                          target_companies: List[str], difficulty_pref: str = "adaptive") -> Dict[str, Any]:
        """
        Get personalized problem recommendation using multi-company intelligence
        """
        
        candidate_problems = []
        company_context = {}
        
        # Analyze target companies for patterns
        company_patterns = self._analyze_company_patterns(target_companies)
        
        # Prioritize problems from target companies with frequency weighting
        for company in target_companies:
            if company in self.company_index:
                company_info = self.company_metadata.get(company, {})
                company_context[company] = {
                    "focus_areas": company_info.get("focus_areas", []),
                    "difficulty_bias": company_info.get("difficulty_bias", "Medium"),
                    "culture": company_info.get("culture", [])
                }
                
                for problem_id in self.company_index[company]:
                    problem = self.problem_db.get(problem_id)
                    if problem and problem_id not in [p['id'] for p in candidate_problems]:
                        # Add company-specific context
                        problem_copy = problem.copy()
                        
                        # Get frequency for this specific company
                        freq_data = problem['companies'].get(company, {})
                        frequency = freq_data.get('frequency', 1)
                        last_asked = freq_data.get('last_asked', '2024')
                        roles = freq_data.get('role', ['SDE'])
                        
                        problem_copy['company_context'] = {
                            "company": company,
                            "frequency": f"Asked {frequency} times in {last_asked}",
                            "roles": roles,
                            "importance": self._calculate_importance(frequency, last_asked)
                        }
                        
                        # Add to candidates with weight based on frequency
                        candidate_problems.append({
                            "problem": problem_copy,
                            "weight": frequency,
                            "company": company
                        })
        
        # Sort by weight (frequency) and remove duplicates
        candidate_problems.sort(key=lambda x: x['weight'], reverse=True)
        
        # Add problems from weak areas if not enough company-specific problems
        if len(candidate_problems) < 5:
            for topic in weak_areas:
                if topic in self.topic_index:
                    for problem_id in self.topic_index[topic]:
                        problem = self.problem_db.get(problem_id)
                        if problem and problem_id not in [p['problem']['id'] for p in candidate_problems]:
                            candidate_problems.append({
                                "problem": problem,
                                "weight": 1,
                                "company": "general"
                            })
        
        # Select optimal problem based on user level and difficulty preference
        selected = self._select_optimal_problem(
            [p['problem'] for p in candidate_problems], 
            user_profile,
            difficulty_pref,
            company_patterns
        )
        
        # Generate learning path
        learning_path = self._generate_learning_path(selected, weak_areas, target_companies)
        
        return {
            "recommendation": {
                "type": "practice",
                "source": selected.get("platform", "leetcode"),
                "problem": {
                    "id": selected["id"],
                    "title": selected["title"],
                    "url": selected["url"],
                    "difficulty": selected["difficulty"],
                    "topics": selected["topics"],
                    "company_context": selected.get("company_context", {}),
                    "company_patterns": company_patterns,
                    "expected_complexity": selected["solution_approaches"][-1]["complexity"] if selected.get("solution_approaches") else "O(n)",
                    "estimated_time": self._estimate_time(selected["difficulty"])
                },
                "instruction": f"Solve this problem on {selected.get('platform', 'LeetCode').title()}, then paste your solution for AI-powered analysis:",
                "expected_time": self._estimate_time(selected["difficulty"]),
                "hints_available": True,
                "learning_path": learning_path
            },
            "alternative_problems": [
                {
                    "title": p["title"],
                    "difficulty": p["difficulty"],
                    "url": p["url"],
                    "company": p.get("company_context", {}).get("company", "general")
                } for p in [c['problem'] for c in candidate_problems[:3] if c['problem']['id'] != selected['id']]
            ],
            "company_insights": company_context,
            "next_milestone": self._get_next_milestone(user_profile, selected)
        }
    
    def _analyze_company_patterns(self, companies: List[str]) -> Dict[str, Any]:
        """Analyze patterns across multiple target companies"""
        
        patterns = {
            "common_topics": [],
            "difficulty_trend": [],
            "recommended_focus": [],
            "company_specific_notes": {}
        }
        
        topic_frequency = {}
        
        for company in companies:
            if company in self.company_index:
                metadata = self.company_metadata.get(company, {})
                patterns["company_specific_notes"][company] = {
                    "focus_areas": metadata.get("focus_areas", []),
                    "culture": metadata.get("culture", []),
                    "process": metadata.get("interview_process", [])
                }
                
                # Count topic frequency across companies
                for problem_id in self.company_index[company]:
                    problem = self.problem_db.get(problem_id)
                    if problem:
                        for topic in problem.get("topics", []):
                            topic_frequency[topic] = topic_frequency.get(topic, 0) + 1
        
        # Find common topics across target companies
        patterns["common_topics"] = sorted(
            topic_frequency.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return patterns
    
    def _calculate_importance(self, frequency: int, last_asked: str) -> str:
        """Calculate problem importance based on frequency and recency"""
        if frequency > 10 and last_asked == "2024":
            return "Critical"
        elif frequency > 5 and last_asked >= "2023":
            return "High"
        elif frequency > 2:
            return "Medium"
        else:
            return "Low"
    
    def _select_optimal_problem(self, problems: List[Dict], user_profile: Dict, 
                               difficulty_pref: str, company_patterns: Dict) -> Dict:
        """Select the best problem using ML-inspired heuristics"""
        
        if not problems:
            return self._get_fallback_problem()
        
        # Score each problem
        scored_problems = []
        for problem in problems:
            score = 0
            
            # Base score from company importance
            company_context = problem.get("company_context", {})
            if isinstance(company_context, dict):
                importance = company_context.get("importance", "Medium")
                score += {"Critical": 30, "High": 20, "Medium": 10, "Low": 5}.get(importance, 10)
            
            # Topic alignment with common patterns
            for topic, freq in company_patterns.get("common_topics", []):
                if topic in problem.get("topics", []):
                    score += freq * 2
            
            # Difficulty adjustment based on user level
            user_level = user_profile.get("current_level", "intermediate")
            difficulty_order = {"Easy": 1, "Medium": 2, "Hard": 3}
            prob_diff = difficulty_order.get(problem["difficulty"], 2)
            
            if user_level == "beginner" and prob_diff == 1:
                score += 15
            elif user_level == "intermediate" and prob_diff == 2:
                score += 15
            elif user_level == "advanced" and prob_diff == 3:
                score += 15
            
            # Preference adjustment
            if difficulty_pref == "easy" and prob_diff == 1:
                score += 10
            elif difficulty_pref == "hard" and prob_diff == 3:
                score += 10
            
            scored_problems.append((problem, score))
        
        # Return highest scored problem
        scored_problems.sort(key=lambda x: x[1], reverse=True)
        return scored_problems[0][0]
    
    def _generate_learning_path(self, current_problem: Dict, weak_areas: List[str], 
                               target_companies: List[str]) -> List[Dict]:
        """Generate a learning path based on current problem"""
        
        path = []
        current_topic = current_problem.get("topics", [""])[0]
        
        # Prerequisite topics
        prerequisites = {
            "dynamic-programming": ["recursion", "memoization"],
            "graphs": ["trees", "bfs/dfs"],
            "hash-table": ["arrays"],
            "stack": ["arrays"],
            "linked-list": ["arrays"]
        }
        
        # Add prerequisite path
        for prereq in prerequisites.get(current_topic, []):
            path.append({
                "type": "prerequisite",
                "topic": prereq,
                "estimated_time": "2 hours",
                "reason": f"Master {prereq} before diving into {current_topic}"
            })
        
        # Current problem
        path.append({
            "type": "current",
            "topic": current_problem["title"],
            "difficulty": current_problem["difficulty"],
            "estimated_time": self._estimate_time(current_problem["difficulty"]),
            "reason": "Primary focus for today"
        })
        
        # Next steps
        next_steps_map = {
            "two-sum": "3sum",
            "valid-parentheses": "generate-parentheses",
            "number-of-islands": "max-area-of-island",
            "climbing-stairs": "min-cost-climbing-stairs"
        }
        
        next_problem = next_steps_map.get(current_problem.get("id", ""))
        if next_problem:
            path.append({
                "type": "next",
                "topic": next_problem,
                "difficulty": "Medium",
                "estimated_time": "45 minutes",
                "reason": "Natural progression after mastering current concept"
            })
        
        return path
    
    def _get_next_milestone(self, user_profile: Dict, current_problem: Dict) -> Dict:
        """Get next achievement milestone"""
        
        milestones = {
            "Easy": {"next": "Medium", "problems_needed": 5},
            "Medium": {"next": "Hard", "problems_needed": 10},
            "Hard": {"next": "Interview Ready", "problems_needed": 3}
        }
        
        current_diff = current_problem.get("difficulty", "Easy")
        milestone = milestones.get(current_diff, milestones["Easy"])
        
        return {
            "next_level": milestone["next"],
            "problems_remaining": milestone["problems_needed"],
            "estimated_days": milestone["problems_needed"] // 2 + 1
        }
    
    def _estimate_time(self, difficulty: str) -> int:
        """Estimate solving time in minutes"""
        times = {
            "Easy": 20,
            "Medium": 35,
            "Hard": 50
        }
        return times.get(difficulty, 30)
    
    def _get_fallback_problem(self) -> Dict:
        """Return a default problem if no matches found"""
        return self.problem_db.get("two-sum", {})