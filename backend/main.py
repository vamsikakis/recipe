from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from dotenv import load_dotenv

# Import our modules
from api.recipes import router as recipes_router
from services.database import init_cosmos_db
from services.monitoring import setup_monitoring

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ITC Yippee Recipe Generator API",
    description="AI-Powered Personalized Recipe Generator for ITC Yippee",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup monitoring
setup_monitoring()

# Include routers
app.include_router(recipes_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        await init_cosmos_db()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ITC Yippee Recipe Generator API"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to ITC Yippee AI-Powered Recipe Generator",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 