import os
from dotenv import load_dotenv

# Load variables from .env file if it exists
load_dotenv()

# Bot setup
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in the environment variables or .env file.")

# Admin configuration
admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(aid.strip()) for aid in admin_ids_str.split(",") if aid.strip().isdigit()]

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///byetiktok.db")

# Scheduler setup
POLL_TIME = os.getenv("POLL_TIME", "21:00")
try:
    POLL_HOUR, POLL_MINUTE = map(int, POLL_TIME.split(":"))
except ValueError:
    POLL_HOUR, POLL_MINUTE = 21, 0
