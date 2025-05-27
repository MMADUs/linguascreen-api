# Copyright (c) 2024-2025 LinguaScreen, Inc.
#
# This file is part of LinguaScreen Server
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pydantic_settings import BaseSettings

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "FastAPI Server"
    PORT: int = 8000
    DEBUG: bool = False

    # Database settings
    DATABASE_URL: str = "sqlite:///./app.db"

    # Security settings
    SECRET_KEY: str = "default-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Azure credential settings

    # text-translation credentials
    AZURE_TEXT_TRANSLATION_API_KEY: str
    AZURE_TEXT_TRANSLATION_REGION: str = "southeastasia"

    # image-analysis credentials
    AZURE_IMAGE_ANALYSIS_ENDPOINT: str
    AZURE_IMAGE_ANALYSIS_API_KEY: str

    # azure-llm-openai
    AZURE_LLM_OPENAI_API_VERSION: str = "2024-10-21"
    AZURE_LLM_OPENAI_API_KEY: str
    AZURE_LLM_OPENAI_ENDPOINT: str

    class Config:
        env_file = ".env"
        case_sensitive = True


# Initialize settings
settings = Settings()
