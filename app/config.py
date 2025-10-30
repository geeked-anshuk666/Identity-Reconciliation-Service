from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()