from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_daily_poll_keyboard() -> InlineKeyboardMarkup:
    """Returns the inline keyboard for the daily check-in poll"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Ні, тримаюсь", callback_data="check:clean"),
        InlineKeyboardButton(text="❌ Так, зірвався", callback_data="check:relapsed")
    )
    return builder.as_markup()

def get_leaderboard_keyboard() -> InlineKeyboardMarkup:
    """Returns sorting options for the leaderboard"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔥 Найкращий стрік", callback_data="lead:best_streak"),
        InlineKeyboardButton(text="⚡ Поточний стрік", callback_data="lead:current_streak")
    )
    builder.row(
        InlineKeyboardButton(text="🏆 Досвід & XP", callback_data="lead:xp")
    )
    return builder.as_markup()

def get_admin_forcecheck_keyboard() -> InlineKeyboardMarkup:
    """Returns admin check-in control button"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⏳ Запустити опитування зараз", callback_data="admin:forcecheck")
    )
    return builder.as_markup()
