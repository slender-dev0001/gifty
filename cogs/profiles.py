import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import os

class Database:
    def __init__(self):
        self.db_path = "users.db"
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                balance INTEGER DEFAULT 0,
                bio TEXT DEFAULT "Aucune bio"
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_user(self, user_id, username):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
            conn.commit()
        
        conn.close()

    def add_xp(self, user_id, xp):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        self.add_user(user_id, "Unknown")
        
        cursor.execute('SELECT xp, level FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            current_xp, level = result
            new_xp = current_xp + xp
            new_level = level + (new_xp // 1000)
            new_xp = new_xp % 1000
            
            cursor.execute('UPDATE users SET xp = ?, level = ? WHERE user_id = ?', (new_xp, new_level, user_id))
            conn.commit()
        
        conn.close()

    def add_balance(self, user_id, amount):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        self.add_user(user_id, "Unknown")
        
        cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            balance = result[0] + amount
            cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (balance, user_id))
            conn.commit()
        
        conn.close()

    def get_user(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result

    def get_leaderboard(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id, username, xp, level FROM users ORDER BY level DESC, xp DESC LIMIT ?', (limit,))
        results = cursor.fetchall()
        conn.close()
        
        return results

    def update_bio(self, user_id, bio):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        self.add_user(user_id, "Unknown")
        cursor.execute('UPDATE users SET bio = ? WHERE user_id = ?', (bio[:100], user_id))
        
        conn.commit()
        conn.close()

class Profiles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        self.db.add_user(message.author.id, str(message.author))
        self.db.add_xp(message.author.id, 10)

    @commands.command(name='profile')
    async def profile(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_data = self.db.get_user(member.id)
        
        if not user_data:
            await ctx.send("❌ Aucun profil trouvé")
            return
        
        user_id, username, xp, level, balance, bio = user_data
        
        embed = discord.Embed(
            title=f"👤 Profil de {member.name}",
            color=member.color
        )
        embed.add_field(name="💬 Bio", value=bio, inline=False)
        embed.add_field(name="📊 Niveau", value=f"Level **{level}**", inline=True)
        embed.add_field(name="⭐ XP", value=f"**{xp}/1000** XP", inline=True)
        embed.add_field(name="💰 Balance", value=f"**{balance}** coins", inline=True)
        
        progress_bar = "█" * (xp // 100) + "░" * (10 - xp // 100)
        embed.add_field(name="Progression", value=f"`{progress_bar}`", inline=False)
        
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        
        await ctx.send(embed=embed)

    @commands.command(name='setbio')
    async def setbio(self, ctx, *, bio):
        self.db.update_bio(ctx.author.id, bio)
        await ctx.send(f"✅ Bio mise à jour: {bio}")

    @commands.command(name='balance')
    async def balance(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_data = self.db.get_user(member.id)
        
        if not user_data:
            await ctx.send("❌ Aucun profil trouvé")
            return
        
        balance = user_data[4]
        embed = discord.Embed(
            title=f"💰 Balance",
            description=f"{member.mention} a **{balance}** coins",
            color=discord.Color.gold()
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='addbal')
    @commands.has_permissions(manage_guild=True)
    async def addbal(self, ctx, member: discord.Member, amount: int):
        self.db.add_balance(member.id, amount)
        embed = discord.Embed(
            title="💰 Balance ajoutée",
            description=f"{member.mention} a reçu **{amount}** coins",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx):
        leaders = self.db.get_leaderboard(10)
        
        if not leaders:
            await ctx.send("❌ Pas d'utilisateurs avec du profil")
            return
        
        embed = discord.Embed(
            title="🏆 Leaderboard",
            color=discord.Color.gold()
        )
        
        leaderboard_text = ""
        for i, (user_id, username, xp, level) in enumerate(leaders, 1):
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
            leaderboard_text += f"{medal} **{username}** - Level {level} ({xp}/1000 XP)\n"
        
        embed.description = leaderboard_text
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Profiles(bot))
