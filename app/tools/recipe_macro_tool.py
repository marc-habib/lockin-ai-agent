"""
Recipe macro calculation tool for LockIn AI.

Calculates total macros for a recipe from ingredients.
"""

from typing import Any, Dict, List
from app.tools.base import BaseTool
from app.services.nutrition_service import nutrition_service
from app.schemas.nutrition import RecipeIngredient
from app.schemas.tools import RecipeMacroOutput


class RecipeMacroTool(BaseTool):
    """Tool for calculating recipe macros."""
    
    def __init__(self):
        self.nutrition_service = nutrition_service
        super().__init__()
    
    def _get_name(self) -> str:
        return "recipe_macro"
    
    def _get_description(self) -> str:
        return "Calculate total macros for a recipe from its ingredients. Use this when you need to calculate nutrition for a complete dish or meal. Requires nutrition data per 100g for each ingredient."
    
    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "recipe_name": {
                    "type": "string",
                    "description": "Name of the recipe (optional)"
                },
                "ingredients": {
                    "type": "array",
                    "description": "List of ingredients with their quantities and nutrition per 100g",
                    "items": {
                        "type": "object",
                        "properties": {
                            "food_name": {"type": "string"},
                            "quantity_g": {"type": "number"},
                            "kcal_100g": {"type": "number"},
                            "protein_100g": {"type": "number"},
                            "carbs_100g": {"type": "number"},
                            "fat_100g": {"type": "number"}
                        },
                        "required": ["food_name", "quantity_g", "kcal_100g", "protein_100g", "carbs_100g", "fat_100g"]
                    }
                }
            },
            "required": ["ingredients"]
        }
    
    def execute(self, ingredients: List[Dict[str, Any]], recipe_name: str | None = None, **kwargs) -> Dict[str, Any]:
        """
        Execute recipe macro calculation.
        
        Args:
            ingredients: List of ingredient dicts
            recipe_name: Optional recipe name
            **kwargs: Additional parameters (ignored)
        
        Returns:
            Dict with recipe macros
        """
        # Convert to RecipeIngredient objects
        ingredient_objects = [
            RecipeIngredient(
                food_name=ing["food_name"],
                quantity_g=float(ing["quantity_g"]),
                kcal_100g=float(ing["kcal_100g"]),
                protein_100g=float(ing["protein_100g"]),
                carbs_100g=float(ing["carbs_100g"]),
                fat_100g=float(ing["fat_100g"])
            )
            for ing in ingredients
        ]
        
        # Calculate recipe nutrition
        recipe_macros = self.nutrition_service.calculate_recipe_nutrition(
            recipe_name=recipe_name,
            ingredients=ingredient_objects
        )
        
        # Convert to output schema
        output = RecipeMacroOutput(recipe_macros=recipe_macros)
        
        return output.model_dump()


# Global tool instance
recipe_macro_tool = RecipeMacroTool()
