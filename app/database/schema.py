"""
Database schema initialization for LockIn AI.

Creates all necessary tables for profiles, cache, and progress tracking.
"""

from app.database.connection import db


def initialize_database() -> None:
    """Create all database tables if they don't exist."""
    
    with db.get_connection() as conn:
        # User profiles table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                user_id TEXT PRIMARY KEY,
                age INTEGER NOT NULL,
                sex TEXT NOT NULL CHECK(sex IN ('male', 'female')),
                height_cm REAL NOT NULL,
                weight_kg REAL NOT NULL,
                goal TEXT NOT NULL CHECK(goal IN ('lose_fat', 'maintain', 'gain_muscle')),
                activity_level TEXT NOT NULL CHECK(
                    activity_level IN ('sedentary', 'light', 'moderate', 'active', 'very_active')
                ),
                gym_sessions_per_week INTEGER DEFAULT 0,
                running_sessions_per_week INTEGER DEFAULT 0,
                allergies TEXT,
                dietary_restrictions TEXT,
                disliked_foods TEXT,
                country TEXT,
                budget_per_day REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # API response cache table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS api_cache (
                cache_key TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                query TEXT NOT NULL,
                response_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_api_cache_source 
            ON api_cache(source)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_api_cache_expires 
            ON api_cache(expires_at)
        """)
        
        # Daily progress tracking table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                date DATE NOT NULL,
                consumed_calories REAL DEFAULT 0,
                consumed_protein_g REAL DEFAULT 0,
                consumed_carbs_g REAL DEFAULT 0,
                consumed_fat_g REAL DEFAULT 0,
                target_calories REAL NOT NULL,
                target_protein_g REAL NOT NULL,
                target_carbs_g REAL NOT NULL,
                target_fat_g REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES profiles(user_id),
                UNIQUE(user_id, date)
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_daily_progress_user_date 
            ON daily_progress(user_id, date)
        """)
        
        # Meal logs table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meal_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                date DATE NOT NULL,
                meal_type TEXT NOT NULL CHECK(
                    meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')
                ),
                food_name TEXT NOT NULL,
                quantity_g REAL NOT NULL,
                calories REAL NOT NULL,
                protein_g REAL NOT NULL,
                carbs_g REAL NOT NULL,
                fat_g REAL NOT NULL,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES profiles(user_id)
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_meal_logs_user_date 
            ON meal_logs(user_id, date)
        """)
        
        conn.commit()


def drop_all_tables() -> None:
    """Drop all tables. Use with caution - for testing only."""
    
    with db.get_connection() as conn:
        conn.execute("DROP TABLE IF EXISTS meal_logs")
        conn.execute("DROP TABLE IF EXISTS daily_progress")
        conn.execute("DROP TABLE IF EXISTS api_cache")
        conn.execute("DROP TABLE IF EXISTS profiles")
        conn.commit()


if __name__ == "__main__":
    # Initialize database when run directly
    initialize_database()
    print("Database initialized successfully")
