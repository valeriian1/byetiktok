from aiogram import Router, types
from aiogram.filters import Command
from utils.messages import get_start_message, get_help_message
from database.models import User

common_router = Router(name="common")

@common_router.message(Command("start"))
async def cmd_start(message: types.Message, db_user: User, is_new_user: bool):
    """Handles the /start command, registers user and returns atmospheric greeting"""
    if not db_user:
        await message.answer("⚠️ Помилка бази даних. Спробуй пізніше.")
        return
        
    if is_new_user:
        # User registered for the first time
        text = get_start_message(db_user.display_name)
    else:
        # Already registered
        text = (
            f"🕯️ *Вітаємо знову в Братстві Уваги, {db_user.display_name}!*\n\n"
            "Твій фокус залишається твоїм найбільшим скарбом. Алгоритми працюють без вихідних, "
            "але твоя стійкість сильніша.\n\n"
            "📈 Напиши /stats, щоб переглянути свій прогрес, або /leaderboard, щоб побачити успіхи однодумців."
        )
        
    await message.answer(text, parse_mode="Markdown")

@common_router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Handles the /help command, providing rules and instructions"""
    text = get_help_message()
    await message.answer(text, parse_mode="Markdown")
