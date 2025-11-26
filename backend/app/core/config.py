from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://311_user:311_password@localhost:5432/township_311"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: list = ["http://localhost:5173", "http://localhost:8080"]
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = ["pdf", "jpg", "jpeg", "png", "doc", "docx"]
    
    # ClamAV
    clamav_host: str = "localhost"
    clamav_port: int = 3310
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Email (for notifications)
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()