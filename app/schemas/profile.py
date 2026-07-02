"""
Profile schemas for LockIn AI.

Pydantic models for user profile data validation and serialization.
"""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.models.enums import Sex, Goal, ActivityLevel


class ProfileCreate(BaseModel):
    """Schema for creating a new user profile."""
    
    user_id: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=13, le=120, description="Age in years")
    sex: Sex
    height_cm: float = Field(..., gt=50, lt=300, description="Height in centimeters")
    weight_kg: float = Field(..., gt=20, lt=500, description="Weight in kilograms")
    goal: Goal
    activity_level: ActivityLevel
    gym_sessions_per_week: int = Field(default=0, ge=0, le=14)
    running_sessions_per_week: int = Field(default=0, ge=0, le=14)
    allergies: list[str] = Field(default_factory=list)
    dietary_restrictions: list[str] = Field(default_factory=list)
    disliked_foods: list[str] = Field(default_factory=list)
    country: str | None = None
    budget_per_day: float | None = Field(default=None, ge=0)
    
    @field_validator("allergies", "dietary_restrictions", "disliked_foods")
    @classmethod
    def validate_string_lists(cls, v: list[str]) -> list[str]:
        """Ensure list items are non-empty strings."""
        return [item.strip() for item in v if item.strip()]


class ProfileUpdate(BaseModel):
    """Schema for updating an existing profile."""
    
    age: int | None = Field(default=None, ge=13, le=120)
    sex: Sex | None = None
    height_cm: float | None = Field(default=None, gt=50, lt=300)
    weight_kg: float | None = Field(default=None, gt=20, lt=500)
    goal: Goal | None = None
    activity_level: ActivityLevel | None = None
    gym_sessions_per_week: int | None = Field(default=None, ge=0, le=14)
    running_sessions_per_week: int | None = Field(default=None, ge=0, le=14)
    allergies: list[str] | None = None
    dietary_restrictions: list[str] | None = None
    disliked_foods: list[str] | None = None
    country: str | None = None
    budget_per_day: float | None = Field(default=None, ge=0)


class MacroTargets(BaseModel):
    """Calculated macro targets."""
    
    calories: float = Field(..., description="Target daily calories")
    protein_g: float = Field(..., description="Target protein in grams")
    carbs_g: float = Field(..., description="Target carbohydrates in grams")
    fat_g: float = Field(..., description="Target fat in grams")


class ProfileResponse(BaseModel):
    """Complete profile with calculated targets."""
    
    user_id: str
    age: int
    sex: Sex
    height_cm: float
    weight_kg: float
    goal: Goal
    activity_level: ActivityLevel
    gym_sessions_per_week: int
    running_sessions_per_week: int
    allergies: list[str]
    dietary_restrictions: list[str]
    disliked_foods: list[str]
    country: str | None
    budget_per_day: float | None
    created_at: datetime
    updated_at: datetime
    
    # Calculated fields
    bmr: float = Field(..., description="Basal Metabolic Rate")
    tdee: float = Field(..., description="Total Daily Energy Expenditure")
    target_macros: MacroTargets
    
    class Config:
        from_attributes = True
