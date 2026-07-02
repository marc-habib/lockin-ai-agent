"""
Profile guardrails for LockIn AI.

Validates profile completeness before allowing agent execution.
"""

from app.services.profile_service import profile_service


class ProfileGuardrails:
    """Profile completeness validation."""
    
    def __init__(self):
        self.profile_service = profile_service
    
    def validate_profile_exists(self, user_id: str) -> tuple[bool, list[str] | None]:
        """
        Validate that a complete profile exists.
        
        Args:
            user_id: User identifier
        
        Returns:
            Tuple of (is_valid, missing_fields)
        """
        # Check if profile exists
        if not self.profile_service.profile_exists(user_id):
            return False, ['user_id', 'age', 'sex', 'height_cm', 'weight_kg', 'goal', 'activity_level']
        
        # Check for missing required fields
        missing_fields = self.profile_service.get_missing_fields(user_id)
        
        if missing_fields:
            return False, missing_fields
        
        return True, None
    
    def get_profile_or_error(self, user_id: str) -> tuple[dict | None, list[str] | None]:
        """
        Get profile or return missing fields.
        
        Args:
            user_id: User identifier
        
        Returns:
            Tuple of (profile, missing_fields)
        """
        is_valid, missing_fields = self.validate_profile_exists(user_id)
        
        if not is_valid:
            return None, missing_fields
        
        profile = self.profile_service.get_profile(user_id)
        return profile, None


# Global instance
profile_guardrails = ProfileGuardrails()
