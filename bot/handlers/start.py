"""Handler for /start command."""


async def handle_start() -> str:
    """Handle /start command.

    Returns:
        Welcome message for new users.
    """
    return (
        "👋 Добро пожаловать в LMS Bot!\n\n"
        "Я помогу вам взаимодействовать с системой управления обучением.\n\n"
        "Доступные команды:\n"
        "/help - показать список команд\n"
        "/health - проверить статус системы\n"
        "/labs - показать доступные лабораторные работы\n"
    )
