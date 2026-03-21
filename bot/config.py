"""Configuration for the LMS bot."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Bot configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env.bot.secret",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram bot token
    bot_token: str = ""

    # LMS API configuration
    lms_api_base_url: str = "http://localhost:8000"
    lms_api_key: str = ""

    # LLM API configuration
    llm_api_key: str = ""


def get_settings() -> BotSettings:
    """Get bot settings from environment."""
    return BotSettings()
