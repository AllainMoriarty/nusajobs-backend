from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database Configurations
    DB_URL: str = os.getenv("DB_URL")

    # Hugging Face Token
    HF_TOKEN: str = os.getenv("HF_TOKEN")

    # JWT Configurations
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    # S3 Configurations
    S3_ACCESS_KEY_ID: str = os.getenv("S3_ACCESS_KEY_ID")
    S3_SECRET_ACCESS_KEY: str = os.getenv("S3_SECRET_ACCESS_KEY")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME")
    S3_REGION: str = os.getenv("S3_REGION")
    S3_ENDPOINT_URL: str = os.getenv("S3_ENDPOINT_URL")

    # OpenAI API Key
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()