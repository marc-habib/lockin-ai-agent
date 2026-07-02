"""
FastAPI dependencies for LockIn AI.

Provides dependency injection for routes.
"""

from fastapi import Header, HTTPException


async def verify_api_key(x_api_key: str = Header(None)) -> str | None:
    """
    Verify API key (optional - for future use).
    
    Args:
        x_api_key: API key from header
    
    Returns:
        API key if valid, None if not required
    """
    # For now, API key is optional
    # In production, you would validate against a database
    return x_api_key


def get_user_id_from_request(user_id: str) -> str:
    """
    Validate and return user ID.
    
    Args:
        user_id: User identifier from request
    
    Returns:
        Validated user ID
    
    Raises:
        HTTPException: If user_id is invalid
    """
    if not user_id or not user_id.strip():
        raise HTTPException(status_code=400, detail="user_id is required")
    
    return user_id.strip()
