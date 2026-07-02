"""
Get progress tool for LockIn AI.

Retrieves user's daily nutrition progress.
"""

from typing import Any, Dict
from app.tools.base import BaseTool
from app.services.progress_service import progress_service


class GetProgressTool(BaseTool):
    """Tool for getting daily nutrition progress."""
    
    def __init__(self):
        self.progress_service = progress_service
        super().__init__()
    
    def _get_name(self) -> str:
        return "get_progress"
    
    def _get_description(self) -> str:
        return "Get the user's nutrition progress for today. Use this when the user asks about their remaining calories, protein, or whether they're on track. Returns consumed and remaining macros."
    
    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User identifier"
                }
            },
            "required": ["user_id"]
        }
    
    def execute(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """
        Execute progress retrieval.
        
        Args:
            user_id: User identifier
            **kwargs: Additional parameters (ignored)
        
        Returns:
            Dict with progress summary
        """
        # Get progress summary
        summary = self.progress_service.get_progress_summary(user_id)
        
        if not summary:
            return {
                "error": "Profile not found or no progress data available",
                "user_id": user_id
            }
        
        return summary


# Global tool instance
get_progress_tool = GetProgressTool()
