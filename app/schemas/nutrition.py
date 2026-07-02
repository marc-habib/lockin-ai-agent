"""
Nutrition schemas for LockIn AI.

Pydantic models for nutrition data from CIQUAL and OpenFoodFacts.
"""

from pydantic import BaseModel, Field


class FoodNutrition(BaseModel):
    """Nutrition data for a food item (per 100g)."""
    
    food_name: str
    category: str | None = None
    kcal_100g: float = Field(..., ge=0, description="Calories per 100g")
    protein_100g: float = Field(..., ge=0, description="Protein per 100g")
    carbs_100g: float = Field(..., ge=0, description="Carbohydrates per 100g")
    fat_100g: float = Field(..., ge=0, description="Fat per 100g")
    fiber_100g: float | None = Field(default=None, ge=0, description="Fiber per 100g")
    sugars_100g: float | None = Field(default=None, ge=0, description="Sugars per 100g")
    source: str = Field(..., description="Data source (ciqual or openfoodfacts)")


class ProductNutrition(BaseModel):
    """Nutrition data for a packaged product from OpenFoodFacts."""
    
    product_name: str
    brand: str | None = None
    kcal_100g: float = Field(..., ge=0)
    protein_100g: float = Field(..., ge=0)
    carbs_100g: float = Field(..., ge=0)
    fat_100g: float = Field(..., ge=0)
    fiber_100g: float | None = Field(default=None, ge=0)
    sugars_100g: float | None = Field(default=None, ge=0)
    ingredients: list[str] = Field(default_factory=list)
    allergens: list[str] = Field(default_factory=list)
    nutriscore: str | None = Field(default=None, description="Nutri-Score grade (A-E)")
    nova_group: int | None = Field(default=None, ge=1, le=4, description="NOVA group (1-4)")
    source: str = "openfoodfacts"


class RecipeIngredient(BaseModel):
    """Ingredient for recipe calculation."""
    
    food_name: str
    quantity_g: float = Field(..., gt=0, description="Quantity in grams")
    kcal_100g: float = Field(..., ge=0)
    protein_100g: float = Field(..., ge=0)
    carbs_100g: float = Field(..., ge=0)
    fat_100g: float = Field(..., ge=0)


class RecipeMacros(BaseModel):
    """Calculated macros for a complete recipe."""
    
    recipe_name: str | None = None
    total_calories: float = Field(..., ge=0)
    total_protein_g: float = Field(..., ge=0)
    total_carbs_g: float = Field(..., ge=0)
    total_fat_g: float = Field(..., ge=0)
    ingredients: list[RecipeIngredient]


class DailyProgress(BaseModel):
    """Daily nutrition progress tracking."""
    
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    consumed_calories: float = Field(default=0, ge=0)
    consumed_protein_g: float = Field(default=0, ge=0)
    consumed_carbs_g: float = Field(default=0, ge=0)
    consumed_fat_g: float = Field(default=0, ge=0)
    target_calories: float = Field(..., ge=0)
    target_protein_g: float = Field(..., ge=0)
    target_carbs_g: float = Field(..., ge=0)
    target_fat_g: float = Field(..., ge=0)
    
    @property
    def remaining_calories(self) -> float:
        """Calculate remaining calories."""
        return max(0, self.target_calories - self.consumed_calories)
    
    @property
    def remaining_protein_g(self) -> float:
        """Calculate remaining protein."""
        return max(0, self.target_protein_g - self.consumed_protein_g)
    
    @property
    def remaining_carbs_g(self) -> float:
        """Calculate remaining carbs."""
        return max(0, self.target_carbs_g - self.consumed_carbs_g)
    
    @property
    def remaining_fat_g(self) -> float:
        """Calculate remaining fat."""
        return max(0, self.target_fat_g - self.consumed_fat_g)
    
    @property
    def is_on_track(self) -> bool:
        """Check if user is on track with their targets."""
        # Allow 10% variance
        tolerance = 0.10
        calorie_ratio = self.consumed_calories / self.target_calories if self.target_calories > 0 else 0
        return (1 - tolerance) <= calorie_ratio <= (1 + tolerance)
