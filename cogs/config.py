import discord
from discord.ext import commands
import sqlite3
from utils import admin_or_owner

class ConfigDB:
    def __init__(self):
        self.db_path = "server_config.db"
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS server_config (
                guild_id INTEGER PRIMARY KEY,
                prefix TEXT DEFAULT '+',
                language TEXT DEFAULT 'FR',
                welcome_channel_id INTEGER,
                welcome_message TEXT,
                leave_message TEXT,
                autorole_id INTEGER,
                log_channel_id INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS live_config (
                id INTEGER PRIMARY KEY,
                live_status TEXT DEFAULT 'Dev by Slender_0001. +aide pour les commandes'
            )
        ''')
        
        conn.commit()
        conn.close()

    def get_prefix(self, guild_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT prefix FROM server_config WHERE guild_id = ?', (guild_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else '+'

    def set_prefix(self, guild_id, prefix):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO server_config (guild_id, prefix) VALUES (?, ?)', (guild_id, prefix))
        conn.commit()
        conn.close()

    def set_welcome_message(self, guild_id, message):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO server_config (guild_id, welcome_message) VALUES (?, ?)', (guild_id, message))
        conn.commit()
        conn.close()

    def get_welcome_message(self, guild_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT welcome_message FROM server_config WHERE guild_id = ?', (guild_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def set_leave_message(self, guild_id, message):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO server_config (guild_id, leave_message) VALUES (?, ?)', (guild_id, message))
        conn.commit()
        conn.close()

    def get_leave_message(self, guild_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT leave_message FROM server_config WHERE guild_id = ?', (guild_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def set_autorole(self, guild_id, role_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO server_config (guild_id, autorole_id) VALUES (?, ?)', (guild_id, role_id))
        conn.commit()
        conn.close()

    def get_autorole(self, guild_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT autorole_id FROM server_config WHERE guild_id = ?', (guild_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def set_welcome_channel(self, guild_id, channel_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO server_config (guild_id, welcome_channel_id) VALUES (?, ?)', (guild_id, channel_id))
        conn.commit()
        conn.close()

    def get_welcome_channel(self, guild_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT welcome_channel_id FROM server_config WHERE guild_id = ?', (guild_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def set_live_status(self, status):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO live_config (id, live_status) VALUES (1, ?)', (status,))
        conn.commit()
        conn.close()

    def get_live_status(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT live_status FROM live_config WHERE id = 1')
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "Dev by Slender_0001. +aide pour les commandes"

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = ConfigDB()

    @commands.command(name='prefix')
    @admin_or_owner()
    async def change_prefix(self, ctx, new_prefix):
        if len(new_prefix) > 5:
            await ctx.send("❌ Le prefix est trop long (max 5 caractères)")
            return
        
        self.db.set_prefix(ctx.guild.id, new_prefix)
        embed = discord.Embed(
            title="✅ Prefix Changé",
            description=f"Nouveau prefix: `{new_prefix}`",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name='setwelcome')
    @admin_or_owner()
    async def set_welcome(self, ctx, *, message):
        self.db.set_welcome_message(ctx.guild.id, message)
        embed = discord.Embed(
            title="✅ Message de Bienvenue Défini",
            description=f"Message: {message}",
            color=discord.Color.green()
        )
        embed.add_field(name="Variables", value="`{user}` = Utilisateur\n`{guild}` = Serveur\n`{count}` = Nombre de membres", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='setleave')
    @admin_or_owner()
    async def set_leave(self, ctx, *, message):
        self.db.set_leave_message(ctx.guild.id, message)
        embed = discord.Embed(
            title="✅ Message de Départ Défini",
            description=f"Message: {message}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name='setautorole')
    @admin_or_owner()
    async def set_autorole(self, ctx, role: discord.Role):
        self.db.set_autorole(ctx.guild.id, role.id)
        embed = discord.Embed(
            title="✅ Rôle Automatique Défini",
            description=f"Les nouveaux membres recevront: {role.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name='setlive')
    @commands.has_permissions(administrator=True)
    async def set_live_status(self, ctx, *, description):
        if len(description) > 128:
            await ctx.send("❌ La description est trop longue (max 128 caractères)")
            return
        
        self.db.set_live_status(description)
        
        await self.bot.change_presence(activity=discord.Streaming(name=description, url="https://twitch.tv/bot"))
        
        embed = discord.Embed(
            title="✅ Statut en Live Défini",
            description=f"📡 Le bot affiche maintenant: `{description}`",
            color=discord.Color.green()
        )
        embed.add_field(name="Status Type", value="🎮 Streaming (En Live)", inline=True)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        autorole_id = self.db.get_autorole(member.guild.id)
        if autorole_id:
            role = member.guild.get_role(autorole_id)
            if role:
                await member.add_roles(role)
        
        welcome_msg = self.db.get_welcome_message(member.guild.id)
        welcome_channel_id = self.db.get_welcome_channel(member.guild.id)
        
        if welcome_msg and welcome_channel_id:
            channel = self.bot.get_channel(welcome_channel_id)
            if channel:
                msg = welcome_msg.format(
                    user=member.mention,
                    guild=member.guild.name,
                    count=member.guild.member_count
                )
                embed = discord.Embed(
                    title="👋 Bienvenue!",
                    description=msg,
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        leave_msg = self.db.get_leave_message(member.guild.id)
        
        if leave_msg:
            channel = discord.utils.get(member.guild.channels, name="general")
            if channel:
                msg = leave_msg.format(
                    user=member.mention,
                    guild=member.guild.name
                )
                embed = discord.Embed(
                    title="👋 Au Revoir",
                    description=msg,
                    color=discord.Color.orange()
                )
                await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Config(bot))
