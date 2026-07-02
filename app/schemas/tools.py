"""
Tool schemas for LockIn AI.

Pydantic models for tool inputs and outputs.
"""

from pydantic import BaseModel, Field
from app.schemas.nutrition import FoodNutrition, ProductNutrition, RecipeMacros


class FoodLookupInput(BaseModel):
    """Input schema for food_lookup tool."""
    
    query: str = Field(..., min_length=1, description="Food name to search for")
    limit: int = Field(default=5, ge=1, le=20, description="Maximum number of results")


class FoodLookupOutput(BaseModel):
    """Output schema for food_lookup tool."""
    
    results: list[FoodNutrition]
    query: str
    source: str = "ciqual"


class ProductLookupInput(BaseModel):
    """Input schema for product_lookup tool."""
    
    query: str = Field(..., min_length=1, description="Product name or barcode")
    limit: int = Field(default=5, ge=1, le=20)


class ProductLookupOutput(BaseModel):
    """Output schema for product_lookup tool."""
    
    results: list[ProductNutrition]
    query: str
    source: str = "openfoodfacts"


class RecipeMacroInput(BaseModel):
    """Input schema for recipe_macro tool."""
    
    recipe_name: str | None = None
    ingredients: list[dict[str, float]] = Field(
        ...,
        description="List of ingredients with food_name, quantity_g, and nutrition per 100g"
    )


class RecipeMacroOutput(BaseModel):
    """Output schema for recipe_macro tool."""
    
    recipe_macros: RecipeMacros


class MealPlanInput(BaseModel):
    """Input schema for daily_planner tool (meal planning)."""
    
    target_calories: float = Field(..., gt=0)
    target_protein_g: float = Field(..., gt=0)
    target_carbs_g: float = Field(..., gt=0)
    target_fat_g: float = Field(..., gt=0)
    preferences: dict[str, list[str]] = Field(
        default_factory=dict,
        description="User preferences (allergies, restrictions, dislikes)"
    )
    num_meals: int = Field(default=3, ge=2, le=6, description="Number of meals per day")


class Meal(BaseModel):
    """A single meal in a meal plan."""
    
    meal_type: str = Field(..., description="breakfast, lunch, dinner, snack")
    foods: list[dict[str, Any]] = Field(..., description="List of foods with quantities")
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float


class MealPlanOutput(BaseModel):
    """Output schema for daily_planner tool (meal planning)."""
    
    meals: list[Meal]
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    notes: str | None = None


from typing import Any
