"""
Enumerations for LockIn AI.

Defines all enum types used throughout the application for type safety
and validation.
"""

from enum import Enum


class Sex(str, Enum):
    """Biological sex for TDEE calculations."""
    MALE = "male"
    FEMALE = "female"


class Goal(str, Enum):
    """User fitness goal."""
    LOSE_FAT = "lose_fat"
    MAINTAIN = "maintain"
    GAIN_MUSCLE = "gain_muscle"


class ActivityLevel(str, Enum):
    """Physical activity level for TDEE calculation."""
    SEDENTARY = "sedentary"  # Little to no exercise
    LIGHT = "light"  # Light exercise 1-3 days/week
    MODERATE = "moderate"  # Moderate exercise 3-5 days/week
    ACTIVE = "active"  # Heavy exercise 6-7 days/week
    VERY_ACTIVE = "very_active"  # Very heavy exercise, physical job


class Intent(str, Enum):
    """User request intent classification."""
    ONBOARDING = "onboarding"
    PROFILE = "profile"
    FOOD_SEARCH = "food_search"
    PRODUCT_SEARCH = "product_search"
    RECIPE = "recipe"
    MEAL_PLAN = "meal_plan"
    WORKOUT = "workout"
    SHOPPING_LIST = "shopping_list"
    PRODUCTIVITY = "productivity"
    PROGRESS = "progress"
    GENERAL_FITNESS = "general_fitness"
    UNKNOWN = "unknown"


class MealType(str, Enum):
    """Type of meal for logging."""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class RequestStatus(str, Enum):
    """Status of a request."""
    SUCCESS = "success"
    ERROR = "error"
    BLOCKED = "blocked"
    PROFILE_REQUIRED = "profile_required"
