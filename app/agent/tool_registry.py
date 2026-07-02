"""
Tool registry for LockIn AI.

Manages available tools and provides them based on intent.
"""

from typing import List, Dict, Any
from app.models.enums import Intent
from app.tools.base import BaseTool
from app.tools import (
    food_lookup_tool,
    product_lookup_tool,
    recipe_macro_tool,
    daily_planner_tool,
    get_progress_tool,
)


class ToolRegistry:
    """Registry for managing and providing tools."""
    
    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self) -> None:
        """Register all default tools."""
        self.register(food_lookup_tool)
        self.register(product_lookup_tool)
        self.register(recipe_macro_tool)
        self.register(daily_planner_tool)
        self.register(get_progress_tool)
    
    def register(self, tool: BaseTool) -> None:
        """
        Register a tool.
        
        Args:
            tool: Tool instance to register
        """
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> BaseTool | None:
        """
        Get a tool by name.
        
        Args:
            name: Tool name
        
        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(name)
    
    def get_all_tools(self) -> List[BaseTool]:
        """
        Get all registered tools.
        
        Returns:
            List of all tools
        """
        return list(self._tools.values())
    
    def get_tools_for_intent(self, intent: Intent) -> List[BaseTool]:
        """
        Get tools appropriate for a given intent.
        
        Args:
            intent: User intent
        
        Returns:
            List of relevant tools
        """
        intent_tool_mapping = {
            Intent.FOOD_SEARCH: [food_lookup_tool],
            Intent.PRODUCT_SEARCH: [product_lookup_tool],
            Intent.RECIPE: [food_lookup_tool, recipe_macro_tool],
            Intent.MEAL_PLAN: [food_lookup_tool, daily_planner_tool],
            Intent.PROGRESS: [get_progress_tool, daily_planner_tool],
            Intent.SHOPPING_LIST: [food_lookup_tool, daily_planner_tool],
            Intent.WORKOUT: [],  # No specific tools yet
            Intent.PRODUCTIVITY: [],  # No specific tools yet
            Intent.GENERAL_FITNESS: [],  # No specific tools needed
            Intent.UNKNOWN: [food_lookup_tool],  # Default to basic search
        }
        
        return intent_tool_mapping.get(intent, [])
    
    def get_tool_schemas(self, tools: List[BaseTool]) -> List[Dict[str, Any]]:
        """
        Get function schemas for a list of tools.
        
        Args:
            tools: List of tools
        
        Returns:
            List of function schemas for LLM
        """
        return [tool.to_function_schema() for tool in tools]


# Global registry instance
tool_registry = ToolRegistry()
