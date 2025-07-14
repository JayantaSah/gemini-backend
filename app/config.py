from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "postgresql://postgres:password@localhost:5432/gemini_backend"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT Configuration
    secret_key: str = "your-super-secret-jwt-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # Google Gemini API
    gemini_api_key: str = ""
    
    # Stripe Configuration
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id: str = ""
    
    # Application Configuration
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Rate Limiting
    basic_daily_limit: int = 5
    pro_daily_limit: int = 1000
    
    class Config:
        env_file = ".env"


settings = Settings()

