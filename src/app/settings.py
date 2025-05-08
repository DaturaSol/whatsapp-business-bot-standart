from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
DOTENV_PATH = BASE_DIR / "../../.env"  # ajuste se necessário

load_dotenv(dotenv_path=DOTENV_PATH)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=DOTENV_PATH,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    access_token: str = Field(..., env="ACCESS_TOKEN")
    api_version: str = Field(..., env="API_VERSION")
    phone_number_id: str = Field(..., env="PHONE_NUMBER_ID")
    webhook_verify_token: str = Field(..., env="WEBHOOK_VERIFY_TOKEN")
