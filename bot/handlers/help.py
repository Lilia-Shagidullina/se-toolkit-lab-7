"""Handler for /help command."""


async def handle_help() -> str:
    """Handle /help command.

    Returns:
        List of available commands with descriptions.
    """
    return (
        "📚 Список команд:\n\n"
        "/start - приветственное сообщение\n"
        "/help - показать этот список команд\n"
        "/health - проверить статус системы\n"
        "/labs - показать доступные лабораторные работы\n"
        "/scores <lab_id> - показать оценки за лабораторную\n"
    )
