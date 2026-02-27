from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from .base_agent import BaseAgent
from utils.llm_client import LLMClient

class CompanyAnalyzerAgent(BaseAgent):
    """Analyzes target companies and extracts interview patterns"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            agent_id="company_analyzer_001",
            name="Company DNA Analyzer",
            description="Analyzes company patterns and requirements",
            config=config
        )
        self.llm_client = LLMClient(**config.get("llm_config", {}))
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze target companies"""
        self.log(f"Analyzing companies: {input_data.get('target_companies')}")
        
        target_companies = input_data.get("target_companies", [])
        target_role = input_data.get("target_role", "SDE")
        
        try:
            company_insights = {}
            for company in target_companies:
                insights = self._analyze_company(company, target_role)
                company_insights[company] = insights
            
            # Generate consolidated insights
            consolidated = self._consolidate_insights(company_insights)
            
            response = {
                "status": "success",
                "analysis_id": f"ca_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "company_insights": company_insights,
                "consolidated_requirements": consolidated,
                "priority_topics": self._extract_priority_topics(consolidated),
                "company_specific_tips": self._generate_company_tips(company_insights)
            }
            
            self.update_memory({
                "action": "analyzed_companies",
                "companies": target_companies,
                "role": target_role
            })
            
            return response
            
        except Exception as e:
            self.log(f"Error in company analysis: {str(e)}", "ERROR")
            return self._create_error_response(str(e))
    
    def _analyze_company(self, company: str, role: str) -> Dict[str, Any]:
        """Analyze specific company patterns"""
        
        system_prompt = """You are an expert at analyzing company interview patterns.
        Provide detailed insights about interview processes, question patterns, and success factors."""
        
        prompt = f"""
        Analyze interview patterns for {company} for role {role}:
        
        Provide:
        1. Most frequently asked topics with weights
        2. Difficulty distribution (Easy:Medium:Hard)
        3. Interview rounds structure
        4. Preferred programming languages
        5. Success traits and red flags
        6. Recent trends and changes
        7. Common question types
        8. Preparation resources specific to {company}
        """
        
        schema = {
            "type": "object",
            "properties": {
                "core_topics": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "topic_weights": {
                    "type": "object",
                    "additionalProperties": {"type": "number"}
                },
                "difficulty_curve": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 3,
                    "maxItems": 3
                },
                "interview_rounds": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "preferred_languages": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "success_traits": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "recent_trends": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "common_question_categories": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "company_culture_indicators": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "red_flags": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
        
        return self.llm_client.generate_structured_output(
            prompt=prompt,
            output_schema=schema,
            system_message=system_prompt
        )
    
    def _consolidate_insights(self, company_insights: Dict) -> Dict[str, Any]:
        """Consolidate insights across multiple companies"""
        
        all_topics = []
        topic_weights_sum = {}
        
        for company, insights in company_insights.items():
            topics = insights.get("core_topics", [])
            all_topics.extend(topics)
            
            weights = insights.get("topic_weights", {})
            for topic, weight in weights.items():
                if topic not in topic_weights_sum:
                    topic_weights_sum[topic] = []
                topic_weights_sum[topic].append(weight)
        
        # Calculate average weights
        avg_weights = {}
        for topic, weights in topic_weights_sum.items():
            avg_weights[topic] = sum(weights) / len(weights)
        
        # Sort by weight
        sorted_topics = sorted(avg_weights.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "common_topics": list(set(all_topics)),
            "priority_topics": [t[0] for t in sorted_topics[:10]],
            "topic_importance": avg_weights,
            "unique_requirements": self._find_unique_requirements(company_insights)
        }
    
    def _find_unique_requirements(self, company_insights: Dict) -> Dict[str, List[str]]:
        """Find unique requirements per company"""
        
        unique = {}
        all_topics = []
        
        # Collect all topics
        for company, insights in company_insights.items():
            all_topics.extend(insights.get("core_topics", []))
        
        # Find topics unique to each company
        for company, insights in company_insights.items():
            company_topics = insights.get("core_topics", [])
            unique[company] = [
                topic for topic in company_topics 
                if all_topics.count(topic) == 1
            ]
        
        return unique
    
    def _extract_priority_topics(self, consolidated: Dict) -> List[Dict]:
        """Extract priority topics with context"""
        
        priority_topics = []
        for topic in consolidated.get("priority_topics", [])[:8]:
            priority_topics.append({
                "topic": topic,
                "importance": consolidated.get("topic_importance", {}).get(topic, 0.5),
                "focus_level": "critical" if consolidated.get("topic_importance", {}).get(topic, 0) > 0.7 else "important",
                "estimated_hours": self._estimate_topic_hours(topic)
            })
        
        return priority_topics
    
    def _estimate_topic_hours(self, topic: str) -> int:
        """Estimate hours needed for topic mastery"""
        
        topic_hours = {
            "dynamic programming": 20,
            "graphs": 15,
            "trees": 12,
            "arrays": 8,
            "strings": 8,
            "system design": 25,
            "object oriented design": 15,
            "recursion": 10,
            "sorting": 6,
            "searching": 6
        }
        
        for key, hours in topic_hours.items():
            if key in topic.lower():
                return hours
        
        return 12  # Default
    
    def _generate_company_tips(self, company_insights: Dict) -> Dict[str, List[str]]:
        """Generate company-specific preparation tips"""
        
        tips = {}
        for company, insights in company_insights.items():
            company_tips = []
            
            # Tips based on success traits
            for trait in insights.get("success_traits", [])[:2]:
                company_tips.append(f"Focus on demonstrating {trait.lower()} in your answers")
            
            # Tips based on recent trends
            for trend in insights.get("recent_trends", [])[:2]:
                company_tips.append(f"Prepare for: {trend}")
            
            # Tips based on preferred languages
            langs = insights.get("preferred_languages", [])
            if langs:
                company_tips.append(f"Practice in {langs[0]} as it's commonly used at {company}")
            
            # Tips based on difficulty curve
            diff_curve = insights.get("difficulty_curve", [0.3, 0.4, 0.3])
            if diff_curve[2] > 0.4:  # More hard problems
                company_tips.append(f"{company} asks many hard problems - practice advanced topics")
            
            tips[company] = company_tips
        
        return tips
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "status": "error",
            "error": error_message,
            "timestamp": self._get_timestamp()
        }