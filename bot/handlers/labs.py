"""Handler for /labs command."""


async def handle_labs() -> str:
    """Handle /labs command.

    Returns:
        List of available labs.
    """
    return (
        "📋 Доступные лабораторные работы:\n\n"
        "lab-01 - Рынок, продукт и Git\n"
        "lab-02 - Инфраструктура и контейнеризация\n"
        "lab-03 - CI/CD и автоматизация\n"
        "lab-04 - Мониторинг и логирование\n"
    )
