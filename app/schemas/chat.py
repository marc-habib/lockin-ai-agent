"""
Chat schemas for LockIn AI.

Pydantic models for chat requests and responses.
"""

from typing import Any
from pydantic import BaseModel, Field
from app.models.enums import RequestStatus, Intent


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    
    user_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=2000)
    context: dict[str, Any] | None = Field(default=None, description="Optional additional context")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    
    request_id: str
    status: RequestStatus
    intent: Intent | None = None
    response: str | None = None
    data: dict[str, Any] | None = Field(default=None, description="Structured data (meal plan, etc.)")
    missing_fields: list[str] | None = Field(default=None, description="Missing profile fields")
    guardrail_triggered: str | None = Field(default=None, description="Guardrail that blocked request")
    latency_ms: int
    tool_calls: list[str] | None = Field(default=None, description="Tools that were called")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_abc123",
                "status": "success",
                "intent": "meal_plan",
                "response": "Here's your personalized meal plan for today...",
                "data": {
                    "meals": [
                        {"type": "breakfast", "foods": ["oatmeal", "banana"]},
                        {"type": "lunch", "foods": ["chicken", "rice", "broccoli"]},
                    ]
                },
                "latency_ms": 1250,
                "tool_calls": ["food_lookup", "daily_planner"]
            }
        }
