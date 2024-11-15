from dotenv import load_dotenv
from os import getenv

load_dotenv()

GEMINI_API_KEY = getenv("GEMINI_API_KEY")
TWOGIS_API_KEY = getenv("TWOGIS_API_KEY")
BOT_TOKEN = getenv("BOT_TOKEN")
CHANNEL_USERNAME = getenv("CHANNEL_USERNAME")
