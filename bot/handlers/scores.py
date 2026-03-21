"""Handler for /scores command."""

from config import get_settings
from services.lms_client import LMSClient, BackendError


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

        if not pass_rates:
            # Try to get lab info to check if it exists
            items = await client.get_items()
            lab_exists = any(
                item.get("id", "").startswith(lab_id) for item in items
            )

            if not lab_exists:
                return f"Lab '{lab_id}' not found. Use /labs to see available labs."
            return f"No pass rate data available for '{lab_id}'."

        # Format output
        lines = [f"Pass rates for {lab_id.upper()}:"]
        for rate in pass_rates:
            task_name = rate.get("task_name", rate.get("task", "Unknown"))
            pass_rate = rate.get("pass_rate", rate.get("rate", 0))
            attempts = rate.get("attempts", rate.get("count", 0))

            # Format percentage
            if isinstance(pass_rate, float):
                percentage = f"{pass_rate * 100:.1f}%"
            else:
                percentage = f"{pass_rate}%"

            lines.append(f"- {task_name}: {percentage} ({attempts} attempts)")

        return "\n".join(lines)

    except BackendError as e:
        return f"Backend error: {e.message}. Check that the services are running."
    except Exception as e:
        return f"Error fetching scores: {str(e)}"
