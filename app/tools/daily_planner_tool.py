"""
Daily planner tool for LockIn AI.

Generates daily meal plans based on targets and preferences.
"""

from typing import Any, Dict
from app.tools.base import BaseTool
from app.services.planning_service import planning_service
from app.schemas.tools import MealPlanOutput


class DailyPlannerTool(BaseTool):
    """Tool for generating daily meal plans."""
    
    def __init__(self):
        self.planning_service = planning_service
        super().__init__()
    
    def _get_name(self) -> str:
        return "daily_planner"
    
    def _get_description(self) -> str:
        return "Generate a complete daily meal plan based on the user's targets and preferences. Use this when the user asks to plan their meals for the day. The planner will automatically use the user's profile targets."
    
    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target_calories": {
                    "type": "number",
                    "description": "Target daily calories"
                },
                "target_protein_g": {
                    "type": "number",
                    "description": "Target daily protein in grams"
                },
                "target_carbs_g": {
                    "type": "number",
                    "description": "Target daily carbs in grams"
                },
                "target_fat_g": {
                    "type": "number",
                    "description": "Target daily fat in grams"
                },
                "num_meals": {
                    "type": "integer",
                    "description": "Number of meals per day (2-6)",
                    "default": 3
                },
                "preferences": {
                    "type": "object",
                    "description": "User preferences including allergies, restrictions, and dislikes",
                    "properties": {
                        "allergies": {"type": "array", "items": {"type": "string"}},
                        "dietary_restrictions": {"type": "array", "items": {"type": "string"}},
                        "disliked_foods": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "required": ["target_calories", "target_protein_g", "target_carbs_g", "target_fat_g"]
        }
    
    def execute(
        self,
        target_calories: float,
        target_protein_g: float,
        target_carbs_g: float,
        target_fat_g: float,
        num_meals: int = 3,
        preferences: Dict[str, Any] | None = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute daily meal planning.
        
        Args:
            target_calories: Target daily calories
            target_protein_g: Target daily protein
            target_carbs_g: Target daily carbs
            target_fat_g: Target daily fat
            num_meals: Number of meals
            preferences: User preferences
            **kwargs: Additional parameters (ignored)
        
        Returns:
            Dict with meal plan
        """
        # Generate meal plan
        meals = self.planning_service.generate_meal_plan(
            target_calories=target_calories,
            target_protein_g=target_protein_g,
            target_carbs_g=target_carbs_g,
            target_fat_g=target_fat_g,
            num_meals=num_meals,
            preferences=preferences or {}
        )
        
        # Calculate totals
        total_calories = sum(meal.total_calories for meal in meals)
        total_protein = sum(meal.total_protein_g for meal in meals)
        total_carbs = sum(meal.total_carbs_g for meal in meals)
        total_fat = sum(meal.total_fat_g for meal in meals)
        
        # Convert to output schema
        output = MealPlanOutput(
            meals=meals,
            total_calories=total_calories,
            total_protein_g=total_protein,
            total_carbs_g=total_carbs,
            total_fat_g=total_fat,
            notes=f"Plan generated for {num_meals} meals/day"
        )
        
        return output.model_dump()


# Global tool instance
daily_planner_tool = DailyPlannerTool()
