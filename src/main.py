#!/usr/bin/env python3
"""
Main execution script for AI Whisperer
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from api.config import Config
from data_processor import DataProcessor
from api.ai_whisperer import AIWhisperer

def main():
    """Main function to run AI Whisperer"""
    print("🚀 Starting AI Whisperer...")
    
    # Initialize configuration
    config = Config()
    
    # Check if API key is set
    if not config.OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your API key in .env file or as environment variable")
        return
    
    # Process data if needed
    if not config.COMBINED_DATASET.exists():
        print("📊 Processing dataset...")
        processor = DataProcessor(str(config.DATA_DIR))
        processor.process_all_data()
    
    # Initialize AI Whisperer
    whisperer = AIWhisperer(config)
    
    # Example usage
    test_requests = [
        "Create a website for my bakery that sells custom cakes and pastries",
        "I need a portfolio website for my photography business",
        "Build a website for my digital marketing consulting firm",
        "Make a travel blog website for my adventures around the world"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}: {request}")
        print(f"{'='*60}")
        
        # Generate and execute prompt chain
        results = whisperer.execute_prompt_chain(request)
        
        # Save results
        output_file = whisperer.save_results(results)
        
        print(f"✅ Test case {i} completed. Results saved to: {output_file}")

def interactive_mode():
    """Interactive mode for custom requests"""
    config = Config()
    
    if not config.OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY not found")
        return
    
    whisperer = AIWhisperer(config)
    
    print("\n🎯 AI Whisperer - Interactive Mode")
    print("Enter your website creation request (or 'quit' to exit):")
    
    while True:
        user_input = input("\n💬 Your request: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
            
        if len(user_input) < 10:
            print("Please provide a more detailed request.")
            continue
        
        print(f"\n🔄 Processing: {user_input}")
        
        # Execute prompt chain
        results = whisperer.execute_prompt_chain(user_input)
        
        # Save results
        output_file = whisperer.save_results(results)
        
        print(f"\n✅ Complete! Results saved to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        main()
