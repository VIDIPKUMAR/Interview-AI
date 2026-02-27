from typing import Dict, Any, List, Optional
import ast
import time
import re
from .base_agent import BaseAgent
from utils.llm_client import LLMClient

class CodeAnalyzerAgent(BaseAgent):
    """Advanced code analyzer with multi-language support and company-specific optimization insights"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            agent_id="code_analyzer_001",
            name="Advanced Code Analyzer",
            description="Analyzes code submissions and provides company-specific optimization feedback",
            config=config
        )
        self.llm_client = LLMClient(**config.get("llm_config", {}))
        
        # Company-specific optimization preferences
        self.company_preferences = {
            "Google": {
                "priorities": ["clean_code", "scalability", "edge_cases"],
                "style": "pythonic",
                "feedback_tone": "detailed"
            },
            "Amazon": {
                "priorities": ["efficiency", "scalability", "error_handling"],
                "style": "pragmatic",
                "feedback_tone": "direct"
            },
            "Microsoft": {
                "priorities": ["readability", "maintainability", "documentation"],
                "style": "structured",
                "feedback_tone": "supportive"
            },
            "Meta": {
                "priorities": ["performance", "simplicity", "innovation"],
                "style": "modern",
                "feedback_tone": "encouraging"
            },
            "Goldman Sachs": {
                "priorities": ["correctness", "edge_cases", "robustness"],
                "style": "conservative",
                "feedback_tone": "formal"
            },
            "Flipkart": {
                "priorities": ["efficiency", "scalability", "product_focus"],
                "style": "practical",
                "feedback_tone": "constructive"
            }
        }
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze submitted code with company-specific insights"""
        
        code = input_data.get("code", "")
        problem_id = input_data.get("problem_id")
        language = input_data.get("language", "python")
        target_companies = input_data.get("target_companies", [])
        user_level = input_data.get("user_level", "intermediate")
        
        # Get problem details from database
        from data.problem_database import PROBLEM_DATABASE
        problem = PROBLEM_DATABASE.get(problem_id, {})
        
        # Multi-dimensional analysis
        basic_analysis = self._basic_code_analysis(code, language)
        complexity = self._analyze_complexity(code)
        edge_cases = self._check_edge_cases(code, problem)
        code_quality = self._assess_code_quality(code)
        
        # Company-specific comparison
        company_feedback = {}
        for company in target_companies:
            if company in self.company_preferences:
                company_feedback[company] = self._analyze_for_company(
                    code, problem, company, user_level
                )
        
        # Generate improvements with company context
        improvements = self._generate_company_specific_improvements(
            code, problem, complexity, target_companies
        )
        
        # Performance benchmarks
        benchmarks = self._compare_with_peers(code, problem_id, complexity)
        
        return {
            "status": "success",
            "analysis_id": f"analysis_{self._get_timestamp()}",
            "basic_metrics": basic_analysis,
            "complexity_analysis": complexity,
            "code_quality": code_quality,
            "edge_case_coverage": edge_cases,
            "company_specific_feedback": company_feedback,
            "improvement_suggestions": improvements,
            "performance_benchmarks": benchmarks,
            "next_steps": self._suggest_company_specific_next_steps(
                problem, complexity, target_companies
            ),
            "learning_resources": self._get_learning_resources(problem, target_companies)
        }
    
    def _basic_code_analysis(self, code: str, language: str) -> Dict[str, Any]:
        """Comprehensive static code analysis"""
        
        metrics = {
            "line_count": len(code.split('\n')),
            "character_count": len(code),
            "function_count": code.count('def ') + code.count('function '),
            "class_count": code.count('class '),
            "comment_lines": code.count('#') + code.count('//') + code.count('/*'),
            "has_docstring": '"""' in code or "'''" in code or '/**' in code,
            "empty_lines": code.count('\n\n'),
            "max_line_length": max([len(line) for line in code.split('\n')], default=0)
        }
        
        # Calculate comment ratio
        total_lines = metrics["line_count"]
        if total_lines > 0:
            metrics["comment_ratio"] = round(metrics["comment_lines"] / total_lines * 100, 2)
        else:
            metrics["comment_ratio"] = 0
        
        # Language-specific analysis
        if language == "python":
            try:
                tree = ast.parse(code)
                metrics["ast_parsable"] = True
                metrics["imports"] = [node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)]
                metrics["function_names"] = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                metrics["has_main"] = any(node.name == "main" for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            except SyntaxError as e:
                metrics["ast_parsable"] = False
                metrics["syntax_error"] = str(e)
        
        return metrics
    
    def _check_edge_cases(self, code: str, problem: Dict) -> Dict[str, Any]:
        """Check if code handles common edge cases"""
        
        edge_cases_checked = []
        missing_edge_cases = []
        
        # Common edge cases by problem type
        edge_case_patterns = {
            "two-sum": [
                {"check": "empty array", "pattern": r"if\s+not\s+nums|if\s+len\(nums\)\s*==\s*0"},
                {"check": "single element", "pattern": r"len\(nums\)\s*==\s*1"},
                {"check": "no solution", "pattern": r"return\s+\[\]|raise|None"}
            ],
            "valid-parentheses": [
                {"check": "empty string", "pattern": r"if\s+not\s+s|if\s+s\s*==\s*''"},
                {"check": "single bracket", "pattern": r"len\(s\)\s*==\s*1"},
                {"check": "odd length", "pattern": r"len\(s\)\s*%\s*2\s*!=\s*0"}
            ],
            "number-of-islands": [
                {"check": "empty grid", "pattern": r"if\s+not\s+grid"},
                {"check": "single cell", "pattern": r"len\(grid\)\s*==\s*1\s+and\s+len\(grid\[0\]\)\s*==\s*1"},
                {"check": "all water", "pattern": r"all\(c\s*==\s*'0'\s+for\s+row"}
            ]
        }
        
        problem_id = problem.get("id", "")
        if problem_id in edge_case_patterns:
            for edge in edge_case_patterns[problem_id]:
                if re.search(edge["pattern"], code, re.IGNORECASE):
                    edge_cases_checked.append(edge["check"])
                else:
                    missing_edge_cases.append(edge["check"])
        
        return {
            "edge_cases_handled": edge_cases_checked,
            "edge_cases_missing": missing_edge_cases,
            "coverage_score": round(len(edge_cases_checked) / max(len(edge_cases_checked) + len(missing_edge_cases), 1) * 100, 2)
        }
    
    def _assess_code_quality(self, code: str) -> Dict[str, Any]:
        """Assess code quality metrics"""
        
        quality_metrics = {
            "readability_score": 0,
            "maintainability_score": 0,
            "naming_convention": "unknown",
            "code_smells": []
        }
        
        # Check naming conventions
        if re.search(r'[a-z_]+[a-z0-9_]*', code):
            quality_metrics["naming_convention"] = "snake_case (Pythonic)"
        elif re.search(r'[a-z]+[A-Z][a-z]+', code):
            quality_metrics["naming_convention"] = "camelCase (Java/JS style)"
        
        # Detect code smells
        if len(re.findall(r'if.*if.*if', code)) > 2:
            quality_metrics["code_smells"].append("Deep nesting detected")
        
        if len(re.findall(r'try:', code)) > 0 and len(re.findall(r'except:', code)) == 0:
            quality_metrics["code_smells"].append("Try without except")
        
        if len(re.findall(r'print\(', code)) > 3:
            quality_metrics["code_smells"].append("Debug prints left in code")
        
        # Calculate readability (simple heuristic)
        avg_line_length = sum(len(line) for line in code.split('\n')) / max(len(code.split('\n')), 1)
        if avg_line_length < 50:
            quality_metrics["readability_score"] = 90
        elif avg_line_length < 80:
            quality_metrics["readability_score"] = 70
        else:
            quality_metrics["readability_score"] = 50
        
        # Maintainability score
        if len(quality_metrics["code_smells"]) == 0:
            quality_metrics["maintainability_score"] = 90
        elif len(quality_metrics["code_smells"]) < 3:
            quality_metrics["maintainability_score"] = 70
        else:
            quality_metrics["maintainability_score"] = 50
        
        return quality_metrics
    
    def _analyze_complexity(self, code: str) -> Dict[str, str]:
        """Enhanced complexity analysis with detailed explanations"""
        
        # Use LLM for detailed complexity analysis
        prompt = f"""Analyze this code and provide a detailed complexity analysis:

```python
{code}