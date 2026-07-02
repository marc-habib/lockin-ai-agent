"""
Main FastAPI application for LockIn AI.

Entry point for the web server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes import router
from app.database.schema import initialize_database
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    
    Args:
        app: FastAPI application
    """
    # Startup
    print("🚀 Starting LockIn AI...")
    
    # Ensure directories exist
    settings.ensure_directories()
    
    # Initialize database
    print("📊 Initializing database...")
    initialize_database()
    
    print("✅ LockIn AI is ready!")
    print(f"📍 Running on http://{settings.host}:{settings.port}")
    print(f"📚 API docs: http://{settings.host}:{settings.port}/docs")
    
    yield
    
    # Shutdown
    print("👋 Shutting down LockIn AI...")


# Create FastAPI app
app = FastAPI(
    title="LockIn AI",
    description="Agentic Health & Performance Planning System",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.app_env == "development"
    )
