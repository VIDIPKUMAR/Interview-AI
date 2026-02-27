import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key loaded: {bool(api_key)}")

try:
    import google.generativeai as genai
    print("✓ google.generativeai imported successfully")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say 'Hello World'")
    print(f"✓ Gemini response: {response.text}")
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {str(e)}")
