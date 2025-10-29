"""
Test script for the Browser Agent.

This script tests the basic functionality of the BrowserAgent class
without requiring Azure OpenAI credentials.
"""

import os
import sys
from unittest.mock import Mock, patch, MagicMock


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        from browser_agent import BrowserAgent
        print("✓ Successfully imported BrowserAgent")
        return True
    except Exception as e:
        print(f"✗ Failed to import: {e}")
        return False


def test_action_parsing():
    """Test the LLM response parsing logic."""
    print("\nTesting action parsing...")
    
    try:
        from browser_agent import BrowserAgent
        
        agent = BrowserAgent.__new__(BrowserAgent)  # Create without __init__
        
        # Test case 1: Navigate action
        response1 = """Thought: I need to navigate to the website
Action: navigate
Action Input: {"url": "https://example.com"}"""
        
        thought, action, params = agent.parse_llm_response(response1)
        assert action == "navigate", f"Expected 'navigate', got '{action}'"
        assert params.get("url") == "https://example.com", f"Expected URL, got {params}"
        print("✓ Navigate action parsing works")
        
        # Test case 2: Final answer
        response2 = """Final Answer: Task completed successfully"""
        
        thought, action, params = agent.parse_llm_response(response2)
        assert action == "FINISH", f"Expected 'FINISH', got '{action}'"
        print("✓ Final answer parsing works")
        
        # Test case 3: Click action
        response3 = """Thought: Now I need to click the button
Action: click
Action Input: {"selector": "button#submit"}"""
        
        thought, action, params = agent.parse_llm_response(response3)
        assert action == "click", f"Expected 'click', got '{action}'"
        assert params.get("selector") == "button#submit", f"Expected selector, got {params}"
        print("✓ Click action parsing works")
        
        return True
        
    except Exception as e:
        print(f"✗ Parsing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_browser_actions():
    """Test browser action execution with mocked Playwright."""
    print("\nTesting browser actions...")
    
    try:
        from browser_agent import BrowserAgent
        
        # Mock environment variables
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': 'test_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
            'AZURE_OPENAI_DEPLOYMENT': 'test-deployment'
        }):
            # Mock AzureOpenAI
            with patch('browser_agent.AzureOpenAI'):
                agent = BrowserAgent()
                
                # Mock page object
                mock_page = Mock()
                mock_page.url = "https://example.com"
                mock_page.title.return_value = "Example Domain"
                mock_page.content.return_value = "<html><body>Test</body></html>"
                mock_page.text_content.return_value = "Example Domain"
                
                agent.page = mock_page
                
                # Test navigate action
                result = agent.execute_action("navigate", {"url": "https://example.com"})
                assert result["success"], "Navigate should succeed"
                mock_page.goto.assert_called_once_with("https://example.com")
                print("✓ Navigate action works")
                
                # Test click action
                result = agent.execute_action("click", {"selector": "button"})
                assert result["success"], "Click should succeed"
                mock_page.click.assert_called_once_with("button")
                print("✓ Click action works")
                
                # Test type action
                result = agent.execute_action("type", {"selector": "input", "text": "test"})
                assert result["success"], "Type should succeed"
                mock_page.fill.assert_called_once_with("input", "test")
                print("✓ Type action works")
                
                # Test get_text action
                result = agent.execute_action("get_text", {"selector": "h1"})
                assert result["success"], "Get text should succeed"
                assert result["result"] == "Example Domain"
                print("✓ Get text action works")
                
                # Test unknown action
                result = agent.execute_action("unknown", {})
                assert not result["success"], "Unknown action should fail"
                print("✓ Unknown action handling works")
                
        return True
        
    except Exception as e:
        print(f"✗ Browser action test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_system_prompt():
    """Test that system prompt is generated correctly."""
    print("\nTesting system prompt generation...")
    
    try:
        from browser_agent import BrowserAgent
        
        # Mock environment and client
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': 'test_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
            'AZURE_OPENAI_DEPLOYMENT': 'test-deployment'
        }):
            with patch('browser_agent.AzureOpenAI'):
                agent = BrowserAgent()
                prompt = agent.create_system_prompt()
                
                # Check that prompt contains key elements
                assert "browser automation agent" in prompt.lower(), "Should mention browser automation"
                assert "navigate" in prompt.lower(), "Should mention navigate action"
                assert "click" in prompt.lower(), "Should mention click action"
                assert "ReAct" in prompt, "Should mention ReAct format"
                assert "Thought:" in prompt, "Should show thought format"
                assert "Action:" in prompt, "Should show action format"
                print("✓ System prompt generation works")
                
        return True
        
    except Exception as e:
        print(f"✗ System prompt test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Browser Agent Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_action_parsing,
        test_browser_actions,
        test_system_prompt,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
