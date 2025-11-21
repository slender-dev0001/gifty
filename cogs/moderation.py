import discord
from discord.ext import commands
from datetime import timedelta
import json
import os

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings_file = "guild_settings.json"
        self.warnings_file = "warnings.json"
        self.load_data()
    
    def load_data(self):
        if not os.path.exists(self.settings_file):
            with open(self.settings_file, 'w') as f:
                json.dump({}, f)
        if not os.path.exists(self.warnings_file):
            with open(self.warnings_file, 'w') as f:
                json.dump({}, f)
    
    def save_settings(self, guild_id, settings):
        with open(self.settings_file, 'r') as f:
            data = json.load(f)
        data[str(guild_id)] = settings
        with open(self.settings_file, 'w') as f:
            json.dump(data, f, indent=4)
    
    def get_settings(self, guild_id):
        with open(self.settings_file, 'r') as f:
            data = json.load(f)
        return data.get(str(guild_id), {})
    
    def add_warning(self, guild_id, user_id, reason):
        with open(self.warnings_file, 'r') as f:
            data = json.load(f)
        key = f"{guild_id}-{user_id}"
        if key not in data:
            data[key] = []
        data[key].append(reason)
        with open(self.warnings_file, 'w') as f:
            json.dump(data, f, indent=4)
        return len(data[key])
    
    def get_warnings(self, guild_id, user_id):
        with open(self.warnings_file, 'r') as f:
            data = json.load(f)
        key = f"{guild_id}-{user_id}"
        return data.get(key, [])

    @commands.command(name='clear')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if amount <= 0:
            await ctx.send("❌ Spécifie un nombre positif!")
            return
        if amount > 100:
            await ctx.send("❌ Maximum 100 messages à la fois!")
            return
        
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'✅ **{len(deleted) - 1}** messages supprimés!', delete_after=3)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Tu n'as pas la permission!")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Spécifie un nombre valide!")

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if member == ctx.author:
            await ctx.send("❌ Tu ne peux pas t'expulser toi-même!")
            return
        
        reason = reason or "Aucune raison spécifiée"
        embed = discord.Embed(
            title="⚠️ Expulsion",
            description=f"{member.mention} a été expulsé",
            color=discord.Color.orange()
        )
        embed.add_field(name="Raison", value=reason)
        embed.add_field(name="Modérateur", value=ctx.author.mention)
        
        await member.kick(reason=reason)
        await ctx.send(embed=embed)

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Tu n'as pas la permission de kick!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Mentionne un utilisateur!")

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if member == ctx.author:
            await ctx.send("❌ Tu ne peux pas te bannir toi-même!")
            return
        
        reason = reason or "Aucune raison spécifiée"
        embed = discord.Embed(
            title="🚫 Bannissement",
            description=f"{member.mention} a été banni",
            color=discord.Color.red()
        )
        embed.add_field(name="Raison", value=reason)
        embed.add_field(name="Modérateur", value=ctx.author.mention)
        
        await member.ban(reason=reason)
        await ctx.send(embed=embed)

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Tu n'as pas la permission de bannir!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Mentionne un utilisateur!")

    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member_name):
        bans = [entry async for entry in ctx.guild.audit_logs(action=discord.AuditLogAction.ban)]
        
        for entry in bans:
            if entry.target.name.lower() == member_name.lower():
                await ctx.guild.unban(entry.target)
                await ctx.send(f"✅ {entry.target.mention} a été débanni!")
                return
        
        await ctx.send("❌ Utilisateur non trouvé dans les bannissements!")

    @commands.command(name='mute')
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: int = None):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
        
        await member.add_roles(muted_role)
        embed = discord.Embed(
            title="🔇 Mute",
            description=f"{member.mention} a été mute",
            color=discord.Color.greyple()
        )
        if duration:
            embed.add_field(name="Durée", value=f"{duration} secondes")
        
        await ctx.send(embed=embed)

    @commands.command(name='unmute')
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await ctx.send(f"✅ {member.mention} a été unmute!")
        else:
            await ctx.send(f"❌ {member.mention} n'est pas mute!")
    
    @commands.command(name='embed')
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx, *, message: str):
        embed = discord.Embed(description=message, color=discord.Color.blue())
        await ctx.send(embed=embed)

    @commands.command(name='leaks')
    @commands.has_permissions(administrator=True)
    async def leaks(self, ctx):
        await ctx.send("https://cdn.discordapp.com/attachments/970483651982324510/970483652166403122/image.png")
        await ctx.message.delete()
        await ctx.send("https://cdn.discordapp.com/attachments/970483651982324510/970483652166403122/image.png")
        await ctx.message.delete()

    @commands.command(name='warn')
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        if member == ctx.author:
            await ctx.send("❌ Tu ne peux pas t'avertir toi-même!")
            return
        
        reason = reason or "Aucune raison spécifiée"
        warn_count = self.add_warning(ctx.guild.id, member.id, reason)
        
        embed = discord.Embed(
            title="⚠️ Avertissement",
            description=f"{member.mention} a reçu un avertissement",
            color=discord.Color.gold()
        )
        embed.add_field(name="Raison", value=reason)
        embed.add_field(name="Nombre d'avertissements", value=f"{warn_count}")
        embed.add_field(name="Modérateur", value=ctx.author.mention)
        
        await ctx.send(embed=embed)

    @commands.command(name='warnings')
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx, member: discord.Member):
        warnings = self.get_warnings(ctx.guild.id, member.id)
        
        if not warnings:
            await ctx.send(f"✅ {member.mention} n'a pas d'avertissements!")
            return
        
        embed = discord.Embed(
            title=f"⚠️ Avertissements de {member.name}",
            color=discord.Color.gold()
        )
        for i, warning in enumerate(warnings, 1):
            embed.add_field(name=f"Avertissement #{i}", value=warning, inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name='lock')
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        
        await ctx.send(f"🔒 {channel.mention} a été verrouillé!")

    @commands.command(name='unlock')
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = None
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        
        await ctx.send(f"🔓 {channel.mention} a été déverrouillé!")

    @commands.command(name='settings')
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx, action: str, *, value: str = None):
        settings = self.get_settings(ctx.guild.id)
        
        if action.lower() == 'view':
            if not settings:
                await ctx.send("❌ Aucun paramètre configuré!")
                return
            
            embed = discord.Embed(title="⚙️ Paramètres du serveur", color=discord.Color.blue())
            for key, val in settings.items():
                embed.add_field(name=key, value=val, inline=False)
            await ctx.send(embed=embed)
        
        elif action.lower() == 'set':
            if not value:
                await ctx.send("❌ Spécifie une clé et une valeur! Usage: +settings set <clé> <valeur>")
                return
            
            parts = value.split(' ', 1)
            if len(parts) < 2:
                await ctx.send("❌ Usage: +settings set <clé> <valeur>")
                return
            
            key, val = parts
            settings[key] = val
            self.save_settings(ctx.guild.id, settings)
            await ctx.send(f"✅ {key} défini à {val}!")
        
        elif action.lower() == 'remove':
            if value not in settings:
                await ctx.send("❌ Cette clé n'existe pas!")
                return
            
            del settings[value]
            self.save_settings(ctx.guild.id, settings)
            await ctx.send(f"✅ {value} a été supprimé!")
        
        else:
            await ctx.send("❌ Actions: `view`, `set`, `remove`")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
