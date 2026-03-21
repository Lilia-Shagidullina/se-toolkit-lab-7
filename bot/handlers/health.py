"""Handler for /health command."""


async def handle_health() -> str:
    """Handle /health command.

    Returns:
        System health status.
    """
    return "✅ Система работает нормально"
