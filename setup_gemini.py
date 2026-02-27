#!/usr/bin/env python3
"""
Setup script for Gemini-based Interview AI Framework
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 9):
        print("Error: Python 3.9 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def install_dependencies():
    """Install required dependencies"""
    print("\nInstalling dependencies...")
    
    requirements_file = "requirements.txt"
    if not Path(requirements_file).exists():
        print(f"Error: {requirements_file} not found")
        sys.exit(1)
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        sys.exit(1)

def setup_environment():
    """Set up environment variables"""
    print("\nSetting up environment...")
    
    env_file = ".env"
    env_example = """
# Google Gemini API Key
GOOGLE_API_KEY=your-gemini-api-key-here

# Optional: Other configurations
LOG_LEVEL=INFO
MODEL_NAME=gemini-pro
MAX_TOKENS=2000
"""
    
    if not Path(env_file).exists():
        print(f"Creating {env_file} file...")
        with open(env_file, "w") as f:
            f.write(env_example)
        print(f"✓ Created {env_file}")
        print(f"Please edit {env_file} and add your Google API key")
    else:
        print(f"✓ {env_file} already exists")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your-gemini-api-key-here":
        print("\n⚠️  WARNING: GOOGLE_API_KEY not set or is default value")
        print("Please set your Google API key in the .env file")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
    else:
        print("✓ GOOGLE_API_KEY is set")

def verify_gemini_installation():
    """Verify Gemini installation"""
    print("\nVerifying Gemini installation...")
    
    try:
        import google.generativeai as genai
        print("✓ google-generativeai package installed")
        
        # Try to configure with a dummy key for verification
        try:
            genai.configure(api_key="dummy_key")
            models = list(genai.list_models())
            print(f"✓ Gemini API accessible")
            print(f"✓ Found {len(models)} available models")
        except Exception as e:
            print(f"⚠️  Note: {e}")
            print("This is expected until you set a valid API key")
            
    except ImportError as e:
        print(f"✗ Failed to import google-generativeai: {e}")
        sys.exit(1)

def create_project_structure():
    """Create project directory structure"""
    print("\nCreating project structure...")
    
    directories = [
        "agents",
        "models",
        "utils",
        "logs",
        "data",
        "exports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Create empty __init__.py files
    init_files = ["agents/__init__.py", "models/__init__.py", "utils/__init__.py"]
    for init_file in init_files:
        Path(init_file).touch(exist_ok=True)
        print(f"✓ Created file: {init_file}")

def main():
    """Main setup function"""
    print("=" * 60)
    print("Gemini-based Interview AI Framework Setup")
    print("=" * 60)
    
    # Check Python version
    check_python_version()
    
    # Create project structure
    create_project_structure()
    
    # Install dependencies
    install_dependencies()
    
    # Setup environment
    setup_environment()
    
    # Verify installation
    verify_gemini_installation()
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETED!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Get your Google Gemini API key from: https://makersuite.google.com/app/apikey")
    print("2. Edit the .env file and add your API key")
    print("3. Run the demo: python main_gemini.py")
    print("\nOptional: Set up Google Cloud for higher rate limits")
    print("- Enable Gemini API: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com")
    print("\nFor help, check the README.md file")
    print("=" * 60)

if __name__ == "__main__":
    main()