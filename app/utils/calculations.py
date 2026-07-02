"""
Deterministic calculations for nutrition and fitness.

All calculations are pure Python functions with no LLM involvement.
Based on established formulas from nutritional science.
"""

from app.models.enums import Sex, Goal, ActivityLevel
from app.utils.constants import (
    ACTIVITY_MULTIPLIERS,
    GOAL_CALORIE_ADJUSTMENTS,
    MACRO_DISTRIBUTIONS,
    CALORIES_PER_GRAM,
    MIN_PROTEIN_PER_KG,
)


def calculate_bmr(age: int, sex: Sex, height_cm: float, weight_kg: float) -> float:
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor equation.
    
    This is the most accurate formula for BMR calculation.
    
    Args:
        age: Age in years
        sex: Biological sex (male/female)
        height_cm: Height in centimeters
        weight_kg: Weight in kilograms
    
    Returns:
        BMR in calories per day
    """
    if sex == Sex.MALE:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:  # Female
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    
    return round(bmr, 1)


def calculate_tdee(bmr: float, activity_level: ActivityLevel) -> float:
    """
    Calculate Total Daily Energy Expenditure.
    
    Args:
        bmr: Basal Metabolic Rate
        activity_level: Physical activity level
    
    Returns:
        TDEE in calories per day
    """
    multiplier = ACTIVITY_MULTIPLIERS[activity_level]
    tdee = bmr * multiplier
    return round(tdee, 1)


def calculate_target_calories(tdee: float, goal: Goal) -> float:
    """
    Calculate target daily calories based on goal.
    
    Args:
        tdee: Total Daily Energy Expenditure
        goal: Fitness goal (lose_fat, maintain, gain_muscle)
    
    Returns:
        Target calories per day
    """
    adjustment = GOAL_CALORIE_ADJUSTMENTS[goal]
    target = tdee + adjustment
    return round(target, 1)


def calculate_macros(
    target_calories: float,
    goal: Goal,
    weight_kg: float
) -> dict[str, float]:
    """
    Calculate target macronutrients based on goal and body weight.
    
    Args:
        target_calories: Target daily calories
        goal: Fitness goal
        weight_kg: Body weight in kg
    
    Returns:
        Dictionary with protein_g, carbs_g, fat_g
    """
    distribution = MACRO_DISTRIBUTIONS[goal]
    
    # Calculate protein (ensure minimum intake)
    protein_calories = target_calories * distribution["protein_pct"]
    protein_g = protein_calories / CALORIES_PER_GRAM["protein"]
    
    # Ensure minimum protein based on body weight
    min_protein = weight_kg * MIN_PROTEIN_PER_KG[goal]
    protein_g = max(protein_g, min_protein)
    
    # Recalculate remaining calories after protein
    protein_calories_actual = protein_g * CALORIES_PER_GRAM["protein"]
    remaining_calories = target_calories - protein_calories_actual
    
    # Calculate fat
    fat_pct_of_remaining = distribution["fat_pct"] / (distribution["fat_pct"] + distribution["carbs_pct"])
    fat_calories = remaining_calories * fat_pct_of_remaining
    fat_g = fat_calories / CALORIES_PER_GRAM["fat"]
    
    # Calculate carbs (remaining calories)
    carbs_calories = remaining_calories - fat_calories
    carbs_g = carbs_calories / CALORIES_PER_GRAM["carbs"]
    
    return {
        "protein_g": round(protein_g, 1),
        "carbs_g": round(carbs_g, 1),
        "fat_g": round(fat_g, 1),
    }


def calculate_recipe_macros(
    ingredients: list[dict[str, float]]
) -> dict[str, float]:
    """
    Calculate total macros for a recipe.
    
    Args:
        ingredients: List of dicts with keys:
            - kcal_100g, protein_100g, carbs_100g, fat_100g, quantity_g
    
    Returns:
        Dictionary with total_calories, total_protein_g, total_carbs_g, total_fat_g
    """
    total_calories = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0
    
    for ingredient in ingredients:
        quantity_g = ingredient["quantity_g"]
        factor = quantity_g / 100.0
        
        total_calories += ingredient.get("kcal_100g", 0) * factor
        total_protein += ingredient.get("protein_100g", 0) * factor
        total_carbs += ingredient.get("carbs_100g", 0) * factor
        total_fat += ingredient.get("fat_100g", 0) * factor
    
    return {
        "total_calories": round(total_calories, 1),
        "total_protein_g": round(total_protein, 1),
        "total_carbs_g": round(total_carbs, 1),
        "total_fat_g": round(total_fat, 1),
    }


def calculate_remaining_macros(
    target_macros: dict[str, float],
    consumed_macros: dict[str, float]
) -> dict[str, float]:
    """
    Calculate remaining macros for the day.
    
    Args:
        target_macros: Target macros (protein_g, carbs_g, fat_g)
        consumed_macros: Already consumed macros
    
    Returns:
        Dictionary with remaining_protein_g, remaining_carbs_g, remaining_fat_g
    """
    return {
        "remaining_protein_g": round(
            target_macros["protein_g"] - consumed_macros.get("protein_g", 0), 1
        ),
        "remaining_carbs_g": round(
            target_macros["carbs_g"] - consumed_macros.get("carbs_g", 0), 1
        ),
        "remaining_fat_g": round(
            target_macros["fat_g"] - consumed_macros.get("fat_g", 0), 1
        ),
    }


def calculate_calories_from_macros(
    protein_g: float,
    carbs_g: float,
    fat_g: float
) -> float:
    """
    Calculate total calories from macronutrients.
    
    Args:
        protein_g: Protein in grams
        carbs_g: Carbohydrates in grams
        fat_g: Fat in grams
    
    Returns:
        Total calories
    """
    calories = (
        protein_g * CALORIES_PER_GRAM["protein"] +
        carbs_g * CALORIES_PER_GRAM["carbs"] +
        fat_g * CALORIES_PER_GRAM["fat"]
    )
    return round(calories, 1)
