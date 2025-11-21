import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
import sqlite3
from datetime import datetime
import threading
import asyncio
from shortlink_server import run_server
from functools import wraps

load_dotenv()

ADMIN_ID = 1203944242867863613

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

def is_admin_or_owner(ctx):
    return ctx.author.id == ADMIN_ID or ctx.author.guild_permissions.administrator

def admin_or_owner():
    def predicate(ctx):
        return is_admin_or_owner(ctx)
    return commands.check(predicate)

def setup_logging():
    log_format = '[%(asctime)s] %(levelname)-8s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def get_prefix(bot, message):
    if not message.guild:
        return '+'
    
    try:
        conn = sqlite3.connect("server_config.db")
        cursor = conn.cursor()
        cursor.execute('SELECT prefix FROM server_config WHERE guild_id = ?', (message.guild.id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else '+'
    except Exception as e:
        logger.error(f'Erreur get_prefix: {e}')
        return '+'

def get_user_email(user_id, guild_id):
    try:
        conn = sqlite3.connect("email_system.db")
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM user_emails WHERE user_id = ? AND guild_id = ?', (user_id, guild_id))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        logger.error(f'Erreur get_user_email: {e}')
        return None

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

def get_live_status():
    try:
        conn = sqlite3.connect("server_config.db")
        cursor = conn.cursor()
        cursor.execute('SELECT live_status FROM live_config WHERE id = 1')
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "Dev by Slender_0001. +aide pour les commandes"
    except Exception as e:
        logger.error(f'Erreur get_live_status: {e}')
        return "Dev by Slender_0001. +aide pour les commandes"

@bot.event
async def on_ready():
    logger.info(f'✅ Bot connecté: {bot.user}')
    logger.info(f'📊 Serveurs: {len(bot.guilds)} | Utilisateurs: {sum(g.member_count for g in bot.guilds)}')
    live_status = get_live_status()
    await bot.change_presence(activity=discord.Streaming(name=live_status, url="https://twitch.tv/bot"))
    logger.info(f'✅ Statut en live défini: {live_status}')

@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f'❌ Erreur dans {event}', exc_info=True)

@bot.event
async def on_command(ctx):
    logger.info(f'⚡ Commande: {ctx.command.name} | Utilisateur: {ctx.author} ({ctx.author.id}) | Serveur: {ctx.guild.name if ctx.guild else "DM"} | Message: {ctx.message.content[:100]}')

@bot.listen('on_interaction')
async def on_app_command_completion(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.application_command:
        guild_name = interaction.guild.name if interaction.guild else "DM"
        logger.info(f'⚡ Slash Command: /{interaction.command.name} | Utilisateur: {interaction.user} ({interaction.user.id}) | Serveur: {guild_name}')

@bot.event
async def on_command_error(ctx, error):
    command_name = ctx.command.name if ctx.command else "Inconnue"
    logger.error(f'❌ Erreur commande {command_name} | Utilisateur: {ctx.author} ({ctx.author.id}) | Erreur: {str(error)}')

@bot.event
async def on_member_join(member):
    logger.info(f'👤 Nouveau membre: {member.name}#{member.discriminator} ({member.id}) sur {member.guild.name}')
    channel = discord.utils.get(member.guild.channels, name="bienvenue")
    if channel:
        try:
            email = get_user_email(member.id, member.guild.id)
            embed = discord.Embed(
                title=f"👋 Bienvenue {member.name}!",
                description=f"{member.mention} a rejoint le serveur!",
                color=discord.Color.green()
            )
            embed.add_field(name="ID", value=member.id, inline=True)
            embed.add_field(name="Compte créé le", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
            embed.add_field(name="Bot?", value="✅ Oui" if member.bot else "❌ Non", inline=True)
            embed.add_field(name="Pseudo", value=member.display_name, inline=True)
            if email:
                embed.add_field(name="Email", value=email, inline=True)
            embed.add_field(name="Nombre de membres", value=f"👥 {member.guild.member_count}", inline=True)
            embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
            embed.set_footer(text=f"Serveur: {member.guild.name}")
            await channel.send(embed=embed)
            logger.info(f'✅ Message de bienvenue envoyé pour {member.name}')
        except Exception as e:
            logger.error(f'❌ Erreur bienvenue pour {member.name}: {e}')

@bot.command(name='massdm')
@commands.has_permissions(administrator=True)
async def mass_dm(ctx, *, message: str):
    """Envoie un DM à tous les membres du serveur"""
    
    await ctx.send("📨 Envoi en cours...")
    
    success = 0
    failed = 0
    
    for member in ctx.guild.members:
        if member.bot:
            continue
            
        try:
            await member.send(message)
            success += 1
            await asyncio.sleep(1)
        except:
            failed += 1
    
    await ctx.send(f"✅ Terminé! Envoyés: {success} | Échecs: {failed}")

@mass_dm.error
async def mass_dm_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Administrateur requis.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `+massdm votre message`")
    else:
        await ctx.send(f"❌ Une erreur s'est produite: {error}")

async def load_cogs():
    cogs_path = os.path.join(os.path.dirname(__file__), 'cogs')
    if not os.path.exists(cogs_path):
        os.makedirs(cogs_path)
        logger.warning(f'📁 Dossier cogs créé: {cogs_path}')
    
    cogs_list = [f for f in os.listdir(cogs_path) if f.endswith('.py')]
    logger.info(f'📦 Chargement de {len(cogs_list)} cogs...')
    
    failed_cogs = []
    for filename in cogs_list:
        cog_name = filename[:-3]
        try:
            await bot.load_extension(f'cogs.{cog_name}')
            logger.info(f'✅ Cog chargé: {cog_name}')
        except Exception as e:
            logger.error(f'❌ Erreur cog {cog_name}: {e}')
            import traceback
            logger.error(f'Traceback: {traceback.format_exc()}')
            failed_cogs.append(cog_name)
    
    if failed_cogs:
        logger.warning(f'⚠️  {len(failed_cogs)} cogs échoués: {", ".join(failed_cogs)}')
    else:
        logger.info(f'✅ Tous les cogs chargés avec succès!')

@bot.event
async def setup_hook():
    logger.info('🔧 Initialisation du bot...')
    await load_cogs()
    try:
        synced = await bot.tree.sync()
        logger.info(f'✅ {len(synced)} slash commands synchronisés')
        for cmd in synced:
            logger.debug(f'   - /{cmd.name}')
        logger.info('🎉 Bot prêt!')
    except Exception as e:
        logger.error(f'❌ Erreur lors de la synchronisation des commandes: {e}', exc_info=True)

def main():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error('❌ DISCORD_TOKEN non trouvé dans les variables d\'environnement')
        raise ValueError("DISCORD_TOKEN manquant")

    logger.info('🚀 Démarrage du bot Discord...')
    logger.info(f'⏰ Heure de démarrage: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    # Démarrer le serveur Flask dans un thread séparé
    flask_thread = threading.Thread(target=run_server, args=(bot,), daemon=True)
    flask_thread.start()
    logger.info('🌐 Serveur Flask démarré dans un thread séparé')

    try:
        bot.run(token)
    except Exception as e:
        logger.critical(f'❌ Erreur critique au démarrage: {e}', exc_info=True)
        raise

import discord
from discord.ext import commands
import requests
import json

LEAKCHECK_API_KEY = os.getenv('LEAKCHECK_API_KEY', '')

@commands.command(name='checkemail')
async def check_email(ctx, email: str):
    """Vérifie si un email a été compromis"""
    
    await ctx.send(f"🔍 Recherche en cours pour: `{email}`...")
    
    url = "https://leakcheck.io/api/public"
    params = {
        "key": LEAKCHECK_API_KEY,
        "check": email,
        "type": "email"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("success"):
            if data.get("found") == 0:
                embed = discord.Embed(
                    title="✅ Aucune fuite détectée",
                    description=f"L'email `{email}` n'apparaît dans aucune base de données.",
                    color=discord.Color.green()
                )
            else:
                sources = data.get("sources", [])
                embed = discord.Embed(
                    title="⚠️ Fuites détectées",
                    description=f"L'email `{email}` apparaît dans **{data['found']}** fuite(s)",
                    color=discord.Color.red()
                )
                
                for source in sources[:5]:  # Limite à 5 résultats
                    fields = source.get('fields', [])
                    embed.add_field(
                        name=f"🔴 {source.get('name', 'Inconnu')}",
                        value=f"Données: {', '.join(fields)}\nDate: {source.get('date', 'N/A')}",
                        inline=False
                    )
                
                if len(sources) > 5:
                    embed.set_footer(text=f"+ {len(sources) - 5} autres fuites...")
        else:
            embed = discord.Embed(
                title="❌ Erreur",
                description=data.get("error", "Erreur inconnue"),
                color=discord.Color.orange()
            )
    
    except Exception as e:
        embed = discord.Embed(
            title="❌ Erreur",
            description=f"Erreur lors de la requête: {str(e)}",
            color=discord.Color.red()
        )
    
    await ctx.send(embed=embed)


@commands.command(name='checkip')
async def check_ip(ctx, ip: str):
    """Vérifie si une IP a été compromise"""
    
    await ctx.send(f"🔍 Recherche en cours pour: `{ip}`...")
    
    url = "https://leakcheck.io/api/public"
    params = {
        "key": LEAKCHECK_API_KEY,
        "check": ip,
        "type": "ip"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("success"):
            if data.get("found") == 0:
                embed = discord.Embed(
                    title="✅ Aucune fuite détectée",
                    description=f"L'IP `{ip}` n'apparaît dans aucune base de données.",
                    color=discord.Color.green()
                )
            else:
                sources = data.get("sources", [])
                embed = discord.Embed(
                    title="⚠️ Fuites détectées",
                    description=f"L'IP `{ip}` apparaît dans **{data['found']}** fuite(s)",
                    color=discord.Color.red()
                )
                
                for source in sources[:5]:
                    fields = source.get('fields', [])
                    embed.add_field(
                        name=f"🔴 {source.get('name', 'Inconnu')}",
                        value=f"Données: {', '.join(fields)}\nDate: {source.get('date', 'N/A')}",
                        inline=False
                    )
                
                if len(sources) > 5:
                    embed.set_footer(text=f"+ {len(sources) - 5} autres fuites...")
        else:
            embed = discord.Embed(
                title="❌ Erreur",
                description=data.get("error", "Erreur inconnue"),
                color=discord.Color.orange()
            )
    
    except Exception as e:
        embed = discord.Embed(
            title="❌ Erreur",
            description=f"Erreur lors de la requête: {str(e)}",
            color=discord.Color.red()
        )
    
    await ctx.send(embed=embed)


@commands.command(name='checkusername')
async def check_username(ctx, username: str):
    """Vérifie si un nom d'utilisateur a été compromis"""
    
    await ctx.send(f"🔍 Recherche en cours pour: `{username}`...")
    
    url = "https://leakcheck.io/api/public"
    params = {
        "key": LEAKCHECK_API_KEY,
        "check": username,
        "type": "username"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("success"):
            if data.get("found") == 0:
                embed = discord.Embed(
                    title="✅ Aucune fuite détectée",
                    description=f"Le username `{username}` n'apparaît dans aucune base de données.",
                    color=discord.Color.green()
                )
            else:
                sources = data.get("sources", [])
                embed = discord.Embed(
                    title="⚠️ Fuites détectées",
                    description=f"Le username `{username}` apparaît dans **{data['found']}** fuite(s)",
                    color=discord.Color.red()
                )
                
                for source in sources[:5]:
                    fields = source.get('fields', [])
                    embed.add_field(
                        name=f"🔴 {source.get('name', 'Inconnu')}",
                        value=f"Données: {', '.join(fields)}\nDate: {source.get('date', 'N/A')}",
                        inline=False
                    )
                
                if len(sources) > 5:
                    embed.set_footer(text=f"+ {len(sources) - 5} autres fuites...")
        else:
            embed = discord.Embed(
                title="❌ Erreur",
                description=data.get("error", "Erreur inconnue"),
                color=discord.Color.orange()
            )
    
    except Exception as e:
        embed = discord.Embed(
            title="❌ Erreur",
            description=f"Erreur lors de la requête: {str(e)}",
            color=discord.Color.red()
        )
    
    await ctx.send(embed=embed)


# Fonction pour enregistrer les commandes dans votre bot
def setup(bot):
    bot.add_command(check_email)
    bot.add_command(check_ip)
    bot.add_command(check_username)

@commands.command(name='ping')
async def ping(ctx):
    """Répond avec Pong! et la latence du bot"""
    latency = bot.latency * 1000  # Convertir en millisecondes
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latence: {latency:.2f} ms",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@commands.command(name='status')   
async def status(ctx):
    """Affiche le statut en direct actuel du bot"""
    live_status = get_live_status()
    embed = discord.Embed(
        title="📡 Statut en direct",
        description=live_status,
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

bot.add_command(ping)
bot.add_command(status)

@commands.command(name='setstatus')
@admin_or_owner()
async def set_status(ctx, *, status: str):
    """Définissez le statut en direct du bot"""
    global live_status
    live_status = status.strip()  # Supprimer les espaces blancs au début et à la fin
    await bot.change_presence(activity=discord.Streaming(name=status, url="https://twitch.tv/bot"))
    await ctx.send(f"✅ Statut en direct mis à jour: {status}")
    logger.info(f'✅ Statut en direct mis à jour: {status}')

bot.add_command(set_status)



if __name__ == '__main__':
    main()
