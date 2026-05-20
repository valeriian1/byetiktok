import random
from datetime import datetime
from aiogram import Router, types, F
from aiogram.filters import Command
from database.models import User
from database.requests import get_user_stats, get_leaderboard, add_daily_check, use_freeze
from utils.messages import (
    get_stats_message, 
    get_leaderboard_message, 
    get_achievement_unlock_message, 
    get_level_up_message
)
from utils.insights import get_random_insight, get_random_quote, get_random_reaction
from keyboards.inline import get_leaderboard_keyboard
from services.gamification import ACHIEVEMENTS_BOOK, LEVEL_THRESHOLDS

gameplay_router = Router(name="gameplay")

@gameplay_router.message(Command("stats"))
async def cmd_stats(message: types.Message, db_user: User):
    """Displays detailed personal statistics and achievements for the user"""
    if not db_user:
        await message.answer("⚠️ Спочатку зареєструйся через /start")
        return
        
    stats = await get_user_stats(db_user.telegram_id)
    if not stats:
        await message.answer("⚠️ Не вдалося завантажити статистику. Спробуй ще раз.")
        return
        
    text = get_stats_message(stats)
    await message.answer(text, parse_mode="Markdown")

@gameplay_router.message(Command("leaderboard"))
async def cmd_leaderboard(message: types.Message):
    """Displays the group leaderboard, sorted by best streak by default"""
    users = await get_leaderboard(sort_by="best_streak")
    text = get_leaderboard_message(users, sort_by="best_streak")
    keyboard = get_leaderboard_keyboard()
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

@gameplay_router.callback_query(F.data.startswith("lead:"))
async def cb_leaderboard_sort(callback: types.CallbackQuery):
    """Handles switching between different leaderboard sorting modes dynamically"""
    sort_by = callback.data.split(":")[1]
    
    users = await get_leaderboard(sort_by=sort_by)
    text = get_leaderboard_message(users, sort_by=sort_by)
    keyboard = get_leaderboard_keyboard()
    
    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    except Exception:
        # Prevent errors if user clicks the button for the already selected sort option
        pass
    finally:
        await callback.answer()

@gameplay_router.message(Command("freeze"))
async def cmd_freeze(message: types.Message, db_user: User):
    """Triggers streak freezing for today, keeping the active streak safe"""
    if not db_user:
        await message.answer("⚠️ Спочатку зареєструйся через /start")
        return
        
    today = datetime.utcnow().date()
    
    try:
        user, new_achievements = await use_freeze(db_user.telegram_id, today)
    except ValueError as e:
        await message.answer(f"❌ *Помилка:* {str(e)}", parse_mode="Markdown")
        return
        
    text = (
        f"❄️ *ЗАМОРОЗКУ АКТИВОВАНО!* ❄️\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Успішно заморожено стрік для *{user.display_name}* на сьогодні ({today.strftime('%d.%m.%Y')}).\n\n"
        f"🔥 Твій поточний стрік у `{user.current_streak} днів` у безпеці й не згорить.\n"
        f"❄️ Доступних заморозок залишилось: `{user.freezes_available}`.\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"_Відпочинь сьогодні від екранів та віднови сили. Завтра чекаємо твого свідомого вибору!_"
    )
    
    await message.answer(text, parse_mode="Markdown")
    
    # Award and notify achievements
    for ach in new_achievements:
        xp_bonus = ACHIEVEMENTS_BOOK.get(ach.badge_id, {}).get("xp_bonus", 10)
        ach_text = get_achievement_unlock_message(
            display_name=user.display_name,
            badge_title=ach.title,
            description=ach.description,
            xp_bonus=xp_bonus
        )
        await message.answer(ach_text, parse_mode="Markdown")

