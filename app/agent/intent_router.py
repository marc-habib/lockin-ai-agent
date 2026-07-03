"""
Intent router for LockIn AI.

Classifies user requests into intents for tool selection.
"""

from app.models.enums import Intent


class IntentRouter:
    """Routes user requests to appropriate intents."""
    
    def classify(self, message: str) -> Intent:
        """
        Classify user message into an intent.
        
        Uses keyword-based classification for simplicity and speed.
        Could be upgraded to use a lightweight LLM classifier if needed.
        
        Args:
            message: User message
        
        Returns:
            Intent enum
        """
        message_lower = message.lower()
        
        # Calorie target / daily target queries
        if any(keyword in message_lower for keyword in [
            "how many calories should i eat",
            "how many calories do i have to eat",
            "how many kcal should i eat",
            "daily calories",
            "target calories",
            "calorie target",
            "maintenance calories",
            "tdee",
            "bmr"
        ]):
            return Intent.PROGRESS

        # Progress queries
        if any(keyword in message_lower for keyword in [
            'remaining', 'left', 'on track', 'progress',
            'consumed', 'eaten', 'logged'
        ]):
            return Intent.PROGRESS
        
        # Meal planning
        if any(keyword in message_lower for keyword in [
            'plan', 'meal plan', 'daily plan', 'today\'s meals',
            'what should i eat', 'meals for'
        ]):
            return Intent.MEAL_PLAN
        
        # Recipe calculation
        if any(keyword in message_lower for keyword in [
            'recipe', 'calculate', 'total macros', 'ingredients',
            'how many calories in'
        ]):
            return Intent.RECIPE
        
        # Product search
        if any(keyword in message_lower for keyword in [
            'product', 'brand', 'branded', 'packaged', 'barcode', 'label',
            'nutriscore', 'nutri-score', 'nova', 'ingredients',
            'manufacturer', 'allergens',
            'nutella', 'danone', 'carrefour', 'monoprix', 'yoplait', 'lidl'
        ]):
            return Intent.PRODUCT_SEARCH
        
        # Food search
        if any(keyword in message_lower for keyword in [
            'nutrition', 'calories', 'protein', 'carbs', 'fat',
            'macros', 'food', 'nutrient'
        ]):
            return Intent.FOOD_SEARCH
        
        # Shopping list
        if any(keyword in message_lower for keyword in [
            'shopping', 'grocery', 'buy', 'purchase', 'list'
        ]):
            return Intent.SHOPPING_LIST
        
        # Workout planning
        if any(keyword in message_lower for keyword in [
            'workout', 'exercise', 'training', 'gym', 'lift', 'run'
        ]):
            return Intent.WORKOUT
        
        # Productivity
        if any(keyword in message_lower for keyword in [
            'productivity', 'schedule', 'work', 'focus', 'time'
        ]):
            return Intent.PRODUCTIVITY
        
        # General fitness
        if any(keyword in message_lower for keyword in [
            'fitness', 'health', 'weight', 'muscle', 'fat loss',
            'goal', 'advice', 'tip'
        ]):
            return Intent.GENERAL_FITNESS
        
        # Default to unknown
        return Intent.UNKNOWN


# Global router instance
intent_router = IntentRouter()
