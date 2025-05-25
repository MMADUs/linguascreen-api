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

    # Azure credential settings

    # text-translation credentials
    # AZURE_TEXT_TRANSLATION_ENDPOINT: Optional[str]
    AZURE_TEXT_TRANSLATION_API_KEY: str
    AZURE_TEXT_TRANSLATION_REGION: str = "southeastasia"

    # image-analysis credentials
    AZURE_IMAGE_ANALYSIS_ENDPOINT: str
    AZURE_IMAGE_ANALYSIS_API_KEY: str

    # azure-llm-openai
    AZURE_LLM_OPENAI_API_VERSION: str = "2024-10-21"
    AZURE_LLM_OPENAI_API_KEY: str
    AZURE_LLM_OPENAI_ENDPOINT: str

    # Validators
    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v: Optional[str], info: ValidationInfo) -> str:
        if not v:
            raise ValueError("DATABASE_URL must be set")
        return v

    @field_validator("AZURE_TEXT_TRANSLATION_API_KEY")
    def validate_translation_credential(
        cls, v: Optional[str], info: ValidationInfo
    ) -> str:
        if not v:
            raise ValueError("Azure text-translation api-key must be set")
        return v

    # @model_validator(mode="after")
    # def validate_ocr_credentials():
    #     None

    class Config:
        env_file = ".env"
        case_sensitive = True


# Initialize settings
settings = Settings()
