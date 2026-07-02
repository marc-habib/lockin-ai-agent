"""
Profile repository for LockIn AI.

Handles all database operations for user profiles.
"""

import json
from datetime import datetime
from app.database.connection import db
from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.models.enums import Sex, Goal, ActivityLevel


class ProfileRepository:
    """Repository for user profile database operations."""
    
    def create(self, profile: ProfileCreate) -> None:
        """
        Create a new user profile.
        
        Args:
            profile: Profile data to create
        """
        query = """
            INSERT INTO profiles (
                user_id, age, sex, height_cm, weight_kg, goal, activity_level,
                gym_sessions_per_week, running_sessions_per_week,
                allergies, dietary_restrictions, disliked_foods,
                country, budget_per_day
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            profile.user_id,
            profile.age,
            profile.sex.value,
            profile.height_cm,
            profile.weight_kg,
            profile.goal.value,
            profile.activity_level.value,
            profile.gym_sessions_per_week,
            profile.running_sessions_per_week,
            json.dumps(profile.allergies),
            json.dumps(profile.dietary_restrictions),
            json.dumps(profile.disliked_foods),
            profile.country,
            profile.budget_per_day,
        )
        
        db.execute(query, params)
    
    def get(self, user_id: str) -> dict | None:
        """
        Get a user profile by ID.
        
        Args:
            user_id: User identifier
        
        Returns:
            Profile data as dict or None if not found
        """
        query = "SELECT * FROM profiles WHERE user_id = ?"
        row = db.fetchone(query, (user_id,))
        
        if not row:
            return None
        
        return self._row_to_dict(row)
    
    def update(self, user_id: str, profile_update: ProfileUpdate) -> None:
        """
        Update an existing user profile.
        
        Args:
            user_id: User identifier
            profile_update: Fields to update
        """
        # Build dynamic update query based on provided fields
        update_fields = []
        params = []
        
        for field, value in profile_update.model_dump(exclude_unset=True).items():
            if value is not None:
                # Handle enum values
                if isinstance(value, (Sex, Goal, ActivityLevel)):
                    value = value.value
                # Handle list fields
                elif isinstance(value, list):
                    value = json.dumps(value)
                
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        if not update_fields:
            return  # Nothing to update
        
        # Add updated_at timestamp
        update_fields.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())
        
        # Add user_id for WHERE clause
        params.append(user_id)
        
        query = f"""
            UPDATE profiles 
            SET {', '.join(update_fields)}
            WHERE user_id = ?
        """
        
        db.execute(query, tuple(params))
    
    def delete(self, user_id: str) -> None:
        """
        Delete a user profile.
        
        Args:
            user_id: User identifier
        """
        query = "DELETE FROM profiles WHERE user_id = ?"
        db.execute(query, (user_id,))
    
    def exists(self, user_id: str) -> bool:
        """
        Check if a profile exists.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if profile exists, False otherwise
        """
        query = "SELECT 1 FROM profiles WHERE user_id = ? LIMIT 1"
        row = db.fetchone(query, (user_id,))
        return row is not None
    
    def _row_to_dict(self, row) -> dict:
        """
        Convert a database row to a dictionary.
        
        Args:
            row: SQLite row object
        
        Returns:
            Dictionary with profile data
        """
        data = dict(row)
        
        # Parse JSON fields
        data['allergies'] = json.loads(data['allergies']) if data['allergies'] else []
        data['dietary_restrictions'] = json.loads(data['dietary_restrictions']) if data['dietary_restrictions'] else []
        data['disliked_foods'] = json.loads(data['disliked_foods']) if data['disliked_foods'] else []
        
        # Convert string enums back to enum types
        data['sex'] = Sex(data['sex'])
        data['goal'] = Goal(data['goal'])
        data['activity_level'] = ActivityLevel(data['activity_level'])
        
        return data


# Global repository instance
profile_repository = ProfileRepository()
