#!/usr/bin/env python3
"""
RedSet ProtoCell Setup Script
Initializes directories and creates sample prompt files
"""

import os
import sys

def create_directory_structure():
    """Create required directories"""
    directories = [
        'prompts/sniper',
        'logs/spotter',
        'logs/transcripts'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_sample_env_file():
    """Create sample .env file"""
    env_content = """# RedSet ProtoCell Environment Variables
# Copy this to .env and fill in your actual API keys

OPENAI_API_KEY=your_openai_api_key_here
"""
    
    with open('.env.sample', 'w') as f:
        f.write(env_content)
    
    print("✓ Created .env.sample file")

def main():
    print("🎯 RedSet ProtoCell Setup")
    print("=" * 30)
    
    # Create directories
    create_directory_structure()
    
    # Create sample environment file
    create_sample_env_file()
    
    print("\n📋 Setup Complete!")
    print("\nNext steps:")
    print("1. Copy .env.sample to .env and add your OpenAI API key")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the system: python main.py")
    print("\n⚠️  Remember: This is for authorized red team testing only!")

if __name__ == "__main__":
    main()