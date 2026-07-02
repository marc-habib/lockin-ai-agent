"""
Nutrition service for LockIn AI.

Deterministic nutrition calculations - no LLM involvement.
"""

from app.schemas.nutrition import RecipeIngredient, RecipeMacros
from app.utils.calculations import calculate_recipe_macros, calculate_calories_from_macros


class NutritionService:
    """Service for nutrition calculations."""
    
    def calculate_recipe_nutrition(
        self,
        recipe_name: str | None,
        ingredients: list[RecipeIngredient]
    ) -> RecipeMacros:
        """
        Calculate total nutrition for a recipe.
        
        Args:
            recipe_name: Name of the recipe
            ingredients: List of ingredients with nutrition data
        
        Returns:
            RecipeMacros with total nutrition
        """
        # Convert to dict format for calculation
        ingredients_data = [
            {
                'quantity_g': ing.quantity_g,
                'kcal_100g': ing.kcal_100g,
                'protein_100g': ing.protein_100g,
                'carbs_100g': ing.carbs_100g,
                'fat_100g': ing.fat_100g,
            }
            for ing in ingredients
        ]
        
        # Calculate totals
        totals = calculate_recipe_macros(ingredients_data)
        
        return RecipeMacros(
            recipe_name=recipe_name,
            total_calories=totals['total_calories'],
            total_protein_g=totals['total_protein_g'],
            total_carbs_g=totals['total_carbs_g'],
            total_fat_g=totals['total_fat_g'],
            ingredients=ingredients
        )
    
    def calculate_meal_nutrition(
        self,
        foods: list[dict]
    ) -> dict:
        """
        Calculate nutrition for a meal from multiple foods.
        
        Args:
            foods: List of dicts with food_name, quantity_g, and nutrition per 100g
        
        Returns:
            Dict with total_calories, total_protein_g, total_carbs_g, total_fat_g
        """
        total_calories = 0.0
        total_protein = 0.0
        total_carbs = 0.0
        total_fat = 0.0
        
        for food in foods:
            quantity_g = food['quantity_g']
            factor = quantity_g / 100.0
            
            total_calories += food.get('kcal_100g', 0) * factor
            total_protein += food.get('protein_100g', 0) * factor
            total_carbs += food.get('carbs_100g', 0) * factor
            total_fat += food.get('fat_100g', 0) * factor
        
        return {
            'total_calories': round(total_calories, 1),
            'total_protein_g': round(total_protein, 1),
            'total_carbs_g': round(total_carbs, 1),
            'total_fat_g': round(total_fat, 1),
        }
    
    def scale_recipe(
        self,
        recipe: RecipeMacros,
        target_calories: float
    ) -> RecipeMacros:
        """
        Scale a recipe to match target calories.
        
        Args:
            recipe: Original recipe
            target_calories: Target calories
        
        Returns:
            Scaled recipe
        """
        if recipe.total_calories == 0:
            return recipe
        
        scale_factor = target_calories / recipe.total_calories
        
        # Scale ingredients
        scaled_ingredients = [
            RecipeIngredient(
                food_name=ing.food_name,
                quantity_g=ing.quantity_g * scale_factor,
                kcal_100g=ing.kcal_100g,
                protein_100g=ing.protein_100g,
                carbs_100g=ing.carbs_100g,
                fat_100g=ing.fat_100g,
            )
            for ing in recipe.ingredients
        ]
        
        return RecipeMacros(
            recipe_name=recipe.recipe_name,
            total_calories=round(recipe.total_calories * scale_factor, 1),
            total_protein_g=round(recipe.total_protein_g * scale_factor, 1),
            total_carbs_g=round(recipe.total_carbs_g * scale_factor, 1),
            total_fat_g=round(recipe.total_fat_g * scale_factor, 1),
            ingredients=scaled_ingredients
        )
    
    def calculate_portion_nutrition(
        self,
        kcal_100g: float,
        protein_100g: float,
        carbs_100g: float,
        fat_100g: float,
        quantity_g: float
    ) -> dict:
        """
        Calculate nutrition for a specific portion.
        
        Args:
            kcal_100g: Calories per 100g
            protein_100g: Protein per 100g
            carbs_100g: Carbs per 100g
            fat_100g: Fat per 100g
            quantity_g: Portion size in grams
        
        Returns:
            Dict with calories, protein_g, carbs_g, fat_g for the portion
        """
        factor = quantity_g / 100.0
        
        return {
            'calories': round(kcal_100g * factor, 1),
            'protein_g': round(protein_100g * factor, 1),
            'carbs_g': round(carbs_100g * factor, 1),
            'fat_g': round(fat_100g * factor, 1),
        }


# Global service instance
nutrition_service = NutritionService()
