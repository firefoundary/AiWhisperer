#!/usr/bin/env python3
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src folder to the system path for imports (adjust if your structure differs)
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from ai_whisperer import AIWhisperer, Config

def main():
    print("🚀 AI Whisperer Starting...")

    # Initialize configuration
    config = Config()

    # Validate API Key
    if not config.GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY environment variable not set.")
        print("Please add your Gemini API key to the .env file or your environment.")
        return

    whisperer = AIWhisperer(config)

    # Accept user input for prompt or use pre-set example
    user_input = input("\nEnter your website creation request:\n> ").strip()
    if not user_input:
        user_input = "Create a website for my bakery selling custom cakes and pastries"

    print(f"\n🎯 Processing your request: {user_input}")

    # Run the prompt chain
    results = whisperer.execute_prompt_chain(user_input)

    # Generate human-readable report
    report = whisperer.generate_final_report(results)

    # Print report to console
    print("\n" + report)

    # Save report to output dir
    output_path = whisperer.save_report(report)
    print(f"\n✅ Report saved to: {output_path}")

if __name__ == "__main__":
    main()
