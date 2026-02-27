import os
os.environ["USE_MOCK_LLM"] = "true"

# Test that mock mode works
try:
    from utils.llm_client import LLMClient
    
    client = LLMClient(provider="google", model="mock-model")
    
    # Test completion
    response = client.generate_completion("Test prompt")
    print(f"Mock completion test: {response[:100]}...")
    
    # Test structured output
    structured = client.generate_structured_output(
        "Test structured",
        {"type": "object", "properties": {"test": {"type": "string"}}}
    )
    print(f"Mock structured test: {structured}")
    
    print("✓ Mock mode working correctly!")
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {str(e)}")
