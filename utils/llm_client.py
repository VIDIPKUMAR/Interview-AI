import warnings
warnings.filterwarnings("ignore", message=".*google.generativeai.*")

from typing import Dict, Any, List, Optional
import json
import os
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging
import time
import random

logger = logging.getLogger(__name__)

# Try to import real Gemini, fall back to mock
USE_MOCK = os.getenv("USE_MOCK_LLM", "false").lower() == "true"

if not USE_MOCK:
    try:
        import google.generativeai as genai
        HAS_GENAI = True
        logger.info("Using real Gemini API")
    except ImportError:
        HAS_GENAI = False
        logger.warning("google.generativeai not available, using mock mode")
    except Exception as e:
        HAS_GENAI = False
        logger.warning(f"Gemini API error, using mock mode: {str(e)}")
else:
    HAS_GENAI = False
    logger.info("Using mock LLM mode")

# Custom exception for rate limiting
class RateLimitError(Exception):
    """Raised when API rate limit is hit"""
    pass

if HAS_GENAI:
    class GeminiClient:
        """Real Gemini LLM client implementation"""
        
        def __init__(self, api_key: str = None, model: str = "models/gemini-2.5-flash", **kwargs):
            self.model_name = model
            self.config = kwargs
            
            # Configure Gemini
            if api_key:
                genai.configure(api_key=api_key)
            elif os.getenv("GOOGLE_API_KEY"):
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            else:
                raise ValueError("Google API key not provided. Set GOOGLE_API_KEY environment variable.")
            
            # Initialize the model
            try:
                self.model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config=self.config.get("generation_config"),
                    safety_settings=self.config.get("safety_settings")
                )
                logger.info(f"Initialized Gemini model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {str(e)}")
                raise
        
        @retry(
            stop=stop_after_attempt(5),  # Try 5 times
            wait=wait_exponential(multiplier=2, min=4, max=30),  # Exponential backoff
            retry=retry_if_exception_type((Exception, RateLimitError)),  # Retry on any exception
            before_sleep=lambda retry_state: logger.info(f"Retrying API call, attempt {retry_state.attempt_number}, waiting {retry_state.next_action.sleep} seconds")
        )
        def generate_completion(self, 
                               prompt: str, 
                               system_message: Optional[str] = None,
                               temperature: float = 0.7,
                               max_tokens: int = 8192,
                               **kwargs) -> str:
            """Generate completion from Gemini with rate limiting"""
            
            try:
                # Add jitter to avoid thundering herd
                time.sleep(random.uniform(0.5, 1.5))
                
                # Combine system message and prompt for Gemini
                full_prompt = ""
                if system_message:
                    full_prompt = f"{system_message}\n\n"
                full_prompt += prompt
                
                # Update generation config
                generation_config = {
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                    **kwargs
                }
                
                # Generate content
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
                
                # Check for blocked content
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    logger.warning(f"Content blocked: {response.prompt_feedback.block_reason}")
                    raise ValueError(f"Content blocked: {response.prompt_feedback.block_reason}")
                
                return response.text.strip()
                
            except Exception as e:
                error_str = str(e).lower()
                if "quota" in error_str or "rate limit" in error_str or "resource exhausted" in error_str:
                    logger.warning(f"Rate limit hit: {str(e)}")
                    raise RateLimitError(f"Rate limit exceeded: {str(e)}")
                logger.error(f"Gemini generation failed: {str(e)}")
                raise
        
        def generate_structured_output(self, 
                                      prompt: str, 
                                      output_schema: Dict[str, Any],
                                      system_message: Optional[str] = None,
                                      **kwargs) -> Dict[str, Any]:
            """Generate structured JSON output"""
            
            schema_str = json.dumps(output_schema, indent=2)
            structured_prompt = f"""{prompt}

IMPORTANT: You must respond with a valid JSON object ONLY. No additional text, no explanations, no markdown formatting.

Required JSON Schema:
{schema_str}

Your response must be valid JSON that strictly follows this schema. Return ONLY the JSON object."""

            # DEBUG: Print the prompt being sent
            print("\n" + "="*50)
            print("🔍 SENDING PROMPT TO GEMINI:")
            print("="*50)
            print(structured_prompt[:500] + "...")
            print("="*50)

            response = self.generate_completion(
                prompt=structured_prompt,
                system_message=system_message,
                **kwargs
            )
            
            # DEBUG: Print raw response
            print("\n" + "="*50)
            print("🔍 RAW RESPONSE FROM GEMINI:")
            print("="*50)
            print(repr(response))  # Using repr() to see hidden characters
            print("\nLENGTH:", len(response))
            print("FIRST 100 CHARS:", repr(response[:100]))
            print("LAST 100 CHARS:", repr(response[-100:]))
            print("="*50)
            
            # Clean and parse JSON
            try:
                # Remove any markdown formatting
                original_response = response
                response = response.strip()
                
                # Check if it's wrapped in markdown code blocks
                if response.startswith("```json"):
                    response = response[7:]
                    if response.endswith("```"):
                        response = response[:-3]
                elif response.startswith("```"):
                    response = response[3:]
                    if response.endswith("```"):
                        response = response[:-3]
                
                response = response.strip()
                
                # DEBUG: Show cleaned response
                print("\n🔍 CLEANED RESPONSE:")
                print(repr(response[:200]) + "...")
                
                # Parse JSON
                parsed = json.loads(response)
                
                # Validate against schema (basic validation)
                self._validate_json_structure(parsed, output_schema)
                
                print("✅ JSON PARSED SUCCESSFULLY!")
                return parsed
                
            except json.JSONDecodeError as e:
                print("\n❌ JSON DECODE ERROR:")
                print(f"Error: {str(e)}")
                print(f"Position: line {e.lineno}, column {e.colno}")
                print(f"Char: {e.pos}")
                
                # Try to find where it failed
                lines = response.split('\n')
                error_line = lines[e.lineno - 1] if e.lineno <= len(lines) else "N/A"
                print(f"Error line: {error_line}")
                
                logger.error(f"Failed to parse JSON from response: {response[:500]}...")
                logger.error(f"JSON decode error: {str(e)}")
                raise ValueError(f"Invalid JSON response from model: {str(e)}")
            except Exception as e:
                logger.error(f"Error processing structured output: {str(e)}")
                raise
        
        def _validate_json_structure(self, data: Any, schema: Dict[str, Any]) -> bool:
            """Basic JSON structure validation"""
            schema_type = schema.get("type", "object")
            
            if schema_type == "array":
                if not isinstance(data, list):
                    raise ValueError("Expected JSON array")
                return True
            
            if not isinstance(data, dict):
                raise ValueError("Expected JSON object")
            
            # Check required properties
            if "properties" in schema:
                required_props = schema.get("required", [])
                for prop in required_props:
                    if prop not in data:
                        raise ValueError(f"Missing required property: {prop}")
            
            return True
        
        def stream_completion(self, prompt: str, **kwargs):
            """Stream completion for real-time responses"""
            try:
                response = self.model.generate_content(
                    prompt,
                    stream=True,
                    generation_config=kwargs.get("generation_config", {})
                )
                
                for chunk in response:
                    yield chunk.text
                    
            except Exception as e:
                logger.error(f"Streaming failed: {str(e)}")
                raise
        
        def count_tokens(self, text: str) -> int:
            """Count tokens in text"""
            try:
                result = genai.count_tokens(self.model_name, text)
                return result.total_tokens
            except:
                # Fallback estimation
                return len(text.split()) * 1.3
