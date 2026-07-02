"""
Food lookup tool for LockIn AI.

Searches CIQUAL database for generic food nutrition data.
"""

from typing import Any, Dict
from app.tools.base import BaseTool
from app.clients.ciqual_client import ciqual_client
from app.schemas.tools import FoodLookupOutput


class FoodLookupTool(BaseTool):
    """Tool for searching CIQUAL food database."""
    
    def __init__(self):
        self.client = ciqual_client
        super().__init__()
    
    def _get_name(self) -> str:
        return "food_lookup"
    
    def _get_description(self) -> str:
        return "Search for generic food nutrition data from the CIQUAL database. Use this for whole foods like fruits, vegetables, meats, grains, etc. Returns nutrition per 100g."
    
    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Food name to search for (e.g., 'chicken breast', 'banana', 'oats')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    
    def execute(self, query: str, limit: int = 5, **kwargs) -> Dict[str, Any]:
        """
        Execute food lookup.
        
        Args:
            query: Food name to search for
            limit: Maximum number of results
            **kwargs: Additional parameters (ignored)
        
        Returns:
            Dict with search results
        """
        # Search CIQUAL database
        results = self.client.search(query, limit=limit)
        
        # Convert to output schema
        output = FoodLookupOutput(
            results=results,
            query=query,
            source="ciqual"
        )
        
        return output.model_dump()


# Global tool instance
food_lookup_tool = FoodLookupTool()
