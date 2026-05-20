from aiogram import Router, types
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION
from database.requests import register_chat, deactivate_chat
import logging

chat_member_router = Router(name="chat_member")
logger = logging.getLogger(__name__)

@chat_member_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def bot_added_to_chat(event: types.ChatMemberUpdated):
    """Fires when the bot is added to a new group/supergroup chat"""
    chat = event.chat
    try:
        await register_chat(chat_id=chat.id, chat_type=chat.type, title=chat.title)
        logger.info(f"Bot added to chat {chat.title or chat.id}")
        
        await event.answer(
            "🏛️ *Братство Уваги вітає цей чат!*\n\n"
            "Я тут, щоб допомогти вам тримати стрік життя без TikTok, Instagram Reels та коротких відео.\n\n"
            "📅 *Як це працює:*\n"
            "• Щодня о *21:00* я надсилатиму сюди опитування.\n"
            "• Ваша задача — чесно голосувати за результати дня.\n\n"
            "⚙️ *ВАЖЛИВО:* Кожен учасник чату повинен обов'язково написати мені в приватні повідомлення "
            "команду `/start`. Це потрібно, щоб я міг нараховувати вам XP, розблоковувати ачивки, "
            "підвищувати рівні та надсилати статистику в DM.\n\n"
            "💡 Напишіть `/help`, щоб дізнатися всі правила.",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error handling bot additions to group: {e}")

@chat_member_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def bot_removed_from_chat(event: types.ChatMemberUpdated):
    """Fires when the bot is kicked or leaves a group/supergroup chat"""
    chat = event.chat
    try:
        await deactivate_chat(chat_id=chat.id)
        logger.info(f"Bot removed/left chat {chat.title or chat.id}. Deactivating chat.")
    except Exception as e:
        logger.error(f"Error handling bot removal from group: {e}")
