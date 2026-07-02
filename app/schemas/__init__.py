"""Schemas package for LockIn AI."""

from app.schemas.profile import (
    ProfileCreate,
    ProfileUpdate,
    MacroTargets,
    ProfileResponse,
)
from app.schemas.nutrition import (
    FoodNutrition,
    ProductNutrition,
    RecipeIngredient,
    RecipeMacros,
    DailyProgress,
)
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.schemas.tools import (
    FoodLookupInput,
    FoodLookupOutput,
    ProductLookupInput,
    ProductLookupOutput,
    RecipeMacroInput,
    RecipeMacroOutput,
    MealPlanInput,
    Meal,
    MealPlanOutput,
)
from app.schemas.monitoring import (
    RequestLog,
)

__all__ = [
    # Profile
    "ProfileCreate",
    "ProfileUpdate",
    "MacroTargets",
    "ProfileResponse",
    # Nutrition
    "FoodNutrition",
    "ProductNutrition",
    "RecipeIngredient",
    "RecipeMacros",
    "DailyProgress",
    # Chat
    "ChatRequest",
    "ChatResponse",
    # Tools
    "FoodLookupInput",
    "FoodLookupOutput",
    "ProductLookupInput",
    "ProductLookupOutput",
    "RecipeMacroInput",
    "RecipeMacroOutput",
    "MealPlanInput",
    "Meal",
    "MealPlanOutput",
    # Monitoring
    "RequestLog",
]
