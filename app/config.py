from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    database_url: str = ""
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    @property
    def async_database_url(self) -> str:
        """Convert PostgreSQL URL to async format for Render deployment"""
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