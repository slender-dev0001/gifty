import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('PREFIX', '+')

if not DISCORD_TOKEN:
    raise ValueError("❌ DISCORD_TOKEN est manquant dans le fichier .env")
