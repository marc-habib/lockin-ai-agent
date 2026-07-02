"""
Progress repository for LockIn AI.

Handles daily progress tracking and meal logging.
"""

from datetime import datetime, date
from app.database.connection import db
from app.models.enums import MealType


class ProgressRepository:
    """Repository for daily progress and meal logging."""
    
    def get_daily_progress(self, user_id: str, date_str: str) -> dict | None:
        """
        Get daily progress for a specific date.
        
        Args:
            user_id: User identifier
            date_str: Date in YYYY-MM-DD format
        
        Returns:
            Progress data as dict or None if not found
        """
        query = """
            SELECT * FROM daily_progress 
            WHERE user_id = ? AND date = ?
        """
        
        row = db.fetchone(query, (user_id, date_str))
        return dict(row) if row else None
    
    def get_or_create_daily_progress(
        self,
        user_id: str,
        date_str: str,
        target_calories: float,
        target_protein_g: float,
        target_carbs_g: float,
        target_fat_g: float
    ) -> dict:
        """
        Get or create daily progress entry.
        
        Args:
            user_id: User identifier
            date_str: Date in YYYY-MM-DD format
            target_calories: Target calories for the day
            target_protein_g: Target protein
            target_carbs_g: Target carbs
            target_fat_g: Target fat
        
        Returns:
            Progress data as dict
        """
        progress = self.get_daily_progress(user_id, date_str)
        
        if progress:
            return progress
        
        # Create new entry
        query = """
            INSERT INTO daily_progress (
                user_id, date, 
                consumed_calories, consumed_protein_g, consumed_carbs_g, consumed_fat_g,
                target_calories, target_protein_g, target_carbs_g, target_fat_g
            ) VALUES (?, ?, 0, 0, 0, 0, ?, ?, ?, ?)
        """
        
        db.execute(query, (
            user_id, date_str,
            target_calories, target_protein_g, target_carbs_g, target_fat_g
        ))
        
        return self.get_daily_progress(user_id, date_str)
    
    def update_daily_progress(
        self,
        user_id: str,
        date_str: str,
        consumed_calories: float,
        consumed_protein_g: float,
        consumed_carbs_g: float,
        consumed_fat_g: float
    ) -> None:
        """
        Update consumed macros for a day.
        
        Args:
            user_id: User identifier
            date_str: Date in YYYY-MM-DD format
            consumed_calories: Total consumed calories
            consumed_protein_g: Total consumed protein
            consumed_carbs_g: Total consumed carbs
            consumed_fat_g: Total consumed fat
        """
        query = """
            UPDATE daily_progress 
            SET consumed_calories = ?,
                consumed_protein_g = ?,
                consumed_carbs_g = ?,
                consumed_fat_g = ?,
                updated_at = ?
            WHERE user_id = ? AND date = ?
        """
        
        db.execute(query, (
            consumed_calories, consumed_protein_g, consumed_carbs_g, consumed_fat_g,
            datetime.utcnow().isoformat(),
            user_id, date_str
        ))
    
    def log_meal(
        self,
        user_id: str,
        date_str: str,
        meal_type: MealType,
        food_name: str,
        quantity_g: float,
        calories: float,
        protein_g: float,
        carbs_g: float,
        fat_g: float
    ) -> None:
        """
        Log a meal.
        
        Args:
            user_id: User identifier
            date_str: Date in YYYY-MM-DD format
            meal_type: Type of meal
            food_name: Name of food
            quantity_g: Quantity in grams
            calories: Calories in this serving
            protein_g: Protein in this serving
            carbs_g: Carbs in this serving
            fat_g: Fat in this serving
        """
        query = """
            INSERT INTO meal_logs (
                user_id, date, meal_type, food_name, quantity_g,
                calories, protein_g, carbs_g, fat_g
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        db.execute(query, (
            user_id, date_str, meal_type.value, food_name, quantity_g,
            calories, protein_g, carbs_g, fat_g
        ))
    
    def get_meals_for_date(self, user_id: str, date_str: str) -> list[dict]:
        """
        Get all meals logged for a specific date.
        
        Args:
            user_id: User identifier
            date_str: Date in YYYY-MM-DD format
        
        Returns:
            List of meal dicts
        """
        query = """
            SELECT * FROM meal_logs 
            WHERE user_id = ? AND date = ?
            ORDER BY logged_at
        """
        
        rows = db.fetchall(query, (user_id, date_str))
        return [dict(row) for row in rows]
    
    def calculate_consumed_macros(self, user_id: str, date_str: str) -> dict:
        """
        Calculate total consumed macros from meal logs.
        
        Args:
            user_id: User identifier
            date_str: Date in YYYY-MM-DD format
        
        Returns:
            Dict with consumed_calories, consumed_protein_g, consumed_carbs_g, consumed_fat_g
        """
        query = """
            SELECT 
                COALESCE(SUM(calories), 0) as consumed_calories,
                COALESCE(SUM(protein_g), 0) as consumed_protein_g,
                COALESCE(SUM(carbs_g), 0) as consumed_carbs_g,
                COALESCE(SUM(fat_g), 0) as consumed_fat_g
            FROM meal_logs
            WHERE user_id = ? AND date = ?
        """
        
        row = db.fetchone(query, (user_id, date_str))
        return dict(row) if row else {
            'consumed_calories': 0,
            'consumed_protein_g': 0,
            'consumed_carbs_g': 0,
            'consumed_fat_g': 0
        }


# Global repository instance
progress_repository = ProgressRepository()
