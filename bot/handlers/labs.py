"""Handler for /labs command."""

from config import get_settings
from services.lms_client import LMSClient, BackendError


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

        if not items:
            return "No labs available. The backend may be empty or unreachable."

        # Group items by lab (extract lab number from id like "lab-01-task-1")
        labs_dict: dict[str, dict] = {}
        for item in items:
            item_id = item.get("id", "")
            item_type = item.get("type", "")
            item_name = item.get("name", item_id)

            # Extract lab number (e.g., "lab-01" from "lab-01-task-1")
            parts = item_id.split("-")
            if len(parts) >= 2 and parts[0] == "lab":
                lab_key = f"{parts[0]}-{parts[1]}"
                if lab_key not in labs_dict:
                    labs_dict[lab_key] = {"name": item_name, "tasks": []}
                if item_type == "task":
                    labs_dict[lab_key]["tasks"].append(item_name)

        if not labs_dict:
            # If no structured labs found, just list items
            lab_list = "\n".join(f"- {item.get('name', item.get('id', 'Unknown'))}" for item in items[:10])
            return f"Available items:\n{lab_list}"

        # Format output
        lines = ["Available labs:"]
        for lab_id, lab_info in sorted(labs_dict.items()):
            lab_name = lab_info["name"]
            # Clean up lab name (remove task suffix if present)
            if " - " in lab_name:
                lab_name = lab_name.split(" - ")[0]
            lines.append(f"- {lab_id.upper()} — {lab_name}")

        return "\n".join(lines)

    except BackendError as e:
        return f"Backend error: {e.message}. Check that the services are running."
    except Exception as e:
        return f"Error fetching labs: {str(e)}"
