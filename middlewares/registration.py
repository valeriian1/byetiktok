from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from database.requests import register_user, register_chat
from config import ADMIN_IDS

class RegistrationMiddleware(BaseMiddleware):
    """
    Middleware to automatically register and update users and chats
    upon any interaction with the bot.
    """
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # 1. Resolve user and chat objects safely
        telegram_user = event.from_user
        event_chat = getattr(event, "chat", None)
        
        # If it's a callback query, the chat is nested under message
        if isinstance(event, CallbackQuery) and event.message:
            event_chat = event.message.chat
            
        # 2. Register/Update Group Chat
        if event_chat and event_chat.type in ["group", "supergroup"]:
            try:
                await register_chat(
                    chat_id=event_chat.id,
                    chat_type=event_chat.type,
                    title=event_chat.title
                )
            except Exception:
                # Fail-safe: database errors shouldn't crash bot flow
                pass
                
        # 3. Register/Update User
        if telegram_user:
            is_admin = telegram_user.id in ADMIN_IDS
            
            # Construct clear display name
            display_name = telegram_user.first_name or "Учасник"
            if telegram_user.last_name:
                display_name += f" {telegram_user.last_name}"
                
            try:
                db_user, is_new = await register_user(
                    telegram_id=telegram_user.id,
                    username=telegram_user.username,
                    display_name=display_name,
                    is_admin=is_admin
                )
                # Inject user info into the handler's parameters list
                data["db_user"] = db_user
                data["is_new_user"] = is_new
            except Exception as e:
                # In case db fails, pass None so handler can react or ignore
                data["db_user"] = None
                data["is_new_user"] = False
                
        return await handler(event, data)
