"""
Tool executor for LockIn AI.

Executes tools and collects observations.
"""

from typing import List, Dict, Any
from app.agent.tool_registry import tool_registry


class ToolExecutor:
    """Executes tools and manages tool results."""
    
    def __init__(self):
        """Initialize the tool executor."""
        self.registry = tool_registry
    
    def execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute multiple tool calls.
        
        Args:
            tool_calls: List of tool call dicts with 'name' and 'arguments'
        
        Returns:
            List of tool results
        """
        results = []
        
        for tool_call in tool_calls:
            result = self.execute_tool_call(
                tool_name=tool_call.get('name'),
                arguments=tool_call.get('arguments', {}),
                call_id=tool_call.get('id')
            )
            results.append(result)
        
        return results
    
    def execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        call_id: str | None = None
    ) -> Dict[str, Any]:
        """
        Execute a single tool call.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            call_id: Optional call ID for tracking
        
        Returns:
            Tool result dict
        """
        # Get tool from registry
        tool = self.registry.get_tool(tool_name)
        
        if not tool:
            return {
                'tool_name': tool_name,
                'call_id': call_id,
                'success': False,
                'error': f"Tool '{tool_name}' not found",
                'result': None
            }
        
        # Execute tool
        try:
            result = tool.execute(**arguments)
            
            return {
                'tool_name': tool_name,
                'call_id': call_id,
                'success': True,
                'error': None,
                'result': result
            }
        
        except Exception as e:
            return {
                'tool_name': tool_name,
                'call_id': call_id,
                'success': False,
                'error': str(e),
                'result': None
            }
    
    def format_tool_results_for_llm(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format tool results for LLM consumption.
        
        Args:
            results: List of tool results
        
        Returns:
            Formatted results for LLM
        """
        formatted = []
        
        for result in results:
            if result['success']:
                formatted.append({
                    'tool_call_id': result.get('call_id'),
                    'role': 'tool',
                    'name': result['tool_name'],
                    'content': str(result['result'])
                })
            else:
                formatted.append({
                    'tool_call_id': result.get('call_id'),
                    'role': 'tool',
                    'name': result['tool_name'],
                    'content': f"Error: {result['error']}"
                })
        
        return formatted


# Global executor instance
tool_executor = ToolExecutor()
