from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from app.config import settings
from app.database import engine, Base
from app.routers import auth_router, user_router, chatroom_router, subscription_router, webhook_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up Gemini Backend Clone...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
    
    yield
    
    # Shutdown
    print("Shutting down Gemini Backend Clone...")


# Create FastAPI app
app = FastAPI(
    title="Gemini Backend Clone",
    description="A Gemini-style backend system with OTP authentication, chatrooms, and AI conversations",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(chatroom_router)
app.include_router(subscription_router)
app.include_router(webhook_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Gemini Backend Clone API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "details": str(exc) if settings.debug else None
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

