import os
from dotenv import load_dotenv
load_dotenv()

# Force mock mode to test
os.environ["USE_MOCK_LLM"] = "false"

from utils.llm_client import LLMClient

# Test the structured output
client = LLMClient(provider="google", model="models/gemini-2.5-flash")

schema = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "strengths_highlighted": {"type": "array", "items": {"type": "string"}},
        "improvement_areas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "area": {"type": "string"},
                    "issue": {"type": "string"},
                    "suggestion": {"type": "string"},
                    "practice_exercise": {"type": "string"}
                }
            }
        }
    },
    "required": ["summary", "strengths_highlighted", "improvement_areas"]
}

prompt = """Based on this evaluation:
{
  "technical_accuracy": {
    "score": 8.5,
    "feedback": "Good understanding of concepts",
    "strengths": ["Correct hashmap explanation", "Accurate time complexity"],
    "weaknesses": ["Could provide more details on collision resolution"]
  }
}

Generate actionable feedback that starts with a brief summary."""

try:
    result = client.generate_structured_output(
        prompt=prompt,
        output_schema=schema,
        system_message="You are a supportive and constructive interview coach."
    )
    print("Result keys:", result.keys())
    print("Has summary?", 'summary' in result)
    print("Full result:", json.dumps(result, indent=2))
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)}")
