import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    # API settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development-key")

    # MongoDB settings
    MONGO_URI: str = os.getenv("MONGO_URI", "")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "deepfake_speech")

    # GCS settings
    GCS_BUCKET: str = os.getenv("GCS_BUCKET", "deepfake-speech-files")

    # ML Service settings
    ML_SERVICE_URL: str = os.getenv("ML_SERVICE_URL", "http://ml-service:5000")
    ML_SERVICE_API_KEY: str = os.getenv("ML_SERVICE_API_KEY", "")

    # JWT settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


settings = Settings()