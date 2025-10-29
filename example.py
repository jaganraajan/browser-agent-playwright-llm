"""
Example demonstrating the BrowserAgent structure and capabilities.

This example shows how the agent would work with a mock LLM response.
For actual usage, you need to set up Azure OpenAI credentials in .env file.
"""

from browser_agent import BrowserAgent


def demo_agent_structure():
    """Demonstrate the agent's structure and capabilities."""
    
    ACTION_NAME_WIDTH = 12  # Width for formatting action names
    
    print("=" * 70)
    print("Browser Agent Demo - Structure and Capabilities")
    print("=" * 70)
    
    print("\n1. SUPPORTED ACTIONS:")
    print("-" * 70)
    actions = {
        "navigate": "Navigate to a URL",
        "click": "Click on an element using CSS selector",
        "type": "Type text into an input field",
        "get_text": "Extract text from an element",
        "screenshot": "Take a screenshot of the page"
    }
    
    for action, description in actions.items():
        print(f"   • {action:{ACTION_NAME_WIDTH}} - {description}")
    
    print("\n2. REACT LOOP PROCESS:")
    print("-" * 70)
    print("   Step 1: LLM analyzes the task and current state")
    print("   Step 2: LLM generates a Thought (reasoning)")
    print("   Step 3: LLM selects an Action to take")
    print("   Step 4: Agent executes the Action")
    print("   Step 5: Agent observes the result")
    print("   Step 6: Repeat until task is complete")
    
    print("\n3. EXAMPLE REACT FORMAT:")
    print("-" * 70)
    print('''
   Thought: I need to navigate to the website first
   Action: navigate
   Action Input: {"url": "https://www.example.com"}
   
   [After observation]
   
   Thought: Now I can extract the heading text
   Action: get_text
   Action Input: {"selector": "h1"}
   
   [After observation]
   
   Final Answer: The heading text is "Example Domain"
    ''')
    
    print("\n4. HOW TO USE:")
    print("-" * 70)
    print("""
   # Set up environment variables in .env file:
   AZURE_OPENAI_API_KEY=your_api_key
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=your-deployment-name
   
   # Create and run the agent:
   from browser_agent import BrowserAgent
   
   agent = BrowserAgent()
   result = agent.run("Navigate to example.com and get the title", headless=False)
   print(result)
    """)
    
    print("\n5. CONFIGURATION:")
    print("-" * 70)
    print(f"   • Maximum iterations: 10 (configurable)")
    print(f"   • Browser mode: Headless or visible")
    print(f"   • LLM temperature: 0.7 (balanced creativity)")
    print(f"   • Max tokens per response: 500")
    
    print("\n" + "=" * 70)
    print("To run with actual Azure OpenAI:")
    print("  1. Copy .env.example to .env")
    print("  2. Fill in your Azure OpenAI credentials")
    print("  3. Install Playwright browsers: playwright install chromium")
    print("  4. Run: python main.py")
    print("=" * 70 + "\n")


def demo_parsing_logic():
    """Demonstrate the LLM response parsing logic."""
    
    print("\n" + "=" * 70)
    print("Response Parsing Demo")
    print("=" * 70)
    
    # Create agent instance without initialization
    agent = BrowserAgent.__new__(BrowserAgent)
    
    # Example responses
    examples = [
        {
            "name": "Navigate Action",
            "response": '''Thought: I need to go to the website
Action: navigate
Action Input: {"url": "https://example.com"}'''
        },
        {
            "name": "Click Action",
            "response": '''Thought: Now I'll click the submit button
Action: click
Action Input: {"selector": "button#submit"}'''
        },
        {
            "name": "Completion",
            "response": '''Final Answer: Successfully completed the task'''
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['name']}:")
        print("-" * 70)
        print("Input:")
        print(example['response'])
        print("\nParsed:")
        thought, action, params = agent.parse_llm_response(example['response'])
        print(f"  Thought: {thought}")
        print(f"  Action: {action}")
        print(f"  Params: {params}")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    demo_agent_structure()
    demo_parsing_logic()
