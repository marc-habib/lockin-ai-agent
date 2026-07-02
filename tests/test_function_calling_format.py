"""
Regression test for OpenAI function calling message format bug.

Tests that tool_calls are properly formatted with "type": "function"
and that tool responses use "tool_call_id" instead of "name".
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from app.agent.agent_service import AgentService
from app.agent.handler import run_agent_handler
from app.models.enums import Intent, RequestStatus
from app.schemas.profile import ProfileResponse, MacroTargets


class TestFunctionCallingFormat:
    """Test OpenAI function calling message format."""
    
    def test_llm_client_returns_correct_tool_call_format(self):
        """Test that LLM client returns tool_calls with correct OpenAI format."""
        from app.clients.llm_client import LLMClient
        
        # Mock OpenAI response
        mock_tool_call = Mock()
        mock_tool_call.id = "call_abc123"
        mock_tool_call.function.name = "daily_planner"
        mock_tool_call.function.arguments = '{"target_calories": 2500}'
        
        mock_message = Mock()
        mock_message.content = None
        mock_message.tool_calls = [mock_tool_call]
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=mock_message)]
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=50)
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            llm_client = LLMClient(provider="openai", model="gpt-4o-mini", api_key="test-key")
            result = llm_client.chat(
                messages=[{"role": "user", "content": "Plan my meals"}],
                tools=[{"name": "daily_planner", "description": "Generate meal plan"}]
            )
        
        # Verify tool_calls format
        assert len(result['tool_calls']) == 1
        tool_call = result['tool_calls'][0]
        
        # CRITICAL: Must have "type": "function"
        assert 'type' in tool_call, "Missing 'type' field in tool_call"
        assert tool_call['type'] == 'function', "tool_call type must be 'function'"
        
        # CRITICAL: Must have "function" wrapper
        assert 'function' in tool_call, "Missing 'function' wrapper in tool_call"
        assert 'name' in tool_call['function'], "Missing 'name' in function"
        assert 'arguments' in tool_call['function'], "Missing 'arguments' in function"
        
        # Verify structure
        assert tool_call['id'] == 'call_abc123'
        assert tool_call['function']['name'] == 'daily_planner'
        assert isinstance(tool_call['function']['arguments'], str), "arguments must be string"
    
    def test_agent_service_formats_messages_correctly(self, sample_profile):
        """Test that agent service formats messages with correct OpenAI structure."""
        profile = sample_profile
        
        # Mock LLM response with tool call
        mock_llm_response = {
            'content': None,
            'tool_calls': [{
                'id': 'call_xyz789',
                'type': 'function',
                'function': {
                    'name': 'daily_planner',
                    'arguments': '{"target_calories": 2700, "target_protein_g": 135, "target_carbs_g": 300, "target_fat_g": 75, "num_meals": 3}'
                }
            }],
            'usage': {'input_tokens': 100, 'output_tokens': 50}
        }
        
        # Mock final response (no more tool calls)
        mock_final_response = {
            'content': 'Here is your meal plan...',
            'tool_calls': [],
            'usage': {'input_tokens': 150, 'output_tokens': 100}
        }
        
        with patch.object(AgentService, '_get_llm_client') as mock_get_client:
            mock_client = Mock()
            # First call returns tool_calls, second call returns final response
            mock_client.chat.side_effect = [mock_llm_response, mock_final_response]
            mock_get_client.return_value = mock_client
            
            with patch('app.agent.agent_service.tool_executor') as mock_executor:
                # Mock tool execution
                mock_executor.execute_tool_calls.return_value = [{
                    'tool_name': 'daily_planner',
                    'call_id': 'call_xyz789',
                    'success': True,
                    'error': None,
                    'result': {'meals': []}
                }]
                
                agent = AgentService()
                result = agent.run(
                    message="Plan my meals",
                    profile=profile,
                    intent=Intent.MEAL_PLAN,
                    user_id="test_user"
                )
        
        # Verify LLM was called with correctly formatted messages
        calls = mock_client.chat.call_args_list
        
        # Second call should have assistant message with tool_calls
        second_call_messages = calls[1][1]['messages']
        
        # Find assistant message with tool_calls
        assistant_msg = None
        tool_msg = None
        for msg in second_call_messages:
            if msg['role'] == 'assistant' and 'tool_calls' in msg:
                assistant_msg = msg
            elif msg['role'] == 'tool':
                tool_msg = msg
        
        # CRITICAL: Assistant message must have tool_calls in correct format
        assert assistant_msg is not None, "Missing assistant message with tool_calls"
        assert 'tool_calls' in assistant_msg
        assert len(assistant_msg['tool_calls']) == 1
        
        tool_call = assistant_msg['tool_calls'][0]
        assert tool_call['type'] == 'function', "tool_call must have type='function'"
        assert 'function' in tool_call, "tool_call must have 'function' wrapper"
        
        # CRITICAL: Tool response must use "tool_call_id" not "name"
        assert tool_msg is not None, "Missing tool response message"
        assert 'tool_call_id' in tool_msg, "Tool message must have 'tool_call_id'"
        assert tool_msg['tool_call_id'] == 'call_xyz789'
        assert 'name' not in tool_msg or tool_msg.get('name') is None, "Tool message should not have 'name' field for OpenAI"
    
    def test_handler_returns_error_status_on_llm_failure(self, sample_profile):
        """Test that handler returns ERROR status when LLM call fails."""
        with patch('app.agent.handler.profile_guardrails') as mock_profile_guard:
            # Mock profile validation
            mock_profile = sample_profile
            mock_profile_guard.get_profile_or_error.return_value = (mock_profile, None)
            
            with patch('app.agent.handler.input_guardrails') as mock_input_guard:
                mock_input_guard.validate.return_value = (True, None)
                
                with patch('app.agent.handler.agent_service') as mock_agent:
                    # Simulate LLM error
                    mock_agent.run.return_value = {
                        'response': 'Error calling LLM: Missing required parameter',
                        'tool_calls': [],
                        'tool_results': [],
                        'usage': {'input_tokens': 0, 'output_tokens': 0},
                        'iterations': 1,
                        'error': 'Missing required parameter: messages[2].tool_calls[0].type'
                    }
                    
                    response = run_agent_handler(user_id="test_user", message="Plan my meals")
        
        # CRITICAL: Must return ERROR status, not SUCCESS
        assert response.status == RequestStatus.ERROR, "Handler must return ERROR status when LLM fails"
        assert "Error calling LLM" in response.response or "error occurred" in response.response.lower()
    
    def test_tool_call_arguments_are_parsed_correctly(self, sample_profile):
        """Test that string arguments are parsed to dict before tool execution."""
        from app.agent.agent_service import AgentService
        
        profile = sample_profile
        
        # Mock LLM response with string arguments (as OpenAI returns)
        mock_llm_response = {
            'content': None,
            'tool_calls': [{
                'id': 'call_test',
                'type': 'function',
                'function': {
                    'name': 'food_lookup',
                    'arguments': '{"query": "chicken breast", "limit": 5}'  # String format
                }
            }],
            'usage': {'input_tokens': 50, 'output_tokens': 25}
        }
        
        mock_final_response = {
            'content': 'Found chicken breast nutrition data',
            'tool_calls': [],
            'usage': {'input_tokens': 100, 'output_tokens': 50}
        }
        
        with patch.object(AgentService, '_get_llm_client') as mock_get_client:
            mock_client = Mock()
            mock_client.chat.side_effect = [mock_llm_response, mock_final_response]
            mock_get_client.return_value = mock_client
            
            with patch('app.agent.agent_service.tool_executor') as mock_executor:
                mock_executor.execute_tool_calls.return_value = [{
                    'tool_name': 'food_lookup',
                    'call_id': 'call_test',
                    'success': True,
                    'error': None,
                    'result': []
                }]
                
                agent = AgentService()
                result = agent.run(
                    message="Find chicken breast",
                    profile=profile,
                    intent=Intent.FOOD_SEARCH,
                    user_id="test_user"
                )
                
                # Verify tool executor was called with parsed dict arguments
                call_args = mock_executor.execute_tool_calls.call_args[0][0]
                assert len(call_args) == 1
                tool_call = call_args[0]
                
                # Arguments must be dict, not string
                assert isinstance(tool_call['arguments'], dict), "Arguments must be parsed to dict"
                assert tool_call['arguments']['query'] == 'chicken breast'
                assert tool_call['arguments']['limit'] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
