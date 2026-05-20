from aiogram import Router, types, Bot, F
from aiogram.filters import Command
from database.models import User
from database.db import async_session
from database.requests import reset_user_stats
from keyboards.inline import get_daily_poll_keyboard
from utils.messages import get_daily_checkin_message
from sqlalchemy import select
import logging

admin_router = Router(name="admin")
logger = logging.getLogger(__name__)

@admin_router.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message, db_user: User, bot: Bot):
    """Sends a global broadcast message to all registered users"""
    if not db_user or not db_user.is_admin:
        await message.answer("❌ Доступ заборонено. Ця команда лише для адміністраторів.")
        return
        
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "❌ *Будь ласка, вкажи текст повідомлення.* \n"
            "Приклад: `/broadcast Увага! Сьогодні о 22:00 технічні роботи.`",
            parse_mode="Markdown"
        )
        return
        
    broadcast_text = parts[1]
    await message.answer("📣 *Початок розсилки...*", parse_mode="Markdown")
    
    # Fetch all users
    async with async_session() as session:
        stmt = select(User.telegram_id)
        result = await session.execute(stmt)
        user_ids = result.scalars().all()
        
    success = 0
    failed = 0
    
    for uid in user_ids:
        try:
            await bot.send_message(
                chat_id=uid,
                text=f"📢 *Офіційне сповіщення від Братства Уваги:*\n\n{broadcast_text}",
                parse_mode="Markdown"
            )
            success += 1
        except Exception as e:
            failed += 1
            logger.warning(f"Failed to send broadcast message to {uid}: {e}")
            
    await message.answer(
        f"✅ *Розсилку завершено!*\n━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📥 Доставлено користувачам: `{success}`\n"
        f"❌ Не вдалося надіслати: `{failed}`",
        parse_mode="Markdown"
    )

@admin_router.message(Command("forcecheck"))
async def cmd_forcecheck(message: types.Message, db_user: User, bot: Bot):
    """Triggers the check-in poll manually in all active registered chats"""
    if not db_user or not db_user.is_admin:
        await message.answer("❌ Доступ заборонено. Ця команда лише для адміністраторів.")
        return
        
    await message.answer("⏳ *Запуск примусового опитування...*", parse_mode="Markdown")
    
    from scheduler.jobs import trigger_daily_poll
    chat_count, user_count = await trigger_daily_poll(bot)
    
    await message.answer(
        f"✅ *Опитування успішно надіслано!*\n━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Групові чати: `{chat_count}`\n"
        f"👤 Особисті повідомлення: `{user_count}`",
        parse_mode="Markdown"
    )

@admin_router.message(Command("resetuser"))
async def cmd_resetuser(message: types.Message, db_user: User):
    """Wipes the statistics and achievements of a specific user"""
    if not db_user or not db_user.is_admin:
        await message.answer("❌ Доступ заборонено. Ця команда лише для адміністраторів.")
        return
        
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "❌ *Будь ласка, вкажи ID або @username користувача.* \n"
            "Приклад: `/resetuser 123456789` або `/resetuser @username`",
            parse_mode="Markdown"
        )
        return
        
    target = parts[1].strip()
    target_user = None
    
    # Find user by ID or Username
    async with async_session() as session:
        if target.isdigit():
            stmt = select(User).where(User.telegram_id == int(target))
        else:
            clean_username = target.lstrip("@")
            stmt = select(User).where(User.username == clean_username)
        result = await session.execute(stmt)
        target_user = result.scalar_one_or_none()
        
    if not target_user:
        await message.answer(f"❌ Користувача `{target}` не знайдено в системі.", parse_mode="Markdown")
        return
        
    # Reset stats
    reset_res = await reset_user_stats(target_user.telegram_id)
    if reset_res:
        await message.answer(
            f"🧹 *Успішно скинуто!*\n"
            f"Всі стріки, XP, ачивки та логи користувача "
            f"*{target_user.display_name}* (ID: `{target_user.telegram_id}`) "
            f"були повернуті до початкових значень.",
            parse_mode="Markdown"
        )
    else:
        await message.answer("❌ Сталася помилка при спробі очищення.", parse_mode="Markdown")
