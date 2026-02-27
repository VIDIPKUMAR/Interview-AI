"""
Quick start script for Gemini-based framework
"""

import subprocess
import sys
import os

def run_command(command, description):
    print(f"\n{description}...")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✓ {description} completed")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"✗ {description} failed")
        print(f"Error: {result.stderr}")
        return False
    return True

def main():
    print("="*60)
    print("QUICK START: Gemini Interview AI Framework")
    print("="*60)
    
    # Check if we're in a virtual environment
    in_venv = sys.prefix != sys.base_prefix
    if not in_venv:
        print("\n⚠️  Not running in a virtual environment.")
        print("Consider creating one:")
        print("  python -m venv venv")
        print("  source venv/bin/activate  # On Linux/Mac")
        print("  venv\\Scripts\\activate    # On Windows")
        print("\nContinue anyway? (y/n): ", end="")
        if input().lower() != 'y':
            return
    
    # Step 1: Install dependencies
    success = run_command(
        "pip install -r requirements.txt",
        "Installing dependencies"
    )
    
    if not success:
        print("\nFailed to install dependencies. Please check your internet connection.")
        return
    
    # Step 2: Set up environment
    if not os.path.exists(".env"):
        print("\nCreating .env file...")
        with open(".env", "w") as f:
            f.write("""# Google Gemini API Key
GOOGLE_API_KEY=your-gemini-api-key-here

# Optional configurations
LOG_LEVEL=INFO
MODEL_NAME=gemini-pro
MAX_TOKENS=2000
""")
        print("✓ Created .env file")
    
    # Step 3: Create necessary directories
    directories = ["agents", "models", "utils", "logs", "data", "exports"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Create __init__.py files
    for init_file in ["agents/__init__.py", "models/__init__.py", "utils/__init__.py"]:
        with open(init_file, "w") as f:
            f.write("")
    
    print("\n✓ Project structure created")
    
    # Step 4: Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your-gemini-api-key-here":
        print("\n" + "="*60)
        print("IMPORTANT: You need a Google Gemini API key!")
        print("="*60)
        print("\n1. Go to: https://makersuite.google.com/app/apikey")
        print("2. Create an API key")
        print("3. Edit the .env file and replace 'your-gemini-api-key-here' with your key")
        print("\nOnce you have your API key, run: python main_gemini.py")
    else:
        print("\n✓ API key found in environment")
        print("\nTo run the demo: python main_gemini.py")
    
    print("\n" + "="*60)
    print("Quick start completed!")
    print("="*60)

if __name__ == "__main__":
    main()