from fastapi import FastAPI
from app.api.routes import router
from app.database import engine
from app.models.contact import Base
from datetime import datetime
import asyncio

app = FastAPI(
    title="Bitespeed Identity Reconciliation Service",
    description="A service that tracks and consolidates customer identities across multiple purchases by linking contact information",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Bitespeed Engineering Team",
        "url": "https://bitespeed.com",
        "email": "engineering@bitespeed.com",
    },
)

# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    """Create database tables if they don't exist"""
    async with engine.begin() as database_connection:
        await database_connection.run_sync(Base.metadata.create_all)

# Mount API routes under /api prefix
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint providing service information"""
    service_info = {
        "message": "Bitespeed Identity Reconciliation Service", 
        "version": "1.0.0"
    }
    return service_info

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and deployment verification"""
    health_status = {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat()
    }
    return health_status