@gameplay_router.callback_query(F.data.startswith("check:"))
async def cb_checkin(callback: types.CallbackQuery, db_user: User):
    """Processes check-in feedback from daily polls, updating user state and sending rewards"""
    if not db_user:
        await callback.answer("⚠️ Спершу напиши боту в приватні повідомлення /start", show_alert=True)
        return
        
    status = callback.data.split(":")[1] # "clean" or "relapsed"
    today = datetime.utcnow().date()
    
    try:
        user, level_up_title, new_achievements = await add_daily_check(
            telegram_id=callback.from_user.id,
            check_date=today,
            status=status
        )
    except ValueError as e:
        await callback.answer(str(e), show_alert=True)
        return
        
    await callback.answer("Твій звіт прийнято!")
    
    # Send a notification to the chat (so everyone in the group can see the milestone)
    display_name = callback.from_user.full_name
    mention_html = f"<a href='tg://user?id={user.telegram_id}'>{user.display_name}</a>"
    
    if status == 'clean':
        group_text = (
            f"🕯️ {mention_html} *тримається!* \n"
            f"└ Стрік: <code>{user.current_streak} дн</code> 🔥 | Досвід: <code>+{10} XP</code>"
        )
    else:
        group_text = (
            f"🍂 {mention_html} *зірвався...* \n"
            f"└ Стрік згорів. Але це лише досвід. Почни спочатку завтра!"
        )
    await callback.message.answer(group_text, parse_mode="HTML")
    
    # Prepare detailed personal response (sent in private chat to avoid group spam)
    private_text = ""
    if status == 'clean':
        private_text += (
            f"☀️ *Чудовий результат сьогодні!*\n"
            f"Ти успішно провів день без TikTok / Reels / Shorts.\n\n"
            f"🔥 Поточний стрік: `{user.current_streak} днів`\n"
            f"⚡ Досвід: `+10 XP` (Всього: `{user.xp_points} XP`)\n\n"
            f"💡 _{get_random_reaction()}_\n\n"
        )
        # 40% probability to append random educational detox fact or focus quote
        if random.random() < 0.4:
            private_text += (get_random_insight() if random.random() < 0.5 else get_random_quote()) + "\n"
    else:
        private_text += (
            f"🍂 *Звіт про зрив прийнято.*\n\n"
            f"Твій стрік скинуто до `0`. Не звинувачуй себе. Звільнення від цифрових кайданів "
            f"— це шлях спроб і помилок.\n\n"
            f"💡 *Пам'ятай:* Твоя увага тренується як м'яз. Зрив сьогодні — це просто привід "
            f"проаналізувати тригери та спробувати знову. Завтра чекаємо на твою перемогу!"
        )
        
    # Send achievements alerts to private message
    for ach in new_achievements:
        xp_bonus = ACHIEVEMENTS_BOOK.get(ach.badge_id, {}).get("xp_bonus", 10)
        ach_text = get_achievement_unlock_message(
            display_name=user.display_name,
            badge_title=ach.title,
            description=ach.description,
            xp_bonus=xp_bonus
        )
        try:
            await callback.bot.send_message(chat_id=user.telegram_id, text=ach_text, parse_mode="Markdown")
        except Exception:
            pass # Suppress exceptions if the user hasn't PM'ed the bot
            
    # Send level up alerts to private message
    if level_up_title:
        level_desc = ""
        for lvl, _, _, desc in LEVEL_THRESHOLDS:
            if lvl == user.level:
                level_desc = desc
                break
        lvl_text = get_level_up_message(
            display_name=user.display_name,
            level=user.level,
            title=level_up_title,
            description=level_desc
        )
        # Grant a bonus freeze day for leveling up
        from database.requests import force_award_freeze
        await force_award_freeze(user.telegram_id, count=1)
        
        try:
            await callback.bot.send_message(chat_id=user.telegram_id, text=lvl_text, parse_mode="Markdown")
        except Exception:
            pass
            
    # Send main personalized receipt to user
    try:
        await callback.bot.send_message(chat_id=user.telegram_id, text=private_text, parse_mode="Markdown")
    except Exception:
        # Fail silently if bot is not started in PM yet
        pass
