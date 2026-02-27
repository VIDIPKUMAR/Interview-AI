import requests
import json

url = "http://localhost:5001/api/agents"
data = {
    "agent": "evaluator",
    "action": "evaluate",
    "data": {
        "question": "What is a hash table?",
        "question_type": "technical",
        "user_response": "A hash table maps keys to values using a hash function with O(1) average complexity for insert and lookup.",
        "expected_areas": ["hash function", "O(1) complexity", "key-value pairs"]
    }
}

response = requests.post(url, json=data)
result = response.json()

print("Status:", result.get("status"))
print("Overall Score:", result.get("scores", {}).get("overall"))
print("Feedback:", result.get("feedback", {}).get("summary", "")[:300])
