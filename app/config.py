from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    """Application configuration settings
    
    Loads configuration from environment variables or .env file.
    Uses pydantic-settings for validation and type conversion.
    """
    database_url: str = Field(
        default="",
        description="Database connection string (fallback when DATABASE_URL not set)"
    )
    app_env: str = Field(
        default="development",
        description="Application environment (development, staging, production)"
    )
    debug: bool = Field(
        default=True,
        description="Enable debug mode with detailed logging"
    )
    host: str = Field(
        default="0.0.0.0",
        description="Host address to bind the server to"
    )
    port: int = Field(
        default=8000,
        description="Port number to bind the server to"
    )
    
    @property
    def async_database_url(self) -> str:
        """Get the async database URL for SQLAlchemy
        
        Handles Render deployment by converting PostgreSQL URLs to async format.
        Prioritizes DATABASE_URL environment variable (Render) over database_url setting.
        """
        # Check if DATABASE_URL is provided by Render
        render_database_url = os.environ.get("DATABASE_URL")
        if render_database_url:
            if render_database_url.startswith("postgresql://"):
                return render_database_url.replace("postgresql://", "postgresql+psycopg2://")
            return render_database_url
        
        # Fallback to the database_url setting
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+psycopg2://")
        return self.database_url
    
    class Config:
        env_file = ".env"

settings = Settings()