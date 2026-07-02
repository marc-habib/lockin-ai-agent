"""
API routes for LockIn AI.

Defines all FastAPI endpoints.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.profile_service import profile_service
from app.agent.handler import run_agent_handler
from app.monitoring.logger import request_logger
from app.models.enums import RequestStatus
from app.schemas.monitoring import RequestLog


router = APIRouter()


@router.get("/")
async def root():
    """Welcome endpoint."""
    return {
        "message": "Welcome to LockIn AI - Agentic Health & Performance Planning System",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "GET /health",
            "onboarding": "POST /onboarding",
            "profile": "GET /profile/{user_id}",
            "update_profile": "PUT /profile/{user_id}",
            "chat": "POST /chat"
        }
    }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected"
    }


@router.post("/onboarding", response_model=ProfileResponse)
async def onboarding(profile_data: ProfileCreate):
    """
    Create a new user profile (onboarding).
    
    Args:
        profile_data: Profile creation data
    
    Returns:
        Complete profile with calculated targets
    """
    try:
        # Check if profile already exists
        if profile_service.profile_exists(profile_data.user_id):
            raise HTTPException(
                status_code=400,
                detail=f"Profile already exists for user_id: {profile_data.user_id}. Use PUT /profile to update."
            )
        
        # Create profile
        profile = profile_service.create_profile(profile_data)
        return profile
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/{user_id}", response_model=ProfileResponse)
async def get_profile(user_id: str):
    """
    Get user profile.
    
    Args:
        user_id: User identifier
    
    Returns:
        Complete profile with calculated targets
    """
    profile = profile_service.get_profile(user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@router.put("/profile/{user_id}", response_model=ProfileResponse)
async def update_profile(user_id: str, profile_update: ProfileUpdate):
    """
    Update user profile.
    
    Args:
        user_id: User identifier
        profile_update: Fields to update
    
    Returns:
        Updated profile with recalculated targets
    """
    profile = profile_service.update_profile(user_id, profile_update)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - invokes the agent handler.
    
    Args:
        request: Chat request with user_id and message
    
    Returns:
        Chat response with agent's answer
    """
    try:
        # Run agent handler
        response = run_agent_handler(
            user_id=request.user_id,
            message=request.message
        )
        
        # Log request
        log_entry = RequestLog(
            request_id=response.request_id,
            user_id=request.user_id,
            timestamp=datetime.utcnow(),
            endpoint="/chat",
            intent=response.intent,
            tool_calls=response.tool_calls or [],
            reasoning_steps=0,  # Could track this in agent_service
            latency_ms=response.latency_ms,
            estimated_tokens=None,  # Could calculate from LLM usage
            estimated_cost_usd=None,  # Could calculate from LLM usage
            cache_hits=0,
            guardrails_triggered=[response.guardrail_triggered] if response.guardrail_triggered else [],
            error=None if response.status == RequestStatus.SUCCESS else response.response,
            status=response.status
        )
        
        request_logger.log(log_entry)
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_statistics():
    """
    Get monitoring statistics.
    
    Returns:
        Aggregate statistics from logs
    """
    return request_logger.get_statistics()
