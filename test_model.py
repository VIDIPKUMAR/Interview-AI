import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key loaded: {bool(api_key)}")

try:
    import google.generativeai as genai
    print("✓ google.generativeai imported successfully")
    
    genai.configure(api_key=api_key)
    
    # Test with the actual model name
    model = genai.GenerativeModel('models/gemini-2.0-flash')
    response = model.generate_content("Say 'Hello World' in one word")
    print(f"✓ Gemini response: {response.text}")
    print("✓ Model working correctly!")
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {str(e)}")
