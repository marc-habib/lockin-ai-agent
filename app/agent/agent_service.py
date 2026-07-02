"""
Agent service for LockIn AI.

Handles LLM interaction and function calling orchestration.
"""

from typing import List, Dict, Any
from app.clients.llm_client import get_llm_client
from app.agent.tool_registry import tool_registry
from app.agent.tool_executor import tool_executor
from app.prompts import get_system_prompt, get_reflection_prompt
from app.schemas.profile import ProfileResponse
from app.config import settings
from app.models.enums import Intent


class AgentService:
    """Service for agent execution with LLM and tools."""
    
    def __init__(self):
        """Initialize the agent service."""
        self.llm_client = None  # Lazy initialization
        self.registry = tool_registry
        self.executor = tool_executor
        self.max_iterations = settings.max_reasoning_steps
        self.enable_reflection = settings.enable_reflection
    
    def _get_llm_client(self):
        """Lazy initialization of LLM client."""
        if self.llm_client is None:
            self.llm_client = get_llm_client()
        return self.llm_client
    
    def run(
        self,
        message: str,
        profile: ProfileResponse,
        intent: Intent,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Run the agent with function calling.
        
        Args:
            message: User message
            profile: User profile
            intent: Classified intent
            user_id: User identifier
        
        Returns:
            Dict with response, tool_calls, and usage
        """
        # Get tools for intent
        tools = self.registry.get_tools_for_intent(intent)
        tool_schemas = self.registry.get_tool_schemas(tools)
        
        # Build messages
        system_prompt = get_system_prompt(profile)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        # Track iterations and tool calls
        iterations = 0
        all_tool_calls = []
        tool_results = []
        
        while iterations < self.max_iterations:
            iterations += 1
            
            # Call LLM
            try:
                llm_response = self._get_llm_client().chat(
                    messages=messages,
                    tools=tool_schemas if tool_schemas else None,
                    temperature=0.7,
                    max_tokens=2000
                )
            except Exception as e:
                return {
                    'response': f"Error calling LLM: {str(e)}",
                    'tool_calls': all_tool_calls,
                    'tool_results': tool_results,
                    'usage': {'input_tokens': 0, 'output_tokens': 0},
                    'iterations': iterations,
                    'error': str(e)
                }
            
            # Check if LLM wants to use tools
            if llm_response.get('tool_calls'):
                # Execute tool calls
                tool_call_list = llm_response['tool_calls']
                
                # Parse and prepare tool calls for execution
                exec_tool_calls = []
                for tool_call in tool_call_list:
                    # Parse arguments if they're a string
                    import json
                    args = tool_call['function']['arguments']
                    if isinstance(args, str):
                        args = json.loads(args)
                    
                    # Inject user_id into get_progress tool calls
                    if tool_call['function']['name'] == 'get_progress':
                        args['user_id'] = user_id
                    
                    exec_tool_calls.append({
                        'id': tool_call['id'],
                        'name': tool_call['function']['name'],
                        'arguments': args
                    })
                
                results = self.executor.execute_tool_calls(exec_tool_calls)
                
                # Track tool calls and results
                all_tool_calls.extend([tc['function']['name'] for tc in tool_call_list])
                tool_results.extend(results)
                
                # Add assistant message with tool calls (OpenAI format)
                messages.append({
                    "role": "assistant",
                    "content": llm_response.get('content'),
                    "tool_calls": tool_call_list
                })
                
                # Add tool results to messages (OpenAI format)
                for result in results:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": result['call_id'],
                        "content": str(result['result']) if result['success'] else f"Error: {result['error']}"
                    })
                
                # Continue to next iteration
                continue
            
            # No more tool calls - we have final response
            final_response = llm_response.get('content', '')
            
            # Apply reflection if enabled
            if self.enable_reflection and final_response:
                final_response = self._apply_reflection(
                    messages=messages,
                    response=final_response,
                    tool_results=tool_results
                )
            
            return {
                'response': final_response,
                'tool_calls': list(set(all_tool_calls)),  # Unique tool names
                'tool_results': tool_results,
                'usage': llm_response.get('usage', {}),
                'iterations': iterations
            }
        
        # Max iterations reached
        return {
            'response': "I apologize, but I've reached my reasoning limit. Please try rephrasing your request.",
            'tool_calls': list(set(all_tool_calls)),
            'tool_results': tool_results,
            'usage': {'input_tokens': 0, 'output_tokens': 0},
            'iterations': iterations
        }
    
    def _apply_reflection(
        self,
        messages: List[Dict[str, str]],
        response: str,
        tool_results: List[Dict[str, Any]]
    ) -> str:
        """
        Apply reflection to validate the response.
        
        Args:
            messages: Conversation messages
            response: Agent's response
            tool_results: Tool execution results
        
        Returns:
            Validated or revised response
        """
        # Add reflection prompt
        reflection_prompt = get_reflection_prompt()
        
        reflection_messages = messages + [
            {"role": "assistant", "content": response},
            {"role": "user", "content": f"{reflection_prompt}\n\nYour response: {response}\n\nIs this response valid? If not, provide a corrected version."}
        ]
        
        try:
            reflection_response = self._get_llm_client().chat(
                messages=reflection_messages,
                tools=None,
                temperature=0.3,
                max_tokens=1000
            )
            
            reflected_content = reflection_response.get('content', '')
            
            # Reflection is currently only used as an internal validation step.
            # Never replace the user-facing response with the reflection output.
            return response
            
        except Exception:
            # If reflection fails, return original response
            pass
        
        return response


# Global service instance
agent_service = AgentService()
