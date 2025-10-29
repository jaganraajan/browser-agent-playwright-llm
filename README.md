# Browser Agent with Azure OpenAI and Playwright

A minimal Python implementation of an LLM-powered browser agent using Azure OpenAI and Playwright with ReAct-style reasoning loop.

## Features

- **Azure OpenAI Integration**: Uses Azure OpenAI's language models for intelligent decision-making
- **Playwright Browser Automation**: Automates browser interactions with Playwright
- **ReAct-Style Loop**: Implements Reasoning + Acting loop for task completion
- **Supported Actions**:
  - Navigate to URLs
  - Click on elements
  - Type text into input fields
  - Extract text from elements
  - Take screenshots

## Prerequisites

- Python 3.8 or higher
- Azure OpenAI API access with a deployed model
- Playwright browser drivers

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jaganraajan/browser-agent-playwright-llm.git
cd browser-agent-playwright-llm
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

4. Configure Azure OpenAI credentials:
```bash
cp .env.example .env
```

Edit `.env` and add your Azure OpenAI credentials:
```env
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## Usage

### Basic Usage

Run with a default task:
```bash
python main.py
```

### Custom Task

Provide your own task as a command-line argument:
```bash
python main.py "Navigate to https://www.github.com and search for playwright"
```

### Programmatic Usage

```python
from browser_agent import BrowserAgent

# Create agent instance
agent = BrowserAgent()

# Define your task
task = "Navigate to https://www.example.com and get the main heading"

# Run the agent (headless=False to see the browser)
result = agent.run(task, headless=False)

print(result)
```

## Screenshot Saving

Screenshots taken by the agent are automatically saved in the `playwright-screenshots` folder with a timestamped filename (e.g., `screenshot_20251029_153045.png`).

This ensures all screenshots are organized and uniquely named for each run.

## How It Works

The browser agent uses a **ReAct (Reasoning + Acting)** loop:

1. **Reasoning**: The LLM analyzes the task and current state
2. **Action**: The LLM decides on an action to take
3. **Observation**: The action is executed and results are observed
4. **Iteration**: Steps 1-3 repeat until the task is complete

### ReAct Format

The LLM responds in this format:
```
Thought: [Reasoning about what to do next]
Action: [Action name: navigate, click, type, get_text, or screenshot]
Action Input: [JSON parameters for the action]
```

When complete:
```
Final Answer: [Summary of what was accomplished]
```

## Example

```python
from browser_agent import BrowserAgent

agent = BrowserAgent()
task = "Navigate to https://www.example.com and take a screenshot"
result = agent.run(task, headless=False)
```

Output:
```
--- Iteration 1 ---
LLM Response:
Thought: I need to navigate to the example.com website first
Action: navigate
Action Input: {"url": "https://www.example.com"}

Executing action: navigate with params: {'url': 'https://www.example.com'}
Result: {'success': True, 'result': 'Navigated to https://www.example.com'}

--- Iteration 2 ---
LLM Response:
Thought: Now I'll take a screenshot of the page
Action: screenshot
Action Input: {"path": "example_screenshot.png"}

Executing action: screenshot with params: {'path': 'example_screenshot.png'}
Result: {'success': True, 'result': 'Screenshot saved to example_screenshot.png'}

--- Iteration 3 ---
LLM Response:
Final Answer: Successfully navigated to example.com and saved a screenshot

=== FINAL RESULT ===
Successfully navigated to example.com and saved a screenshot
```

## Architecture

```
┌─────────────────┐
│   User Task     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Browser Agent  │
│   (ReAct Loop)  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────┐
│ Azure   │ │  Playwright  │
│ OpenAI  │ │   Browser    │
│   LLM   │ │  Automation  │
└─────────┘ └──────────────┘
```

## Configuration

### Environment Variables

- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_DEPLOYMENT`: Your deployed model name
- `AZURE_OPENAI_API_VERSION`: API version (default: 2024-02-15-preview)

### Agent Parameters

- `max_iterations`: Maximum number of ReAct loop iterations (default: 10)
- `headless`: Run browser in headless mode (default: False)

## Limitations

- Currently supports basic browser interactions (navigate, click, type, get_text, screenshot)
- Limited to 10 iterations per task by default
- Requires valid Azure OpenAI credentials
- CSS selectors must be provided accurately for element interactions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [Playwright](https://playwright.dev/) - Browser automation framework
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) - LLM service
- [ReAct Paper](https://arxiv.org/abs/2210.03629) - Reasoning + Acting paradigm