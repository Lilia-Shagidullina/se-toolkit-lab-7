"""Handler for /health command."""

from config import get_settings
from services.lms_client import LMSClient, BackendError


async def handle_health() -> str:
    """Handle /health command.

    Returns:
        System health status with backend connection check.
    """
    settings = get_settings()
    client = LMSClient(
        base_url=settings.lms_api_base_url,
        api_key=settings.lms_api_key,
    )

    try:
        is_healthy, message = await client.health_check()
        return message
    except BackendError as e:
        return f"Backend error: {e.message}. Check that the services are running."
    except Exception as e:
        return f"Backend error: {str(e)}. Check that the services are running."
