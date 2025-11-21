import discord
from discord import app_commands
from discord.ext import commands

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Aide complète du bot")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📚 Bot Discord Complet - Commandes",
            description="**90+ Commandes Disponibles**",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎮 **Basiques**",
            value="`+hello` • `+ping` • `+say <msg>` • `+avatar [@user]`",
            inline=False
        )
        
        embed.add_field(
            name="📊 **Slash Commands** (Modernes avec /)",
            value="`/help` • `/ping` • `/usercard [@user]` • `/leaderboard` • `/about`",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ **Informations**",
            value="`+serverinfo` • `+userinfo [@u]` • `+roleinfo <role>` • `+channelinfo [channel]` • `+stats`",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ **Modération** (Admin)",
            value="`+clear <n>` • `+kick @user` • `+ban @user` • `+unban <name>` • `+mute @user` • `+unmute @user`",
            inline=False
        )
        
        embed.add_field(
            name="🎮 **Interactions Avancées**",
            value="`+buttons` • `+select` • `+modal` (Buttons, Menus, Modales)",
            inline=False
        )
        
        embed.add_field(
            name="🎭 **Événements & Rôles**",
            value="`+autoroles <role>` • `+reactionrole <id> <emoji> <role>` • `+welcome` • `+setuplogs`",
            inline=False
        )
        
        embed.add_field(
            name="👤 **Profils & XP**",
            value="`+profile [@u]` • `+setbio <bio>` • `+balance [@u]` • `+addbal @user <n>` • `+leaderboard`",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ **Customisation Serveur** (Admin)",
            value="`+prefix <new>` • `+setwelcome <msg>` • `+setleave <msg>` • `+setautorole <role>`",
            inline=False
        )
        
        embed.add_field(
            name="👥 **Invitations**",
            value="`+invites [@user]` • `+inviteleaderboard` (Tracker d'invitations)",
            inline=False
        )
        
        embed.add_field(
            name="🎫 **Support & Tickets** (Admin)",
            value="`+ticketsystem` - Créer la base de tickets",
            inline=False
        )
        
        embed.add_field(
            name="🔐 **Vérification** (Admin)",
            value="`+setupverification` - Captcha mathématique auto",
            inline=False
        )
        
        embed.add_field(
            name="🎉 **Giveaways** (Admin)",
            value="`+giveaway <durée> <winners> <prize>` • `+giveaways` • `+endgiveaway <id>`",
            inline=False
        )
        
        embed.add_field(
            name="🎨 **Outils Créatifs**",
            value="`+qrcode <texte>` (QR Code) • `+ascii <texte>` (ASCII Art)",
            inline=False
        )
        
        embed.add_field(
            name="🎲 **Jeux & Plaisir**",
            value="`+dice` • `+flip` • `+8ball <question>`",
            inline=False
        )
        
        embed.set_footer(text="✨ Réaction-rôles • Logs complets • XP système • BD SQLite • Prefix personnalisé • Tracker d'invitations")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="slashhelp", description="Voir l'aide des slash commands")
    async def slashhelp(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📚 Slash Commands",
            description="Commandes modernes avec /",
            color=discord.Color.blue()
        )
        embed.add_field(name="/help", value="Aide complète du bot", inline=False)
        embed.add_field(name="/slashhelp", value="Voir cette aide", inline=False)
        embed.add_field(name="/ping", value="Latence du bot", inline=False)
        embed.add_field(name="/usercard", value="Voir ta carte de profil", inline=False)
        embed.add_field(name="/leaderboard", value="Top 10 des utilisateurs", inline=False)
        embed.add_field(name="/about", value="À propos du bot", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ping", description="Latence du bot")
    async def slash_ping(self, interaction: discord.Interaction):
        latence = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! {latence}ms", ephemeral=True)

    @app_commands.command(name="usercard", description="Voir ta carte de profil")
    async def usercard(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user
        embed = discord.Embed(
            title=f"📇 Profil de {user.name}",
            color=discord.Color.gold()
        )
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Créé le", value=user.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Bot?", value="✅" if user.bot else "❌", inline=True)
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="leaderboard", description="Top 10 des utilisateurs")
    async def leaderboard(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🏆 Leaderboard",
            color=discord.Color.gold()
        )
        embed.description = "Fonctionnalité bientôt disponible avec le système de profil!"
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="about", description="À propos du bot")
    async def about(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤖 À Propos",
            description="Bot Discord multifonctionnel avec des features avancées",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Version", value="2.0.0", inline=True)
        embed.add_field(name="Serveurs", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Utilisateurs", value=len(self.bot.users), inline=True)
        embed.add_field(name="Créé par", value="Ton Nom", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(SlashCommands(bot))
