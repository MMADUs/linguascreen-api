from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator, ValidationInfo
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "FastAPI Server"
    PORT: int = 8000
    DEBUG: bool = False

    # Database settings
    DATABASE_URL: str

    # Security settings
    SECRET_KEY: str = "default-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Validators
    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v: Optional[str], info: ValidationInfo) -> str:
        if not v:
            raise ValueError("DATABASE_URL must be set")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


# Initialize settings
settings = Settings()
