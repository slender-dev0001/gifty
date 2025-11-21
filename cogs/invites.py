import discord
from discord.ext import commands
import sqlite3

class InvitesDB:
    def __init__(self):
        self.db_path = "invites.db"
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invites (
                inviter_id INTEGER,
                invited_id INTEGER,
                guild_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (inviter_id, invited_id, guild_id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_invite(self, inviter_id, invited_id, guild_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT OR REPLACE INTO invites (inviter_id, invited_id, guild_id) VALUES (?, ?, ?)',
            (inviter_id, invited_id, guild_id)
        )
        
        conn.commit()
        conn.close()

    def get_invites(self, user_id, guild_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM invites WHERE inviter_id = ? AND guild_id = ?', (user_id, guild_id))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0

    def get_leaderboard(self, guild_id, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT inviter_id, COUNT(*) as count 
            FROM invites 
            WHERE guild_id = ? 
            GROUP BY inviter_id 
            ORDER BY count DESC 
            LIMIT ?
        ''', (guild_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return results

class Invites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = InvitesDB()
        self.invite_cache = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.invite_cache[guild.id] = await guild.invites()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.guild.fetch_invites()
        
        if member.guild.id not in self.invite_cache:
            self.invite_cache[member.guild.id] = []
        
        try:
            invites_after = await member.guild.invites()
            invites_before = self.invite_cache.get(member.guild.id, [])
            
            for invite in invites_before:
                for inv in invites_after:
                    if invite.code == inv.code and invite.uses < inv.uses:
                        self.db.add_invite(inv.inviter.id, member.id, member.guild.id)
                        
                        embed = discord.Embed(
                            title="👋 Nouvel Invité!",
                            description=f"{member.mention} a été invité par {inv.inviter.mention}",
                            color=discord.Color.green()
                        )
                        embed.add_field(name="Invites totales", value=self.db.get_invites(inv.inviter.id, member.guild.id), inline=True)
                        
                        channel = discord.utils.get(member.guild.channels, name="logs") or discord.utils.get(member.guild.channels, name="general")
                        if channel:
                            await channel.send(embed=embed)
                        
                        break
            
            self.invite_cache[member.guild.id] = invites_after
        except:
            pass

    @commands.command(name='invites')
    async def user_invites(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        count = self.db.get_invites(member.id, ctx.guild.id)
        
        embed = discord.Embed(
            title=f"📊 Invites de {member.name}",
            description=f"Nombre d'invités: **{count}**",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        
        await ctx.send(embed=embed)

    @commands.command(name='inviteleaderboard')
    async def invite_leaderboard(self, ctx):
        leaderboard = self.db.get_leaderboard(ctx.guild.id, 10)
        
        if not leaderboard:
            await ctx.send("❌ Aucune donnée d'invitations")
            return
        
        embed = discord.Embed(
            title="🏆 Leaderboard des Invitations",
            color=discord.Color.gold()
        )
        
        leaderboard_text = ""
        for i, (user_id, count) in enumerate(leaderboard, 1):
            user = self.bot.get_user(user_id)
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
            username = user.name if user else f"ID: {user_id}"
            leaderboard_text += f"{medal} **{username}** - {count} invité(s)\n"
        
        embed.description = leaderboard_text
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Invites(bot))
