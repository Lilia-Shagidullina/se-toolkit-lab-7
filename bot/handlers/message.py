"""Handler for natural language messages with LLM routing."""

from config import get_settings
from services.llm_client import LLMClient
from services.lms_client import LMSClient


async def handle_message(message: str, debug: bool = False) -> str:
    """Handle a natural language message using LLM routing.

    Args:
        message: The user's message text.
        debug: Whether to print debug output.

    Returns:
        The response text.
    """
    settings = get_settings()

    llm_client = LLMClient(
        api_key=settings.llm_api_key,
        base_url=settings.llm_api_base_url,
        model=settings.llm_api_model,
    )

    lms_client = LMSClient(
        base_url=settings.lms_api_base_url,
        api_key=settings.lms_api_key,
    )

    return await llm_client.route(message, lms_client, debug=debug)
