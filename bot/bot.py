#!/usr/bin/env python3
"""LMS Telegram Bot entry point.

Usage:
    uv run bot.py                  # Run in Telegram mode
    uv run bot.py --test "/start"  # Run in test mode (no Telegram connection)
    uv run bot.py --test "what labs are available"  # Natural language query
"""

import asyncio
import sys
from pathlib import Path

# Add the bot directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import get_settings
from handlers.help import handle_help
from handlers.health import handle_health
from handlers.labs import handle_labs
from handlers.message import handle_message
from handlers.scores import handle_scores
from handlers.start import handle_start

# Import aiogram only when needed (not in test mode)
aiogram = None
try:
    import aiogram  # type: ignore
except ImportError:
    pass


HANDLERS = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
}


async def process_command(command: str) -> str:
    """Process a command or message and return the response.

    Args:
        command: The command string (e.g., "/start", "/help") or natural language message.

    Returns:
        The response text.
    """
    # Check if it's a slash command
    if command.startswith("/"):
        parts = command.split()
        cmd = parts[0].lower()

        if cmd in HANDLERS:
            return await HANDLERS[cmd]()

        if cmd == "/scores":
            # Extract lab_id argument if present
            lab_id = parts[1] if len(parts) > 1 else None
            return await handle_scores(lab_id)

        return "❓ Неизвестная команда. Используйте /help для списка команд."
    else:
        # Natural language message - use LLM routing
        return await handle_message(command, debug=True)


async def run_test_mode(command: str) -> None:
    """Run the bot in test mode.

    Args:
        command: The command to test (e.g., "/start").
    """
    response = await process_command(command)
    print(response)


async def run_telegram_mode() -> None:
    """Run the bot in Telegram mode."""
    if aiogram is None:
        print("Error: aiogram is not installed. Run: uv sync")
        sys.exit(1)

    settings = get_settings()

    if not settings.bot_token:
        print("Error: BOT_TOKEN is not set in .env.bot.secret")
        sys.exit(1)

    from aiogram import Bot, Dispatcher, types
    from aiogram.filters import Command
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Create inline keyboard for /start
    start_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Labs", callback_data="labs"),
                InlineKeyboardButton(text="📊 Scores", callback_data="scores_help"),
            ],
            [
                InlineKeyboardButton(text="💚 Health", callback_data="health"),
                InlineKeyboardButton(text="❓ Help", callback_data="help"),
            ],
        ]
    )

    @dp.message(Command("start"))
    async def start_handler(message: types.Message) -> None:
        """Handle /start command."""
        response = await handle_start()
        await message.answer(response, reply_markup=start_keyboard)

    @dp.message(Command("help"))
    async def help_handler(message: types.Message) -> None:
        """Handle /help command."""
        response = await handle_help()
        await message.answer(response)

    @dp.message(Command("health"))
    async def health_handler(message: types.Message) -> None:
        """Handle /health command."""
        response = await handle_health()
        await message.answer(response)

    @dp.message(Command("labs"))
    async def labs_handler(message: types.Message) -> None:
        """Handle /labs command."""
        response = await handle_labs()
        await message.answer(response)

    @dp.message(Command("scores"))
    async def scores_handler(message: types.Message) -> None:
        """Handle /scores command."""
        args = message.text.split()[1:] if message.text else []
        lab_id = args[0] if args else None
        response = await handle_scores(lab_id)
        await message.answer(response)

    @dp.message()
    async def message_handler(message: types.Message) -> None:
        """Handle natural language messages."""
        if message.text:
            response = await handle_message(message.text, debug=True)
            await message.answer(response)

    @dp.callback_query()
    async def callback_handler(callback_query: types.CallbackQuery) -> None:
        """Handle inline button callbacks."""
        data = callback_query.data
        response = ""

        if data == "labs":
            response = await handle_labs()
        elif data == "health":
            response = await handle_health()
        elif data == "help":
            response = await handle_help()
        elif data == "scores_help":
            response = "📊 Чтобы посмотреть оценки, отправьте /scores lab-04 (замените lab-04 на нужный номер лабы). Или спросите 'покажи оценки для lab-04'"

        if response:
            await callback_query.message.answer(response)

        await callback_query.answer()

    print("Bot is starting...")
    await dp.start_polling(bot)


def main() -> None:
    """Main entry point."""
    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print("Usage: uv run bot.py --test <command>")
            print("Example: uv run bot.py --test '/start'")
            sys.exit(1)

        command = sys.argv[2]
        response = asyncio.run(process_command(command))
        print(response)
        return

    # Run in Telegram mode
    asyncio.run(run_telegram_mode())


if __name__ == "__main__":
    main()
