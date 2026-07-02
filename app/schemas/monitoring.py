"""
Monitoring schemas for LockIn AI.

Pydantic models for request logging and monitoring.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from app.models.enums import Intent, RequestStatus


class RequestLog(BaseModel):
    """Schema for logging requests to JSONL."""
    
    request_id: str
    user_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    endpoint: str
    intent: Intent | None = None
    tool_calls: list[str] = Field(default_factory=list)
    reasoning_steps: int = 0
    latency_ms: int
    estimated_tokens: int | None = None
    estimated_cost_usd: float | None = None
    cache_hits: int = 0
    guardrails_triggered: list[str] = Field(default_factory=list)
    error: str | None = None
    status: RequestStatus
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