else:
    # Import and use mock client
    try:
        from .mock_llm_client import MockGeminiClient
    except ImportError:
        # Create inline mock client if file doesn't exist
        class MockGeminiClient:
            def __init__(self, model="mock", **kwargs):
                self.model_name = model
            
            def generate_completion(self, prompt, **kwargs):
                return '{"status": "mock", "message": "Mock response"}'
            
            def generate_structured_output(self, prompt, output_schema, **kwargs):
                return {"mock": "data", "status": "success"}
            
            def stream_completion(self, prompt, **kwargs):
                yield "Mock streaming response"
            
            def count_tokens(self, text):
                return len(text.split())
    
    class GeminiClient(MockGeminiClient):
        """Mock client when real API is not available"""
        pass

class LLMClient:
    """Unified LLM client wrapper"""
    
    def __init__(self, provider: str = "google", model: str = "models/gemini-2.5-flash", **kwargs):
        self.provider = provider
        
        if provider == "google" or provider == "mock":
            self.client = GeminiClient(model=model, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate_completion(self, *args, **kwargs):
        """Forward to appropriate client"""
        return self.client.generate_completion(*args, **kwargs)
    
    def generate_structured_output(self, *args, **kwargs):
        """Forward to appropriate client"""
        return self.client.generate_structured_output(*args, **kwargs)
    
    def stream_completion(self, *args, **kwargs):
        """Forward to appropriate client"""
        return self.client.stream_completion(*args, **kwargs)