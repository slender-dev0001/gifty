import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import re

class EmailSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect("email_system.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_emails (
                user_id INTEGER PRIMARY KEY,
                email TEXT NOT NULL,
                guild_id INTEGER
            )
        ''')
        conn.commit()
        conn.close()

    def is_valid_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def set_email(self, user_id, email, guild_id):
        conn = sqlite3.connect("email_system.db")
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_emails WHERE user_id = ? AND guild_id = ?', (user_id, guild_id))
        if cursor.fetchone():
            cursor.execute('UPDATE user_emails SET email = ? WHERE user_id = ? AND guild_id = ?', (email, user_id, guild_id))
        else:
            cursor.execute('INSERT INTO user_emails (user_id, email, guild_id) VALUES (?, ?, ?)', (user_id, email, guild_id))
        conn.commit()
        conn.close()

    def get_email(self, user_id, guild_id):
        conn = sqlite3.connect("email_system.db")
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM user_emails WHERE user_id = ? AND guild_id = ?', (user_id, guild_id))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    @app_commands.command(name="setemail", description="Définir votre email")
    async def setemail(self, interaction: discord.Interaction, email: str):
        if not self.is_valid_email(email):
            embed = discord.Embed(
                title="❌ Email invalide",
                description=f"Le format de l'email `{email}` n'est pas valide!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        self.set_email(interaction.user.id, email, interaction.guild.id)
        embed = discord.Embed(
            title="✅ Email défini",
            description=f"Votre email a été défini à: `{email}`",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="getemail", description="Afficher votre email")
    async def getemail(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user
        email = self.get_email(user.id, interaction.guild.id)
        
        if not email:
            embed = discord.Embed(
                title="❌ Pas d'email",
                description=f"{user.mention} n'a pas défini d'email",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="📧 Email",
                description=f"Email de {user.mention}: `{email}`",
                color=discord.Color.blue()
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(EmailSystem(bot))
