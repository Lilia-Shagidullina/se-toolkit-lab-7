"""Handler for /scores command."""

from config import get_settings
from services.lms_client import LMSClient


async def handle_scores(lab_id: str | None = None) -> str:
    """Handle /scores command.

    Args:
        lab_id: The lab identifier (e.g., "lab-04").

    Returns:
        Pass rates for the specified lab.
    """
    if not lab_id:
        return "Usage: /scores <lab_id>\nExample: /scores lab-04"

    settings = get_settings()
    client = LMSClient(
        base_url=settings.lms_api_base_url,
        api_key=settings.lms_api_key,
    )

    try:
        pass_rates = await client.get_pass_rates(lab_id)
    except Exception as e:
        return f"❌ Backend error: {e}"

    if not pass_rates:
        return f"📊 No data available for {lab_id}. Check that the lab exists and ETL sync has been run."

    # Format pass rates
    lines = [f"📊 Pass rates for {lab_id}:\n"]
    for pr in pass_rates:
        lines.append(f"- {pr.task}: {pr.avg_score}% ({pr.attempts} attempts)")

    return "\n".join(lines)
