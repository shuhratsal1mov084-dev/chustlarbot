import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
WEBAPP_URL = os.getenv("WEBAPP_URL")
DATABASE_PATH = "database.db"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN must be set in .env file")
if not ADMIN_PASSWORD:
    raise ValueError("ADMIN_PASSWORD must be set in .env file")
if not WEBAPP_URL:
    raise ValueError("WEBAPP_URL must be set in .env file")
