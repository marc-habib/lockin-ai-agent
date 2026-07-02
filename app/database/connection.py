"""
SQLite database connection management.

Provides a simple connection manager for SQLite database operations.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Generator
from app.config import settings


class DatabaseConnection:
    """SQLite database connection manager."""
    
    def __init__(self, db_path: str | None = None):
        """
        Initialize database connection manager.
        
        Args:
            db_path: Path to SQLite database file. Uses settings default if None.
        """
        self.db_path = db_path or settings.database_path
        self._ensure_db_directory()
    
    def _ensure_db_directory(self) -> None:
        """Create database directory if it doesn't exist."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Get a database connection as a context manager.
        
        Yields:
            SQLite connection with row factory enabled
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def execute(self, query: str, params: tuple = ()) -> None:
        """
        Execute a single query (INSERT, UPDATE, DELETE).
        
        Args:
            query: SQL query string
            params: Query parameters
        """
        with self.get_connection() as conn:
            conn.execute(query, params)
    
    def fetchone(self, query: str, params: tuple = ()) -> sqlite3.Row | None:
        """
        Fetch a single row.
        
        Args:
            query: SQL query string
            params: Query parameters
        
        Returns:
            Single row or None
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchone()
    
    def fetchall(self, query: str, params: tuple = ()) -> list[sqlite3.Row]:
        """
        Fetch all rows.
        
        Args:
            query: SQL query string
            params: Query parameters
        
        Returns:
            List of rows
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()


# Global database connection instance
db = DatabaseConnection()
