import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .api import adaptive, analytics, documents, export, prompts, research, runs, stats, validation
from .core.config import settings
from .db.connection import close_mongo_connection, connect_to_mongo
from .utils.token_meter import CostCalculator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting CyberCQBench API...")

    # Initialize database
    await connect_to_mongo()

    # Initialize cost calculator
    global cost_calculator
    pricing_config = settings.get_pricing()
    cost_calculator = CostCalculator(pricing_config)

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await close_mongo_connection()


# Create FastAPI application
app = FastAPI(
    title="CyberCQBench API",
    description="Research-grade evaluation platform for SOC/GRC LLM performance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173"   # Vite dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(runs.router)
app.include_router(prompts.router)
app.include_router(analytics.router)
app.include_router(stats.router)
app.include_router(research.router)
app.include_router(documents.router)
app.include_router(adaptive.router)
app.include_router(export.router)
app.include_router(validation.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CyberCQBench API",
        "version": "1.0.0",
        "environment": settings.app_env,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        from .db.connection import database

        # Test database connection
        await database.db.command("ping")

        return {
            "status": "healthy",
            "database": "connected",
            "environment": settings.app_env,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/pricing")
async def get_pricing():
    """Get current pricing configuration"""
    try:
        pricing = settings.get_pricing()
        return {
            "pricing": pricing,
            "note": "Prices in AUD per 1K tokens",
        }
    except Exception as e:
        logger.error(f"Error getting pricing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
