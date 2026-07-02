"""Utilities package for LockIn AI."""

from app.utils.calculations import (
    calculate_bmr,
    calculate_tdee,
    calculate_target_calories,
    calculate_macros,
    calculate_recipe_macros,
    calculate_remaining_macros,
    calculate_calories_from_macros,
)
from app.utils.constants import (
    ACTIVITY_MULTIPLIERS,
    GOAL_CALORIE_ADJUSTMENTS,
    MACRO_DISTRIBUTIONS,
    CALORIES_PER_GRAM,
    MIN_PROTEIN_PER_KG,
    MAX_MESSAGE_LENGTH,
    MAX_REASONING_STEPS,
    DEFAULT_CACHE_EXPIRY_DAYS,
    MEDICAL_KEYWORDS,
    INJECTION_PATTERNS,
    TOOL_TIMEOUT_SECONDS,
    LLM_COSTS,
    CIQUAL_COLUMNS,
)

__all__ = [
    # Calculations
    "calculate_bmr",
    "calculate_tdee",
    "calculate_target_calories",
    "calculate_macros",
    "calculate_recipe_macros",
    "calculate_remaining_macros",
    "calculate_calories_from_macros",
    # Constants
    "ACTIVITY_MULTIPLIERS",
    "GOAL_CALORIE_ADJUSTMENTS",
    "MACRO_DISTRIBUTIONS",
    "CALORIES_PER_GRAM",
    "MIN_PROTEIN_PER_KG",
    "MAX_MESSAGE_LENGTH",
    "MAX_REASONING_STEPS",
    "DEFAULT_CACHE_EXPIRY_DAYS",
    "MEDICAL_KEYWORDS",
    "INJECTION_PATTERNS",
    "TOOL_TIMEOUT_SECONDS",
    "LLM_COSTS",
    "CIQUAL_COLUMNS",
]
