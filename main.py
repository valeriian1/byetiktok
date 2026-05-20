import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database.db import init_db
from middlewares.registration import RegistrationMiddleware
from handlers.common import common_router
from handlers.gameplay import gameplay_router
from handlers.admin import admin_router
from handlers.chat_member import chat_member_router
from scheduler.scheduler import setup_scheduler

# Configure logging style
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def start_health_check_server():
    """Starts a minimal aiohttp web server to pass cloud platform health checks (e.g., Render, Koyeb)"""
    port = int(os.getenv("PORT", 8080))
    
    async def handle_ping(request):
        return web.Response(text="ByeTikTok Bot is alive!", content_type="text/plain")
        
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health check web server successfully started on port {port}")


async def main():
    # 1. Initialize database models and structure
    logger.info("Initializing SQLite database and applying schemas...")
    await init_db()
    logger.info("Database initialized successfully.")

    # 2. Setup Bot instance and Memory FSM storage
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # 3. Setup global outer middlewares (intercepts events before FSM states are resolved)
    reg_middleware = RegistrationMiddleware()
    dp.message.outer_middleware(reg_middleware)
    dp.callback_query.outer_middleware(reg_middleware)

    # 4. Integrate handlers routers
    dp.include_router(chat_member_router)
    dp.include_router(common_router)
    dp.include_router(gameplay_router)
    dp.include_router(admin_router)

    # 5. Initialize APScheduler daily poll tasks
    scheduler = setup_scheduler(bot)
    
    # 6. Start background health-check web server if PORT is defined (e.g., cloud hostings)
    port = os.getenv("PORT")
    if port:
        logger.info(f"Cloud environment detected (PORT={port}). Launching health check web server...")
        await start_health_check_server()
    
    try:
        # Start background schedule triggers
        scheduler.start()
        logger.info("APScheduler jobs started successfully.")
        
        # Clear webhook backlog and run polling loops
        logger.info("Purging pending updates and starting Telegram polling...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.critical(f"Unhandled critical error inside main loop: {e}", exc_info=True)
    finally:
        # Ensure cleanup is triggered on any exit state
        logger.info("Stopping scheduler jobs...")
        if scheduler.running:
            scheduler.shutdown()
        logger.info("Closing bot session...")
        await bot.session.close()
        logger.info("Bot execution finished.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by system signal.")
