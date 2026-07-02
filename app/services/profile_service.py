"""
Profile service for LockIn AI.

Business logic for user profiles including TDEE and macro calculations.
"""

from datetime import datetime
from app.repositories.profile_repository import profile_repository
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse, MacroTargets
from app.utils.calculations import (
    calculate_bmr,
    calculate_tdee,
    calculate_target_calories,
    calculate_macros,
)


class ProfileService:
    """Service for profile management and calculations."""
    
    def __init__(self):
        self.repository = profile_repository
    
    def create_profile(self, profile_data: ProfileCreate) -> ProfileResponse:
        """
        Create a new user profile with calculated targets.
        
        Args:
            profile_data: Profile creation data
        
        Returns:
            Complete profile with calculated BMR, TDEE, and macros
        """
        # Create profile in database
        self.repository.create(profile_data)
        
        # Return complete profile with calculations
        return self.get_profile(profile_data.user_id)
    
    def get_profile(self, user_id: str) -> ProfileResponse | None:
        """
        Get user profile with calculated targets.
        
        Args:
            user_id: User identifier
        
        Returns:
            Complete profile or None if not found
        """
        profile_data = self.repository.get(user_id)
        
        if not profile_data:
            return None
        
        # Calculate BMR
        bmr = calculate_bmr(
            age=profile_data['age'],
            sex=profile_data['sex'],
            height_cm=profile_data['height_cm'],
            weight_kg=profile_data['weight_kg']
        )
        
        # Calculate TDEE
        tdee = calculate_tdee(
            bmr=bmr,
            activity_level=profile_data['activity_level']
        )
        
        # Calculate target calories
        target_calories = calculate_target_calories(
            tdee=tdee,
            goal=profile_data['goal']
        )
        
        # Calculate macros
        macros = calculate_macros(
            target_calories=target_calories,
            goal=profile_data['goal'],
            weight_kg=profile_data['weight_kg']
        )
        
        # Build response
        return ProfileResponse(
            user_id=profile_data['user_id'],
            age=profile_data['age'],
            sex=profile_data['sex'],
            height_cm=profile_data['height_cm'],
            weight_kg=profile_data['weight_kg'],
            goal=profile_data['goal'],
            activity_level=profile_data['activity_level'],
            gym_sessions_per_week=profile_data['gym_sessions_per_week'],
            running_sessions_per_week=profile_data['running_sessions_per_week'],
            allergies=profile_data['allergies'],
            dietary_restrictions=profile_data['dietary_restrictions'],
            disliked_foods=profile_data['disliked_foods'],
            country=profile_data['country'],
            budget_per_day=profile_data['budget_per_day'],
            created_at=datetime.fromisoformat(profile_data['created_at']),
            updated_at=datetime.fromisoformat(profile_data['updated_at']),
            bmr=bmr,
            tdee=tdee,
            target_macros=MacroTargets(
                calories=target_calories,
                protein_g=macros['protein_g'],
                carbs_g=macros['carbs_g'],
                fat_g=macros['fat_g']
            )
        )
    
    def update_profile(self, user_id: str, profile_update: ProfileUpdate) -> ProfileResponse | None:
        """
        Update user profile.
        
        Args:
            user_id: User identifier
            profile_update: Fields to update
        
        Returns:
            Updated profile or None if not found
        """
        if not self.repository.exists(user_id):
            return None
        
        self.repository.update(user_id, profile_update)
        return self.get_profile(user_id)
    
    def delete_profile(self, user_id: str) -> bool:
        """
        Delete user profile.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if deleted, False if not found
        """
        if not self.repository.exists(user_id):
            return False
        
        self.repository.delete(user_id)
        return True
    
    def profile_exists(self, user_id: str) -> bool:
        """
        Check if profile exists.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if exists, False otherwise
        """
        return self.repository.exists(user_id)
    
    def get_missing_fields(self, user_id: str) -> list[str]:
        """
        Get list of missing required profile fields.
        
        Args:
            user_id: User identifier
        
        Returns:
            List of missing field names
        """
        profile_data = self.repository.get(user_id)
        
        if not profile_data:
            return ['user_id', 'age', 'sex', 'height_cm', 'weight_kg', 'goal', 'activity_level']
        
        required_fields = ['age', 'sex', 'height_cm', 'weight_kg', 'goal', 'activity_level']
        missing = []
        
        for field in required_fields:
            if profile_data.get(field) is None:
                missing.append(field)
        
        return missing


# Global service instance
profile_service = ProfileService()
