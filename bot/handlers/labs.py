"""Handler for /labs command."""

from config import get_settings
from services.lms_client import LMSClient


async def handle_labs() -> str:
    """Handle /labs command.

    Returns:
        List of available labs from the backend.
    """
    settings = get_settings()
    client = LMSClient(
        base_url=settings.lms_api_base_url,
        api_key=settings.lms_api_key,
    )

    try:
        items = await client.get_items()
    except Exception as e:
        return f"❌ Backend error: {e}"

    # Filter only labs (type == "lab")
    labs = [item for item in items if item.get("type") == "lab"]

    if not labs:
        return "📋 No labs available at the moment."

    # Format lab list
    lab_lines = []
    for lab in sorted(labs, key=lambda x: x.get("title", "")):
        title = lab.get("title", "Unknown")
        description = lab.get("description", "")
        lab_lines.append(f"- {title}")
        if description:
            lab_lines.append(f"  {description}")

    return "📋 Available labs:\n\n" + "\n".join(lab_lines)
