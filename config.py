import os
from dotenv import load_dotenv

load_dotenv()  # Local use ke liye
TOKEN = os.environ.get("TOKEN")  # Heroku me Config Vars se

if not TOKEN:
    raise ValueError("Bot token missing! Add TOKEN in environment variables or .env file.")
