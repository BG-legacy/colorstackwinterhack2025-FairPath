"""
Main FastAPI app - just setting up the basics here
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pathlib import Path
from app.config import settings
from app.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from middleware.rate_limiting import RateLimitingMiddleware
from middleware.size_limiting import SizeLimitingMiddleware
from routes import api_router
from routes.trust import get_trust_panel, get_model_cards
from models.schemas import BaseResponse
import subprocess
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# creating the app instance
app = FastAPI(
    title="FairPath API",
    description="Backend API for FairPath",
    version="1.0.0"
)

# Add security middleware (order matters - added in reverse execution order)
# FastAPI middleware executes in reverse order of addition
app.add_middleware(
    SizeLimitingMiddleware,
    max_request_size=settings.MAX_REQUEST_SIZE,
    max_upload_size=settings.MAX_UPLOAD_SIZE
)

app.add_middleware(
    RateLimitingMiddleware,
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
    requests_per_hour=settings.RATE_LIMIT_PER_HOUR,
    requests_per_day=settings.RATE_LIMIT_PER_DAY
)

# CORS setup - MUST be added LAST so it executes FIRST to handle preflight OPTIONS requests
# I'm allowing all the common localhost ports, you can add more in .env
cors_origins = settings.CORS_ORIGINS
logger.info(f"CORS configured with origins: {cors_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add global exception handlers for safe error responses
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# including the routes
app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler - conditionally preload models and warm caches
    This ensures no first-request lag for models and occupation vectors
    
    Can be disabled via EAGER_LOAD_MODELS=False to save memory in constrained environments
    """
    # Log that server is starting - this helps with deployment monitoring
    import os
    port = os.getenv("PORT", "8000")
    logger.info(f"Server starting on port {port}")
    
    if not settings.EAGER_LOAD_MODELS:
        logger.info("Eager loading disabled (EAGER_LOAD_MODELS=False) - models will load on first request")
        logger.info("This reduces memory usage at startup")
        logger.info("Server ready to accept requests")
        return
    
    logger.info("Starting up - preloading models and warming caches...")
    
    # Preload recommendation service models and warm occupation vectors cache
    try:
        from services.recommendation_service import CareerRecommendationService
        logger.info("Loading recommendation service models...")
        rec_service = CareerRecommendationService()
        rec_service.load_model_artifacts()
        
        if rec_service.ml_model is not None:
            logger.info(f"✓ ML model loaded (version: {rec_service.model_version})")
        else:
            logger.warning("⚠ ML model not found - will use baseline ranking")
        
        # Warm cache: pre-build occupation vectors
        logger.info("Warming occupation vectors cache...")
        rec_service.build_occupation_vectors()
        logger.info(f"✓ Occupation vectors cache warmed ({len(rec_service._occupation_vectors)} vectors)")
        
        # Also warm processed data cache
        rec_service.load_processed_data()
        logger.info("✓ Processed data cache warmed")
        
    except Exception as e:
        logger.error(f"Error preloading recommendation service: {e}")
        # Don't fail startup - service will handle gracefully on first request
    
    # Preload resume service dependencies
    try:
        from services.resume_service import ResumeService
        logger.info("Preloading resume service dependencies...")
        resume_service = ResumeService()
        
        # Warm caches by loading data
        resume_service.load_processed_data()
        resume_service.get_all_skills()
        resume_service.get_catalog()
        logger.info("✓ Resume service caches warmed")
        
    except Exception as e:
        logger.error(f"Error preloading resume service: {e}")
        # Don't fail startup - service will handle gracefully on first request
    
    logger.info("Startup complete - all models and caches ready")


def _get_git_commit() -> str:
    """Get git commit hash, returns 'unknown' if not available"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent.parent
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _check_model_loaded() -> bool:
    """Check if ML model files exist (lightweight check, doesn't load models)"""
    try:
        artifacts_dir = Path(__file__).parent.parent / "artifacts" / "models"
        # Check if model files exist without loading them
        model_file = list(artifacts_dir.glob("career_model_v*.pkl"))
        scaler_file = list(artifacts_dir.glob("scaler_v*.pkl"))
        metadata_file = list(artifacts_dir.glob("model_metadata_v*.json"))
        return len(model_file) > 0 and len(scaler_file) > 0 and len(metadata_file) > 0
    except Exception:
        return False


def _check_data_loaded() -> bool:
    """Check if processed data file exists (lightweight check, doesn't load data)"""
    try:
        processed_data_file = Path(__file__).parent.parent / "artifacts" / "processed_data.json"
        return processed_data_file.exists() and processed_data_file.stat().st_size > 0
    except Exception:
        return False


def _get_dataset_version() -> str:
    """Get dataset version from processed_data.json"""
    try:
        from services.data_processing import DataProcessingService
        service = DataProcessingService()
        processed_data = service.load_processed_data()
        if processed_data:
            return processed_data.get("version", "unknown")
        return "unknown"
    except Exception:
        return "unknown"


def _get_model_version() -> str:
    """Get model version from model metadata"""
    try:
        artifacts_dir = Path(__file__).parent.parent / "artifacts" / "models"
        metadata_files = list(artifacts_dir.glob("model_metadata_v*.json"))
        if not metadata_files:
            return "unknown"
        # Get latest version
        versions = []
        for f in metadata_files:
            version_str = f.stem.replace("model_metadata_v", "")
            versions.append((version_str, f))
        versions.sort(key=lambda x: x[0], reverse=True)
        metadata_path = versions[0][1]
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        return metadata.get("version", "unknown")
    except Exception:
        return "unknown"


@app.get("/")
async def root():
    """Just a health check endpoint"""
    return {"status": "ok", "message": "FairPath API is running"}


@app.get("/health")
async def health():
    """
    Health check endpoint - returns status + model/data loaded flags
    """
    model_loaded = _check_model_loaded()
    data_loaded = _check_data_loaded()
    
    # Overall status is healthy if both model and data are loaded
    status = "healthy" if (model_loaded and data_loaded) else "degraded"
    
    return {
        "status": status,
        "model_loaded": model_loaded,
        "data_loaded": data_loaded
    }


@app.get("/version")
async def version():
    """
    Version endpoint - returns commit/build stamp + dataset version
    """
    commit_hash = _get_git_commit()
    dataset_version = _get_dataset_version()
    model_version = _get_model_version()
    
    return {
        "app_version": app.version,
        "commit": commit_hash,
        "dataset_version": dataset_version,
        "model_version": model_version
    }


@app.get("/trust-panel", response_model=BaseResponse)
async def trust_panel():
    """
    Trust panel endpoint - returns information about data collection, retention, and limitations
    """
    return await get_trust_panel()


@app.get("/model-cards", response_model=BaseResponse)
async def model_cards():
    """
    Model cards endpoint - returns information about datasets, model types, evaluation metrics, and limitations
    """
    return await get_model_cards()


@app.get("/openai/status")
async def openai_status():
    """
    Check OpenAI service availability and configuration
    """
    from services.openai_enhancement import OpenAIEnhancementService
    from app.config import settings
    
    openai_service = OpenAIEnhancementService()
    api_key_set = bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip() and settings.OPENAI_API_KEY != "your_openai_api_key_here")
    api_key_preview = settings.OPENAI_API_KEY[:10] + "..." if api_key_set and len(settings.OPENAI_API_KEY) > 10 else "Not set"
    is_available = openai_service.is_available()
    
    return {
        "openai_available": is_available,
        "api_key_configured": api_key_set,
        "api_key_preview": api_key_preview,
        "model": settings.OPENAI_MODEL,
        "client_initialized": openai_service.client is not None
    }

