import discord
from discord.ext import commands
from discord import ui

reaction_roles = {}

class RoleButton(ui.View):
    def __init__(self, role_id, timeout=None):
        super().__init__(timeout=timeout)
        self.role_id = role_id

    @ui.button(label="Cliquez pour obtenir le rôle", style=discord.ButtonStyle.blurple)
    async def role_button(self, interaction: discord.Interaction, button: ui.Button):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message("❌ Le rôle n'existe pas", ephemeral=True)
            return
        
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"❌ Rôle {role.mention} retiré", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Rôle {role.mention} ajouté", ephemeral=True)

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild.channels, name="bienvenue")
        if channel:
            embed = discord.Embed(
                title=f"🎉 Bienvenue {member.name}!",
                description=f"{member.mention} a rejoint le serveur!",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
            embed.add_field(name="Membres", value=member.guild.member_count, inline=False)
            await channel.send(embed=embed)

    @commands.command(name='autoroles')
    @commands.has_permissions(manage_roles=True)
    async def autoroles(self, ctx, *, role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send(f"❌ Le rôle '{role_name}' n'existe pas")
            return
        
        if ctx.guild.id not in reaction_roles:
            reaction_roles[ctx.guild.id] = {}
        
        reaction_roles[ctx.guild.id][role.id] = role_name
        
        embed = discord.Embed(
            title="🎭 Auto-Rôles",
            description=f"Clique sur le bouton pour obtenir le rôle {role.mention}",
            color=discord.Color.blurple()
        )
        
        message = await ctx.send(embed=embed, view=RoleButton(role.id))
        await ctx.send(f"✅ Auto-rôle défini pour {role.mention}")

    @commands.command(name='reactionrole')
    @commands.has_permissions(manage_roles=True)
    async def reactionrole(self, ctx, message_id: int, emoji: str, *, role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send(f"❌ Le rôle '{role_name}' n'existe pas")
            return
        
        try:
            message = await ctx.channel.fetch_message(message_id)
        except:
            await ctx.send("❌ Message non trouvé")
            return
        
        try:
            await message.add_reaction(emoji)
        except:
            await ctx.send("❌ Emoji invalide")
            return
        
        if ctx.guild.id not in reaction_roles:
            reaction_roles[ctx.guild.id] = {}
        
        if message_id not in reaction_roles[ctx.guild.id]:
            reaction_roles[ctx.guild.id][message_id] = {}
        
        reaction_roles[ctx.guild.id][message_id][emoji] = role.id
        
        await ctx.send(f"✅ Réaction rôle définie: {emoji} → {role.mention}")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        
        if payload.guild_id not in reaction_roles:
            return
        
        if payload.message_id not in reaction_roles[payload.guild_id]:
            return
        
        emoji_dict = reaction_roles[payload.guild_id][payload.message_id]
        if str(payload.emoji) not in emoji_dict:
            return
        
        role_id = emoji_dict[str(payload.emoji)]
        role = guild.get_role(role_id)
        
        if role:
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        
        if payload.guild_id not in reaction_roles:
            return
        
        if payload.message_id not in reaction_roles[payload.guild_id]:
            return
        
        emoji_dict = reaction_roles[payload.guild_id][payload.message_id]
        if str(payload.emoji) not in emoji_dict:
            return
        
        role_id = emoji_dict[str(payload.emoji)]
        role = guild.get_role(role_id)
        
        if role:
            await member.remove_roles(role)

    @commands.command(name='welcome')
    async def welcome(self, ctx):
        embed = discord.Embed(
            title="👋 Bienvenue sur notre serveur!",
            description="Bon pour un message personnalisé à envoyer dans le canal bienvenue",
            color=discord.Color.gold()
        )
        embed.add_field(name="📋 Règles", value="Respectez tout le monde", inline=False)
        embed.add_field(name="💬 Channels", value="Explore les différents canaux", inline=False)
        embed.add_field(name="👥 Rôles", value="Obtiens tes rôles automatiquement", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Events(bot))
