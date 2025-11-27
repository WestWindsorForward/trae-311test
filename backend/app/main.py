from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
import os

from .core.config import settings
from .core.database import engine, Base
from .api import auth_router, requests_router, admin_router, public_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables on startup
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Create FastAPI app
app = FastAPI(
    title="Township 311 Request Management System",
    description="A comprehensive system for managing citizen service requests",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
os.makedirs("/app/uploads", exist_ok=True)

# Mount static files for attachments
app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")

# Add routers
app.include_router(auth_router, prefix="/api/auth")
app.include_router(requests_router, prefix="/api/requests")
app.include_router(admin_router, prefix="/api")
app.include_router(public_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Township 311 Request Management System...")
    await create_tables()
    logger.info("Database tables created/verified")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Township 311 Request Management System...")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "township-311-api"}

@app.get("/api/health")
async def api_health():
    """Health check endpoint behind Caddy /api proxy"""
    return {"status": "ok", "service": "township-311-api"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Township 311 Request Management System API",
        "version": "1.0.0",
        "docs": "/docs"
    }
