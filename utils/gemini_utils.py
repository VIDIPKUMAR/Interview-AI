import google.generativeai as genai
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

class GeminiUtils:
    """Utility functions for Gemini API"""
    
    @staticmethod
    def format_prompt_for_gemini(system_prompt: str, user_prompt: str) -> str:
        """Format prompt for Gemini (combines system and user prompts)"""
        return f"""{system_prompt}

{user_prompt}"""
    
    @staticmethod
    def get_available_models() -> List[Dict[str, str]]:
        """Get available Gemini models"""
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append({
                    'name': m.name,
                    'display_name': m.display_name,
                    'description': m.description,
                    'input_token_limit': m.input_token_limit,
                    'output_token_limit': m.output_token_limit
                })
        return models
    
    @staticmethod
    def create_generation_config(**kwargs) -> Dict[str, Any]:
        """Create generation config for Gemini"""
        default_config = {
            'temperature': 0.7,
            'top_p': 0.8,
            'top_k': 40,
            'max_output_tokens': 2000,
            'stop_sequences': None,
        }
        default_config.update(kwargs)
        return default_config
    
    @staticmethod
    def create_safety_settings(threshold: str = "BLOCK_MEDIUM_AND_ABOVE") -> List[Dict[str, str]]:
        """Create safety settings for Gemini"""
        return [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": threshold
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": threshold
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": threshold
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": threshold
            }
        ]
    
    @staticmethod
    def validate_response(response: genai.types.GenerateContentResponse) -> bool:
        """Validate Gemini response"""
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            logger.warning(f"Response blocked: {response.prompt_feedback.block_reason}")
            return False
        
        if not response.text:
            logger.warning("Empty response from Gemini")
            return False
        
        return True
    
    @staticmethod
    def extract_json_from_response(response_text: str) -> Dict[str, Any]:
        """Extract JSON from Gemini response text"""
        try:
            # Remove markdown code blocks
            text = response_text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON-like structure
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            raise ValueError("Could not extract valid JSON from response")