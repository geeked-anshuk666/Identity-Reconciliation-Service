from fastapi import FastAPI
from app.api.routes import router
from app.database import engine
from app.models.contact import Base
import asyncio

app = FastAPI(
    title="Bitespeed Identity Reconciliation Service",
    description="A service that tracks and consolidates customer identities across multiple purchases by linking contact information",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Create tables
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Include routes
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Bitespeed Identity Reconciliation Service"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}