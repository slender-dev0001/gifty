import discord
from discord.ext import commands
from datetime import datetime

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_logs_channel(self, guild):
        return discord.utils.get(guild.channels, name="logs") or discord.utils.get(guild.channels, name="mod-logs")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        logs_channel = self.get_logs_channel(member.guild)
        if logs_channel:
            embed = discord.Embed(
                title="👋 Utilisateur rejoins",
                description=f"{member.mention} a rejoint le serveur",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Utilisateur", value=f"{member} ({member.id})", inline=False)
            embed.add_field(name="Compte créé le", value=member.created_at.strftime("%d/%m/%Y %H:%M"), inline=False)
            embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
            
            await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        logs_channel = self.get_logs_channel(member.guild)
        if logs_channel:
            embed = discord.Embed(
                title="👋 Utilisateur parti",
                description=f"{member.mention} a quitté le serveur",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Utilisateur", value=f"{member} ({member.id})", inline=False)
            embed.add_field(name="Serveur depuis", value=member.joined_at.strftime("%d/%m/%Y %H:%M") if member.joined_at else "N/A", inline=False)
            embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
            
            await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        logs_channel = self.get_logs_channel(guild)
        if logs_channel:
            try:
                async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
                    embed = discord.Embed(
                        title="🚫 Bannissement",
                        description=f"{user.mention} a été banni",
                        color=discord.Color.red(),
                        timestamp=datetime.now()
                    )
                    embed.add_field(name="Utilisateur", value=f"{user} ({user.id})", inline=False)
                    embed.add_field(name="Modérateur", value=entry.user.mention, inline=False)
                    embed.add_field(name="Raison", value=entry.reason or "Aucune raison", inline=False)
                    embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
                    
                    await logs_channel.send(embed=embed)
            except:
                pass

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        logs_channel = self.get_logs_channel(guild)
        if logs_channel:
            embed = discord.Embed(
                title="✅ Débannissement",
                description=f"{user.mention} a été débanni",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Utilisateur", value=f"{user} ({user.id})", inline=False)
            embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
            
            await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        
        logs_channel = self.get_logs_channel(message.guild)
        if logs_channel:
            embed = discord.Embed(
                title="🗑️ Message supprimé",
                description=f"Message de {message.author.mention} supprimé dans {message.channel.mention}",
                color=discord.Color.greyple(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Auteur", value=message.author.mention, inline=True)
            embed.add_field(name="Canal", value=message.channel.mention, inline=True)
            embed.add_field(name="Contenu", value=message.content[:1024] or "[Média/Embed]", inline=False)
            
            await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        
        logs_channel = self.get_logs_channel(before.guild)
        if logs_channel:
            embed = discord.Embed(
                title="✏️ Message modifié",
                description=f"Message de {before.author.mention} modifié dans {before.channel.mention}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Auteur", value=before.author.mention, inline=True)
            embed.add_field(name="Canal", value=before.channel.mention, inline=True)
            embed.add_field(name="Avant", value=before.content[:512] or "[Média/Embed]", inline=False)
            embed.add_field(name="Après", value=after.content[:512] or "[Média/Embed]", inline=False)
            
            await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        logs_channel = self.get_logs_channel(before.guild)
        if not logs_channel:
            return
        
        if before.nick != after.nick:
            embed = discord.Embed(
                title="📝 Surnom changé",
                description=f"{after.mention} a changé de surnom",
                color=discord.Color.blurple(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Avant", value=before.nick or "Aucun", inline=True)
            embed.add_field(name="Après", value=after.nick or "Aucun", inline=True)
            
            await logs_channel.send(embed=embed)

    @commands.command(name='setuplogs')
    @commands.has_permissions(manage_guild=True)
    async def setup_logs(self, ctx):
        try:
            logs_channel = await ctx.guild.create_text_channel(
                name="logs",
                topic="📋 Logs du serveur"
            )
            embed = discord.Embed(
                title="✅ Canal de logs créé",
                description=f"Les logs seront envoyés dans {logs_channel.mention}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except:
            await ctx.send("❌ Erreur lors de la création du canal")

async def setup(bot):
    await bot.add_cog(Logs(bot))
