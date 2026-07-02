"""
Product lookup tool for LockIn AI.

Searches OpenFoodFacts for packaged product nutrition data.
"""

from typing import Any, Dict
from app.tools.base import BaseTool
from app.clients.openfoodfacts_client import openfoodfacts_client
from app.schemas.tools import ProductLookupOutput


class ProductLookupTool(BaseTool):
    """Tool for searching OpenFoodFacts product database."""
    
    def __init__(self):
        self.client = openfoodfacts_client
        super().__init__()
    
    def _get_name(self) -> str:
        return "product_lookup"
    
    def _get_description(self) -> str:
        return "Search for packaged product nutrition data from OpenFoodFacts. Use this for branded products, packaged foods, or when you need allergen/ingredient information. Returns nutrition per 100g plus NutriScore and NOVA group."
    
    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Product name or barcode to search for"
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
        Execute product lookup.
        
        Args:
            query: Product name or barcode
            limit: Maximum number of results
            **kwargs: Additional parameters (ignored)
        
        Returns:
            Dict with search results
        """
        # Search OpenFoodFacts
        results = self.client.search(query, limit=limit)
        
        # Convert to output schema
        output = ProductLookupOutput(
            results=results,
            query=query,
            source="openfoodfacts"
        )
        
        return output.model_dump()


# Global tool instance
product_lookup_tool = ProductLookupTool()
