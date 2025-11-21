import discord
from discord.ext import commands
import threading
from shortlink_server import run_server

class ShortlinkServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_shortlink_server()
    
    def start_shortlink_server(self):
        thread = threading.Thread(target=run_server, args=(self.bot,), daemon=True)
        thread.start()

async def setup(bot):
    await bot.add_cog(ShortlinkServer(bot))
