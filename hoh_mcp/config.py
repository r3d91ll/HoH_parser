from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from typing import Any

load_dotenv()

class Settings(BaseSettings):
    debug: bool = False
    log_level: str = "INFO"
    arangodb_url: str = "http://localhost:8529"
    arangodb_user: str = "root"
    arangodb_password: str = ""
    # Add more config options as needed

    model_config = {
        "env_file": ".env"
    }

settings = Settings()
