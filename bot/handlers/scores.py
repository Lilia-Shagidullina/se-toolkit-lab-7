"""Handler for /scores command."""


async def handle_scores(lab_id: str | None = None) -> str:
    """Handle /scores command.

    Args:
        lab_id: The lab identifier (e.g., "lab-04").

    Returns:
        Pass rates for the specified lab (placeholder for Task 1).
    """
    if not lab_id:
        return "Usage: /scores <lab_id>\nExample: /scores lab-04"

    return (
        f"📊 Оценки для {lab_id}:\n\n"
        f"- Repository Setup: 92.1% (187 attempts)\n"
        f"- Back-end Testing: 71.4% (156 attempts)\n"
        f"- Add Front-end: 68.3% (142 attempts)\n"
    )
