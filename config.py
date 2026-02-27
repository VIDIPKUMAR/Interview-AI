import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum

@dataclass
class AgentConfig:
    """Configuration for agents"""
    model_provider: str = "google"
    model_name: str = "models/gemini-2.0-flash-lite"  # Using lite version
    temperature: float = 0.7
    max_tokens: int = 2000

@dataclass
class GeminiConfig:
    """Gemini-specific configuration"""
    api_key: str = ""
    safety_settings: Dict = None
    generation_config: Dict = None

class InterviewType(Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"
    LEADERSHIP = "leadership"
    CASE_STUDY = "case_study"

class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

# Initialize Gemini configuration
def get_gemini_config() -> GeminiConfig:
    return GeminiConfig(
        api_key=os.getenv("GOOGLE_API_KEY", ""),
        safety_settings=[
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ],
        generation_config={
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2000,
        }
    )

if __name__ == "__main__":
    print("Gemini configuration loaded successfully")
