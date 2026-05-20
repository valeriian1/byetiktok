from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from config import POLL_HOUR, POLL_MINUTE
from scheduler.jobs import trigger_daily_poll
import logging

logger = logging.getLogger(__name__)

def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """
    Creates and configures the AsyncIOScheduler.
    Schedules the daily poll job using the HOUR and MINUTE loaded from settings.
    """
    scheduler = AsyncIOScheduler()
    
    # Register the cron trigger
    scheduler.add_job(
        trigger_daily_poll,
        CronTrigger(hour=POLL_HOUR, minute=POLL_MINUTE),
        args=[bot],
        id="daily_checkin_poll",
        replace_existing=True
    )
    
    logger.info(f"Scheduler configured: daily poll scheduled at {POLL_HOUR:02d}:{POLL_MINUTE:02d}")
    return scheduler
