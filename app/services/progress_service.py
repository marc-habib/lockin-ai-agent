"""
Progress service for LockIn AI.

Tracks daily nutrition progress and answers progress-related queries.
"""

from datetime import date
from app.repositories.progress_repository import progress_repository
from app.services.profile_service import profile_service
from app.schemas.nutrition import DailyProgress


class ProgressService:
    """Service for daily progress tracking."""
    
    def __init__(self):
        self.repository = progress_repository
        self.profile_service = profile_service
    
    def get_today_progress(self, user_id: str) -> DailyProgress | None:
        """
        Get today's progress for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            DailyProgress or None if profile not found
        """
        today = date.today().isoformat()
        return self.get_progress_for_date(user_id, today)
    
    def get_progress_for_date(self, user_id: str, date_str: str) -> DailyProgress | None:
        """
        Get progress for a specific date.
        
        Args:
            user_id: User identifier
            date_str: Date in YYYY-MM-DD format
        
        Returns:
            DailyProgress or None if profile not found
        """
        # Get profile to get targets
        profile = self.profile_service.get_profile(user_id)
        if not profile:
            return None
        
        # Get or create progress entry
        progress_data = self.repository.get_or_create_daily_progress(
            user_id=user_id,
            date_str=date_str,
            target_calories=profile.target_macros.calories,
            target_protein_g=profile.target_macros.protein_g,
            target_carbs_g=profile.target_macros.carbs_g,
            target_fat_g=profile.target_macros.fat_g
        )
        
        return DailyProgress(
            date=progress_data['date'],
            consumed_calories=progress_data['consumed_calories'],
            consumed_protein_g=progress_data['consumed_protein_g'],
            consumed_carbs_g=progress_data['consumed_carbs_g'],
            consumed_fat_g=progress_data['consumed_fat_g'],
            target_calories=progress_data['target_calories'],
            target_protein_g=progress_data['target_protein_g'],
            target_carbs_g=progress_data['target_carbs_g'],
            target_fat_g=progress_data['target_fat_g']
        )
    
    def get_remaining_macros(self, user_id: str) -> dict | None:
        """
        Get remaining macros for today.
        
        Args:
            user_id: User identifier
        
        Returns:
            Dict with remaining_calories, remaining_protein_g, etc.
        """
        progress = self.get_today_progress(user_id)
        if not progress:
            return None
        
        return {
            'remaining_calories': progress.remaining_calories,
            'remaining_protein_g': progress.remaining_protein_g,
            'remaining_carbs_g': progress.remaining_carbs_g,
            'remaining_fat_g': progress.remaining_fat_g,
        }
    
    def is_on_track(self, user_id: str) -> bool | None:
        """
        Check if user is on track with their nutrition today.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if on track, False if not, None if no data
        """
        progress = self.get_today_progress(user_id)
        if not progress:
            return None
        
        return progress.is_on_track
    
    def update_progress_from_meals(self, user_id: str, date_str: str) -> None:
        """
        Recalculate progress from meal logs.
        
        Args:
            user_id: User identifier
            date_str: Date in YYYY-MM-DD format
        """
        # Calculate consumed macros from meal logs
        consumed = self.repository.calculate_consumed_macros(user_id, date_str)
        
        # Update progress
        self.repository.update_daily_progress(
            user_id=user_id,
            date_str=date_str,
            consumed_calories=consumed['consumed_calories'],
            consumed_protein_g=consumed['consumed_protein_g'],
            consumed_carbs_g=consumed['consumed_carbs_g'],
            consumed_fat_g=consumed['consumed_fat_g']
        )
    
    def get_progress_summary(self, user_id: str) -> dict | None:
        """
        Get a summary of today's progress.
        
        Args:
            user_id: User identifier
        
        Returns:
            Dict with progress summary
        """
        progress = self.get_today_progress(user_id)
        if not progress:
            return None
        
        return {
            'date': progress.date,
            'consumed': {
                'calories': progress.consumed_calories,
                'protein_g': progress.consumed_protein_g,
                'carbs_g': progress.consumed_carbs_g,
                'fat_g': progress.consumed_fat_g,
            },
            'target': {
                'calories': progress.target_calories,
                'protein_g': progress.target_protein_g,
                'carbs_g': progress.target_carbs_g,
                'fat_g': progress.target_fat_g,
            },
            'remaining': {
                'calories': progress.remaining_calories,
                'protein_g': progress.remaining_protein_g,
                'carbs_g': progress.remaining_carbs_g,
                'fat_g': progress.remaining_fat_g,
            },
            'on_track': progress.is_on_track,
            'progress_percentage': round(
                (progress.consumed_calories / progress.target_calories * 100) if progress.target_calories > 0 else 0,
                1
            )
        }


# Global service instance
progress_service = ProgressService()
