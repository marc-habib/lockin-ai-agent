"""
Planning service for LockIn AI.

Deterministic meal and workout planning logic.
"""

from typing import List, Dict, Any
from app.clients.ciqual_client import ciqual_client
from app.services.nutrition_service import nutrition_service
from app.schemas.tools import Meal


class PlanningService:
    """Service for meal and workout planning."""
    
    def __init__(self):
        self.ciqual = ciqual_client
        self.nutrition = nutrition_service
    
    def generate_meal_plan(
        self,
        target_calories: float,
        target_protein_g: float,
        target_carbs_g: float,
        target_fat_g: float,
        num_meals: int = 3,
        preferences: Dict[str, List[str]] | None = None
    ) -> List[Meal]:
        """
        Generate a daily meal plan.
        
        Args:
            target_calories: Target daily calories
            target_protein_g: Target daily protein
            target_carbs_g: Target daily carbs
            target_fat_g: Target daily fat
            num_meals: Number of meals to generate
            preferences: User preferences (allergies, restrictions, dislikes)
        
        Returns:
            List of Meal objects
        """
        preferences = preferences or {}
        allergies = preferences.get('allergies', [])
        restrictions = preferences.get('dietary_restrictions', [])
        dislikes = preferences.get('disliked_foods', [])
        
        # Distribute calories across meals
        meal_types = self._get_meal_types(num_meals)
        calorie_distribution = self._distribute_calories(target_calories, num_meals)
        
        meals = []
        
        for i, meal_type in enumerate(meal_types):
            meal_calories = calorie_distribution[i]
            
            # Generate meal based on type
            foods = self._generate_meal_foods(
                meal_type=meal_type,
                target_calories=meal_calories,
                allergies=allergies,
                restrictions=restrictions,
                dislikes=dislikes
            )
            
            # Calculate meal nutrition
            meal_nutrition = self.nutrition.calculate_meal_nutrition(foods)
            
            meals.append(Meal(
                meal_type=meal_type,
                foods=foods,
                total_calories=meal_nutrition['total_calories'],
                total_protein_g=meal_nutrition['total_protein_g'],
                total_carbs_g=meal_nutrition['total_carbs_g'],
                total_fat_g=meal_nutrition['total_fat_g']
            ))
        
        return meals
    
    def _get_meal_types(self, num_meals: int) -> List[str]:
        """Get meal types based on number of meals."""
        if num_meals == 2:
            return ['breakfast', 'dinner']
        elif num_meals == 3:
            return ['breakfast', 'lunch', 'dinner']
        elif num_meals == 4:
            return ['breakfast', 'snack', 'lunch', 'dinner']
        elif num_meals == 5:
            return ['breakfast', 'snack', 'lunch', 'snack', 'dinner']
        else:  # 6+
            return ['breakfast', 'snack', 'lunch', 'snack', 'dinner', 'snack']
    
    def _distribute_calories(self, total_calories: float, num_meals: int) -> List[float]:
        """Distribute calories across meals."""
        if num_meals == 2:
            return [total_calories * 0.4, total_calories * 0.6]
        elif num_meals == 3:
            return [total_calories * 0.3, total_calories * 0.4, total_calories * 0.3]
        elif num_meals == 4:
            return [total_calories * 0.3, total_calories * 0.1, total_calories * 0.35, total_calories * 0.25]
        elif num_meals == 5:
            return [total_calories * 0.25, total_calories * 0.1, total_calories * 0.3, total_calories * 0.1, total_calories * 0.25]
        else:  # 6
            return [total_calories * 0.2, total_calories * 0.1, total_calories * 0.25, total_calories * 0.1, total_calories * 0.25, total_calories * 0.1]
    
    def _generate_meal_foods(
        self,
        meal_type: str,
        target_calories: float,
        allergies: List[str],
        restrictions: List[str],
        dislikes: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate foods for a specific meal.
        
        This is a simplified implementation. A production version would:
        - Use more sophisticated meal templates
        - Consider variety and balance
        - Respect dietary restrictions more thoroughly
        """
        # Simple meal templates
        templates = {
            'breakfast': [
                {'name': 'Oats', 'base_g': 80},
                {'name': 'Banana', 'base_g': 120},
                {'name': 'Greek yogurt', 'base_g': 150},
            ],
            'lunch': [
                {'name': 'Chicken breast', 'base_g': 150},
                {'name': 'Brown rice', 'base_g': 100},
                {'name': 'Broccoli', 'base_g': 150},
            ],
            'dinner': [
                {'name': 'Salmon', 'base_g': 150},
                {'name': 'Sweet potato', 'base_g': 200},
                {'name': 'Spinach', 'base_g': 100},
            ],
            'snack': [
                {'name': 'Almonds', 'base_g': 30},
                {'name': 'Banana', 'base_g': 100},
            ],
        }
        
        template = templates.get(meal_type, templates['snack'])
        foods = []
        
        for item in template:
            # Search for food in CIQUAL
            results = self.ciqual.search(item['name'], limit=1)
            
            if results:
                food_data = results[0]
                
                # Skip if in dislikes
                if any(dislike.lower() in food_data.food_name.lower() for dislike in dislikes):
                    continue
                
                foods.append({
                    'food_name': food_data.food_name,
                    'quantity_g': item['base_g'],
                    'kcal_100g': food_data.kcal_100g,
                    'protein_100g': food_data.protein_100g,
                    'carbs_100g': food_data.carbs_100g,
                    'fat_100g': food_data.fat_100g,
                })
        
        # Scale to match target calories (simplified)
        if foods:
            current_calories = sum(
                f['kcal_100g'] * f['quantity_g'] / 100 for f in foods
            )
            if current_calories > 0:
                scale_factor = target_calories / current_calories
                for food in foods:
                    food['quantity_g'] = round(food['quantity_g'] * scale_factor, 1)
        
        return foods
    
    def generate_shopping_list(
        self,
        meals: List[Meal]
    ) -> Dict[str, float]:
        """
        Generate a shopping list from meals.
        
        Args:
            meals: List of meals
        
        Returns:
            Dict mapping food names to total quantities in grams
        """
        shopping_list = {}
        
        for meal in meals:
            for food in meal.foods:
                food_name = food['food_name']
                quantity = food['quantity_g']
                
                if food_name in shopping_list:
                    shopping_list[food_name] += quantity
                else:
                    shopping_list[food_name] = quantity
        
        return shopping_list


# Global service instance
planning_service = PlanningService()
