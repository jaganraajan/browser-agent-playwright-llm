"""
Main entry point for the Browser Agent.

This script demonstrates how to use the BrowserAgent class with Azure OpenAI
to automate browser interactions using natural language tasks.
"""

import sys
from browser_agent import BrowserAgent


def main():
    """Run the browser agent with a task."""
    
    # Default task
    default_task = "Navigate to https://www.example.com and get the main heading text"
    
    # Get task from command line or use default
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        print(f"No task provided. Using default task:")
        print(f"  {default_task}\n")
        task = default_task
    
    print(f"Task: {task}\n")
    print("Starting browser agent...")
    print("-" * 60)
    
    # Create and run agent
    agent = BrowserAgent()
    result = agent.run(task, headless=False)
    
    print("-" * 60)
    print("\n=== FINAL RESULT ===")
    print(result)
    print()


if __name__ == "__main__":
    main()
