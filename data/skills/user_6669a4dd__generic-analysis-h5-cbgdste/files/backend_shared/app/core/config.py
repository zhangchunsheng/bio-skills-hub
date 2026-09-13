from pydantic_settings import BaseSettings
from pathlib import Path
import os


class Settings(BaseSettings):
    # AI API
    base_url: str = "https://api.example.com/v1"
    api_key: str = "sk-your-api-key"
    default_model: str = "gpt-4o"

    # LibreOffice
    soffice_path: str = r"C:\Program Files\LibreOffice\program\soffice.exe"

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/analysis.db"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Paths
    upload_dir: str = str(Path(__file__).parent.parent.parent / "uploads")
    h5_export_dir: str = str(Path(__file__).parent.parent.parent / "data" / "exports" / "h5")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
