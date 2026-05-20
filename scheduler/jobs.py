from aiogram import Bot
from database.requests import get_active_chats
from database.db import async_session
from database.models import User
from keyboards.inline import get_daily_poll_keyboard
from utils.messages import get_daily_checkin_message
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

async def trigger_daily_poll(bot: Bot) -> tuple[int, int]:
    """
    Broadcasts the daily check-in poll to all registered active group chats
    and sends direct message check-ins to all registered users.
    Returns a tuple (successful_group_deliveries, successful_dm_deliveries).
    """
    # 1. Fetch active group chats
    try:
        chats = await get_active_chats()
    except Exception as e:
        logger.error(f"Error fetching active chats: {e}")
        chats = []
        
    # 2. Fetch all registered user IDs
    try:
        async with async_session() as session:
            stmt = select(User.telegram_id)
            result = await session.execute(stmt)
            user_ids = result.scalars().all()
    except Exception as e:
        logger.error(f"Error fetching user IDs: {e}")
        user_ids = []
        
    chat_success = 0
    user_success = 0
    
    poll_text = get_daily_checkin_message()
    keyboard = get_daily_poll_keyboard()
    
    # 3. Deliver to registered groups
    for c in chats:
        try:
            await bot.send_message(
                chat_id=c.chat_id,
                text=poll_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            chat_success += 1
            logger.info(f"Daily poll successfully sent to group {c.chat_id}")
        except Exception as e:
            logger.warning(f"Could not send daily poll to group {c.chat_id}: {e}")
            
    # 4. Deliver directly in PM
    for uid in user_ids:
        try:
            await bot.send_message(
                chat_id=uid,
                text=poll_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            user_success += 1
        except Exception as e:
            # Users blocking the bot or not starting it in PM is very common
            logger.debug(f"Could not send daily poll DM to user {uid}: {e}")
            
    return chat_success, user_success
