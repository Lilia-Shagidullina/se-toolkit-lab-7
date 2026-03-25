"""Handler for /health command."""

from config import get_settings
from services.lms_client import LMSClient


async def handle_health() -> str:
    """Handle /health command.

    Returns:
        System health status from the backend.
    """
    try:
        settings = get_settings()
        client = LMSClient(
            base_url=settings.lms_api_base_url,
            api_key=settings.lms_api_key,
        )

        status = await client.health_check()
    except Exception as e:
        return f"❌ Backend error: {e}"

    if status.is_healthy:
        return f"✅ Backend is healthy. {status.item_count} items available."
    else:
        return f"❌ Backend error: {status.error_message}"
