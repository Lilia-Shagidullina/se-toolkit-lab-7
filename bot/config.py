"""Configuration for the LMS bot."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the path to the root directory (parent of bot/)
ROOT_DIR = Path(__file__).resolve().parent.parent


class BotSettings(BaseSettings):
    """Bot configuration settings."""

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env.bot.secret",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram bot token
    bot_token: str = ""

    # LMS API configuration
    lms_api_base_url: str = os.getenv("LMS_API_BASE_URL", "http://localhost:42002")
    lms_api_key: str = ""

    # LLM API configuration
    llm_api_key: str = ""
    llm_api_base_url: str = os.getenv("LLM_API_BASE_URL", "http://localhost:42005")
    llm_api_model: str = os.getenv("LLM_API_MODEL", "qwen-2.5-72b")


def get_settings() -> BotSettings:
    """Get bot settings from environment."""
    return BotSettings()
