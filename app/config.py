from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    database_url: str
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    @property
    def async_database_url(self) -> str:
        """Convert PostgreSQL URL to asyncpg format for Render deployment"""
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        return self.database_url
    
    class Config:
        env_file = ".env"

settings = Settings()