"""
Browser Agent using Azure OpenAI and Playwright with ReAct-style loop.

This module implements a browser agent that uses Azure OpenAI's LLM to reason
about browser interactions and execute actions using Playwright.
"""

import os
import json
from typing import Dict, List, Any, Optional
from openai import AzureOpenAI
from playwright.sync_api import sync_playwright, Page, Browser
from dotenv import load_dotenv


class BrowserAgent:
    """
    A browser agent that uses Azure OpenAI LLM with ReAct-style reasoning
    to interact with web pages using Playwright.
    """
    
    def __init__(self):
        """Initialize the browser agent with Azure OpenAI and Playwright."""
        load_dotenv()
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        
        # Playwright components
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
        # ReAct loop configuration
        self.max_iterations = 10
        self.history: List[Dict[str, str]] = []
        
    def start_browser(self, headless: bool = False):
        """Start the Playwright browser."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.page = self.browser.new_page()
        
    def stop_browser(self):
        """Stop the Playwright browser."""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
            
    def get_page_info(self) -> Dict[str, Any]:
        """Get current page information."""
        if not self.page:
            return {"error": "Browser not started"}
        
        try:
            return {
                "url": self.page.url,
                "title": self.page.title(),
                "content": self.page.content()[:1000]  # Limit content size
            }
        except Exception as e:
            return {"error": str(e)}
    
    def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a browser action.
        
        Supported actions:
        - navigate: Navigate to a URL
        - click: Click on an element
        - type: Type text into an element
        - get_text: Get text from an element
        - screenshot: Take a screenshot
        """
        if not self.page:
            return {"success": False, "error": "Browser not started"}
        
        try:
            if action == "navigate":
                url = params.get("url", "")
                self.page.goto(url)
                return {"success": True, "result": f"Navigated to {url}"}
            
            elif action == "click":
                selector = params.get("selector", "")
                self.page.click(selector)
                return {"success": True, "result": f"Clicked on {selector}"}
            
            elif action == "type":
                selector = params.get("selector", "")
                text = params.get("text", "")
                self.page.fill(selector, text)
                return {"success": True, "result": f"Typed '{text}' into {selector}"}
            
            elif action == "get_text":
                selector = params.get("selector", "")
                text = self.page.text_content(selector)
                return {"success": True, "result": text}
            
            elif action == "screenshot":
                path = params.get("path", "screenshot.png")
                self.page.screenshot(path=path)
                return {"success": True, "result": f"Screenshot saved to {path}"}
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def parse_llm_response(self, response: str) -> tuple[str, str, Dict[str, Any]]:
        """
        Parse LLM response in ReAct format.
        
        Expected format:
        Thought: <reasoning>
        Action: <action_name>
        Action Input: <json_params>
        
        Returns:
            tuple: (thought, action, params)
        """
        thought = ""
        action = ""
        params = {}
        
        lines = response.strip().split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith("Thought:"):
                thought = line.replace("Thought:", "").strip()
            elif line.startswith("Action:"):
                action = line.replace("Action:", "").strip()
            elif line.startswith("Action Input:"):
                # Parse JSON from remaining lines
                json_str = line.replace("Action Input:", "").strip()
                i += 1
                while i < len(lines) and not lines[i].strip().startswith(("Thought:", "Action:", "Final Answer:")):
                    json_str += "\n" + lines[i].strip()
                    i += 1
                i -= 1  # Step back one line
                
                try:
                    params = json.loads(json_str)
                except json.JSONDecodeError:
                    # Try to extract JSON object
                    if "{" in json_str and "}" in json_str:
                        json_start = json_str.index("{")
                        json_end = json_str.rindex("}") + 1
                        params = json.loads(json_str[json_start:json_end])
            elif line.startswith("Final Answer:"):
                # Task is complete
                action = "FINISH"
                thought = line.replace("Final Answer:", "").strip()
                break
            
            i += 1
        
        return thought, action, params
    
    def create_system_prompt(self) -> str:
        """Create the system prompt for the LLM."""
        return """You are a browser automation agent. You can interact with web pages using the following actions:

1. navigate - Navigate to a URL
   Action Input: {"url": "https://example.com"}

2. click - Click on an element
   Action Input: {"selector": "button#submit"}

3. type - Type text into an element
   Action Input: {"selector": "input#search", "text": "search query"}

4. get_text - Get text from an element
   Action Input: {"selector": "h1"}

5. screenshot - Take a screenshot
   Action Input: {"path": "screenshot.png"}

Use the ReAct format to reason and act:

Thought: [Your reasoning about what to do next]
Action: [The action to take: navigate, click, type, get_text, or screenshot]
Action Input: [JSON parameters for the action]

After receiving the observation, continue reasoning. When you've completed the task, use:

Final Answer: [Summary of what was accomplished]

Always reason step by step and explain your actions."""
    
    def run(self, task: str, headless: bool = False) -> str:
        """
        Run the browser agent with a given task using ReAct-style loop.
        
        Args:
            task: The task description for the agent
            headless: Whether to run browser in headless mode
            
        Returns:
            str: Final answer or error message
        """
        try:
            self.start_browser(headless=headless)
            
            messages = [
                {"role": "system", "content": self.create_system_prompt()},
                {"role": "user", "content": f"Task: {task}"}
            ]
            
            for iteration in range(self.max_iterations):
                print(f"\n--- Iteration {iteration + 1} ---")
                
                # Get LLM response
                response = self.client.chat.completions.create(
                    model=self.deployment,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                
                assistant_message = response.choices[0].message.content
                print(f"LLM Response:\n{assistant_message}\n")
                
                messages.append({"role": "assistant", "content": assistant_message})
                
                # Parse response
                thought, action, params = self.parse_llm_response(assistant_message)
                
                # Check if finished
                if action == "FINISH":
                    print(f"Task completed: {thought}")
                    return thought
                
                # Execute action
                if action:
                    print(f"Executing action: {action} with params: {params}")
                    result = self.execute_action(action, params)
                    print(f"Result: {result}\n")
                    
                    # Add observation to messages
                    observation = f"Observation: {json.dumps(result)}"
                    messages.append({"role": "user", "content": observation})
                else:
                    # No valid action found, ask for clarification
                    messages.append({
                        "role": "user",
                        "content": "Please provide a valid action in the specified format."
                    })
            
            return "Maximum iterations reached without completion."
            
        finally:
            self.stop_browser()


def main():
    """Example usage of the browser agent."""
    # Example task
    task = "Navigate to https://www.example.com and get the main heading text"
    
    agent = BrowserAgent()
    result = agent.run(task, headless=False)
    
    print("\n=== Final Result ===")
    print(result)


if __name__ == "__main__":
    main()
