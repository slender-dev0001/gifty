import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import random
import sqlite3
import secrets
from urllib.parse import urlparse
import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv('BASE_URL', 'https://gifty.up.railway.app')

class AllSlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hello", description="Salut!")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Bonjour {interaction.user.mention}! 👋', ephemeral=True)

    @app_commands.command(name="say", description="Répéter un message")
    async def say(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message(message)

    @app_commands.command(name="avatar", description="Afficher l'avatar d'un utilisateur")
    async def avatar(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user
        embed = discord.Embed(
            title=f"Avatar de {user}",
            color=discord.Color.blue()
        )
        embed.set_image(url=user.avatar.url if user.avatar else None)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="clear", description="Supprimer des messages (Admin)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        if amount <= 0:
            await interaction.response.send_message("❌ Spécifie un nombre positif!", ephemeral=True)
            return
        if amount > 100:
            await interaction.response.send_message("❌ Maximum 100 messages à la fois!", ephemeral=True)
            return
        
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f'✅ **{len(deleted)}** messages supprimés!', ephemeral=True)

    @app_commands.command(name="kick", description="Expulser un utilisateur (Admin)")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        if member == interaction.user:
            await interaction.response.send_message("❌ Tu ne peux pas t'expulser toi-même!", ephemeral=True)
            return
        
        reason = reason or "Aucune raison spécifiée"
        embed = discord.Embed(
            title="⚠️ Expulsion",
            description=f"{member.mention} a été expulsé",
            color=discord.Color.orange()
        )
        embed.add_field(name="Raison", value=reason)
        embed.add_field(name="Modérateur", value=interaction.user.mention)
        
        await member.kick(reason=reason)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ban", description="Bannir un utilisateur (Admin)")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        if member == interaction.user:
            await interaction.response.send_message("❌ Tu ne peux pas te bannir toi-même!", ephemeral=True)
            return
        
        reason = reason or "Aucune raison spécifiée"
        embed = discord.Embed(
            title="🚫 Bannissement",
            description=f"{member.mention} a été banni",
            color=discord.Color.red()
        )
        embed.add_field(name="Raison", value=reason)
        embed.add_field(name="Modérateur", value=interaction.user.mention)
        
        await member.ban(reason=reason)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unban", description="Débannir un utilisateur (Admin)")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, member_name: str):
        bans = [entry async for entry in interaction.guild.audit_logs(action=discord.AuditLogAction.ban)]
        
        for entry in bans:
            if entry.target.name.lower() == member_name.lower():
                await interaction.guild.unban(entry.target)
                await interaction.response.send_message(f"✅ {entry.target.mention} a été débanni!", ephemeral=True)
                return
        
        await interaction.response.send_message("❌ Utilisateur non trouvé dans les bannissements!", ephemeral=True)

    @app_commands.command(name="mute", description="Rendre muet un utilisateur (Admin)")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration: int = None):
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        
        if not muted_role:
            muted_role = await interaction.guild.create_role(name="Muted")
        
        await member.add_roles(muted_role)
        embed = discord.Embed(
            title="🔇 Mute",
            description=f"{member.mention} a été mute",
            color=discord.Color.greyple()
        )
        if duration:
            embed.add_field(name="Durée", value=f"{duration} secondes")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="unmute", description="Retirer le mute d'un utilisateur (Admin)")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        
        if muted_role and muted_role in member.roles:
            await member.remove_roles(muted_role)
            await interaction.response.send_message(f"✅ {member.mention} a été unmute!", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ {member.mention} n'est pas mute!", ephemeral=True)

    @app_commands.command(name="serverinfo", description="Informations du serveur")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(
            title=f"📊 {guild.name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="ID", value=guild.id, inline=True)
        embed.add_field(name="Membres", value=f"👥 {guild.member_count}", inline=True)
        embed.add_field(name="Salons", value=f"#️⃣ {len(guild.channels)}", inline=True)
        embed.add_field(name="Rôles", value=f"🏷️ {len(guild.roles)}", inline=True)
        embed.add_field(name="Créé le", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Propriétaire", value=guild.owner.mention, inline=True)
        embed.add_field(name="Niveau de vérification", value=str(guild.verification_level), inline=True)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="userinfo", description="Informations d'un utilisateur")
    async def userinfo(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user
        embed = discord.Embed(
            title=f"👤 {user}",
            color=discord.Color.blue()
        )
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Mention", value=user.mention, inline=True)
        embed.add_field(name="Compte créé", value=user.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Bot?", value="✅ Oui" if user.bot else "❌ Non", inline=True)
        
        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="roleinfo", description="Informations d'un rôle")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        embed = discord.Embed(
            title=f"🏷️ {role.name}",
            color=role.color
        )
        embed.add_field(name="ID", value=role.id, inline=True)
        embed.add_field(name="Position", value=role.position, inline=True)
        embed.add_field(name="Créé le", value=role.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Mentalité", value="✅ Oui" if role.mentionable else "❌ Non", inline=True)
        embed.add_field(name="Géré par bot", value="✅ Oui" if role.managed else "❌ Non", inline=True)
        embed.add_field(name="Couleur", value=str(role.color), inline=True)
        embed.add_field(name="Membres", value=len(role.members), inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="channelinfo", description="Informations d'un salon")
    async def channelinfo(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        channel = channel or interaction.channel
        embed = discord.Embed(
            title=f"#️⃣ {channel.name}",
            color=discord.Color.purple()
        )
        embed.add_field(name="ID", value=channel.id, inline=True)
        embed.add_field(name="Type", value="Texte", inline=True)
        embed.add_field(name="Créé le", value=channel.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Sujet", value=channel.topic or "Aucun", inline=False)
        embed.add_field(name="NSFW", value="✅ Oui" if channel.is_nsfw() else "❌ Non", inline=True)
        
        if channel.slowmode_delay > 0:
            embed.add_field(name="Mode lent", value=f"{channel.slowmode_delay}s", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="stats", description="Statistiques du bot")
    async def stats(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📈 Statistiques du Bot",
            color=discord.Color.green()
        )
        embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Serveurs", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Utilisateurs", value=len(self.bot.users), inline=True)
        embed.add_field(name="Extensions chargées", value=len(self.bot.cogs), inline=True)
        embed.add_field(name="Version", value="1.0.0", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="createlink", description="Créer un lien court")
    async def createlink(self, interaction: discord.Interaction, url: str):
        try:
            result = urlparse(url)
            if not all([result.scheme in ['http', 'https'], result.netloc]):
                embed = discord.Embed(
                    title="❌ URL invalide",
                    description="Veuillez fournir une URL HTTPS valide (ex: https://discord.com)",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            short_id = secrets.token_urlsafe(4)
            
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO custom_links (id, original_url, user_id, guild_id)
                VALUES (?, ?, ?, ?)
            ''', (short_id, url, interaction.user.id, interaction.guild.id))
            conn.commit()
            conn.close()

            short_url = f"{BASE_URL}/link/{short_id}"
            embed = discord.Embed(
                title="✅ Lien créé avec succès",
                color=discord.Color.green()
            )
            embed.add_field(name="ID du lien", value=f"`{short_id}`", inline=False)
            embed.add_field(name="Lien court", value=f"`{short_url}`", inline=False)
            embed.add_field(name="URL originale", value=url, inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la création du lien: {e}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="getlink", description="Récupérer un lien court")
    async def getlink(self, interaction: discord.Interaction, short_id: str):
        try:
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT original_url, user_id, created_at, clicks
                FROM custom_links
                WHERE id = ?
            ''', (short_id,))
            
            result = cursor.fetchone()
            if not result:
                embed = discord.Embed(
                    title="❌ Lien non trouvé",
                    description=f"Le lien `{short_id}` n'existe pas",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                conn.close()
                return

            original_url, user_id, created_at, clicks = result
            
            cursor.execute('''
                UPDATE custom_links
                SET clicks = clicks + 1
                WHERE id = ?
            ''', (short_id,))
            conn.commit()
            conn.close()

            user = await self.bot.fetch_user(user_id)
            short_url = f"{BASE_URL}/link/{short_id}"
            embed = discord.Embed(
                title="🔗 Lien trouvé",
                color=discord.Color.blue()
            )
            embed.add_field(name="ID", value=f"`{short_id}`", inline=False)
            embed.add_field(name="Lien court", value=f"`{short_url}`", inline=False)
            embed.add_field(name="URL", value=original_url, inline=False)
            embed.add_field(name="Créé par", value=user.mention, inline=True)
            embed.add_field(name="Clics", value=clicks + 1, inline=True)
            embed.add_field(name="Créé le", value=created_at, inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la récupération du lien: {e}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="mylinks", description="Voir vos liens courts")
    async def mylinks(self, interaction: discord.Interaction):
        try:
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, original_url, clicks, created_at
                FROM custom_links
                WHERE user_id = ? AND guild_id = ?
                ORDER BY created_at DESC
            ''', (interaction.user.id, interaction.guild.id))
            
            links = cursor.fetchall()
            conn.close()

            if not links:
                embed = discord.Embed(
                    title="📭 Aucun lien",
                    description="Vous n'avez créé aucun lien dans ce serveur",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            embed = discord.Embed(
                title="🔗 Vos liens",
                color=discord.Color.blue()
            )
            
            for short_id, url, clicks, created_at in links:
                short_url = f"{BASE_URL}/link/{short_id}"
                embed.add_field(
                    name=f"`{short_id}`",
                    value=f"**Lien:** {short_url}\n**Cible:** {url}\n**Clics:** {clicks}",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la récupération de vos liens: {e}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="linkvisits", description="Voir les visiteurs authentifiés (OAuth2)")
    async def linkvisits(self, interaction: discord.Interaction, short_id: str):
        try:
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id FROM custom_links WHERE id = ?
            ''', (short_id,))
            
            link_result = cursor.fetchone()
            if not link_result:
                embed = discord.Embed(
                    title="❌ Lien non trouvé",
                    description=f"Le lien `{short_id}` n'existe pas",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                conn.close()
                return
            
            link_owner_id = link_result[0]
            if link_owner_id != interaction.user.id:
                embed = discord.Embed(
                    title="❌ Accès refusé",
                    description="Vous n'êtes pas le propriétaire de ce lien",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                conn.close()
                return
            
            cursor.execute('''
                SELECT visitor_id, visitor_name, ip_address, browser, device_type, country, region, city, timestamp
                FROM link_visits
                WHERE short_id = ?
                ORDER BY timestamp DESC
            ''', (short_id,))
            
            visits = cursor.fetchall()
            conn.close()
            
            if not visits:
                embed = discord.Embed(
                    title="📭 Aucune visite",
                    description=f"Le lien `{short_id}` n'a pas encore reçu de visite authentifiée",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            embed = discord.Embed(
                title=f"📊 Visites du lien `{short_id}`",
                description=f"Total: {len(visits)} visite(s)",
                color=discord.Color.blue()
            )
            
            for idx, (visitor_id, visitor_name, ip_address, browser, device_type, country, region, city, timestamp) in enumerate(visits[:10], 1):
                visitor_info = f"**{visitor_name}** (`{visitor_id}`)\n"
                visitor_info += f"📱 {device_type} | 🌐 {browser}\n"
                visitor_info += f"📍 {city}, {region}, {country}\n"
                visitor_info += f"🔗 {ip_address}"
                
                embed.add_field(
                    name=f"Visite #{idx}",
                    value=visitor_info,
                    inline=False
                )
            
            if len(visits) > 10:
                embed.set_footer(text=f"Affichage des 10 premières visites sur {len(visits)}")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la récupération des visites: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="searchip", description="Géolocalisation d'une IP")
    async def searchip(self, interaction: discord.Interaction, ip: str):
        try:
            await interaction.response.defer(ephemeral=True)
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(f'http://ip-api.com/json/{ip}?lang=fr', timeout=5, headers=headers)
            
            if response.status_code != 200:
                embed = discord.Embed(
                    title="❌ Erreur",
                    description=f"Erreur API (Status: {response.status_code})\nEssayez dans quelques secondes",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            data = response.json()
            
            if data.get('status') != 'success':
                embed = discord.Embed(
                    title="❌ IP Invalide",
                    description=f"L'IP `{ip}` n'est pas valide ou introuvable",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            embed = discord.Embed(
                title=f"🔍 Résultats pour l'IP: {ip}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(name="🌍 Pays", value=f"{data.get('country', 'Inconnu')}", inline=True)
            embed.add_field(name="🏙️ Ville", value=f"{data.get('city', 'Inconnu')}", inline=True)
            embed.add_field(name="📍 Région", value=f"{data.get('regionName', 'Inconnu')}", inline=True)
            
            embed.add_field(name="🕐 Fuseau horaire", value=f"{data.get('timezone', 'Inconnu')}", inline=False)
            embed.add_field(name="📌 Coordonnées GPS", value=f"Latitude: {data.get('lat', 'N/A')}\nLongitude: {data.get('lon', 'N/A')}", inline=False)
            embed.add_field(name="🔗 FAI (Fournisseur)", value=f"{data.get('isp', 'Inconnu')}", inline=True)
            embed.add_field(name="🏢 Organisation", value=f"{data.get('org', 'Inconnu')}", inline=True)
            embed.add_field(name="💾 Code Pays", value=f"{data.get('countryCode', 'XX')}", inline=True)
            
            embed.set_footer(text="Recherche d'IP | Alimenté par ip-api.com")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="useroslint", description="Lookup OSINT par ID Discord (résultats en DM)")
    async def useroslint(self, interaction: discord.Interaction, user_id: str):
        try:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("🔍 Recherche OSINT en cours... Les résultats vous seront envoyés en DM", ephemeral=True)
            
            try:
                user = await self.bot.fetch_user(int(user_id))
            except:
                embed = discord.Embed(
                    title="❌ Utilisateur non trouvé",
                    description=f"L'ID Discord `{user_id}` n'existe pas",
                    color=discord.Color.red()
                )
                await interaction.user.send(embed=embed)
                return
            
            results_found = False
            embed = discord.Embed(
                title=f"🔍 Résultats OSINT: {user.name} ({user_id})",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="👤 Profil Discord",
                value=f"**Pseudo:** {user.name}\n**ID:** {user_id}\n**Créé le:** {user.created_at.strftime('%d/%m/%Y')}\n**Bot:** {'✅ Oui' if user.bot else '❌ Non'}",
                inline=False
            )
            
            if user.avatar:
                embed.set_thumbnail(url=user.avatar.url)
            
            results_found = True
            
            try:
                username_search = user.name.lower()
                found_accounts = []
                
                accounts_config = {
                    'twitter': f'https://twitter.com/search?q={user.name}',
                    'instagram': f'https://instagram.com/{username_search}',
                    'github': f'https://github.com/{username_search}',
                    'reddit': f'https://reddit.com/user/{username_search}',
                    'tiktok': f'https://tiktok.com/@{username_search}',
                    'youtube': f'https://youtube.com/results?search_query={user.name}',
                    'twitch': f'https://twitch.tv/{username_search}',
                    'linkedin': f'https://linkedin.com/in/{username_search}'
                }
                
                for site, url in accounts_config.items():
                    try:
                        if site == 'github':
                            response = requests.get(f'https://api.github.com/users/{username_search}', timeout=3)
                            if response.status_code == 200:
                                data = response.json()
                                found_accounts.append(f'[{site.capitalize()}]({url}) - {data.get("followers", 0)} followers')
                        elif site in ['twitter', 'youtube']:
                            found_accounts.append(f'[{site.capitalize()}]({url})')
                        else:
                            response = requests.head(url, timeout=3, allow_redirects=True)
                            if response.status_code < 404:
                                found_accounts.append(f'[{site.capitalize()}]({url})')
                    except:
                        pass
                
                if found_accounts:
                    embed.add_field(
                        name="🌐 Comptes Trouvés",
                        value=" • ".join(found_accounts),
                        inline=False
                    )
            except:
                pass
            
            try:
                if user.name:
                    response = requests.get(
                        f'https://api.epieos.com/email-finder?name={user.name}',
                        timeout=5
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('email'):
                            email_found = data.get('email')
                            confidence = data.get('confidence', 'N/A')
                            embed.add_field(
                                name="📧 Email Probable",
                                value=f"`{email_found}`\n**Confiance:** {confidence}%",
                                inline=False
                            )
                            
                            try:
                                hibp_response = requests.get(
                                    f'https://haveibeenpwned.com/api/v3/breachedaccount/{email_found}',
                                    headers={'User-Agent': 'Discord Bot'},
                                    timeout=5
                                )
                                if hibp_response.status_code == 200:
                                    breaches = hibp_response.json()
                                    breach_names = [b['Name'] for b in breaches[:5]]
                                    embed.add_field(
                                        name="⚠️ Fuites de Données",
                                        value=f"Trouvé dans {len(breaches)} fuite(s):\n" + "\n".join(breach_names),
                                        inline=False
                                    )
                            except:
                                pass
            except:
                pass
            
            try:
                response = requests.get(
                    f'https://nominatim.openstreetmap.org/search?q={user.name}&format=json&limit=3',
                    headers={'User-Agent': 'Discord Bot'},
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        locations = [f"{d.get('display_name', 'Unknown')}" for d in data[:2]]
                        if locations:
                            embed.add_field(
                                name="📍 Lieux Publics Associés",
                                value="\n".join(locations),
                                inline=False
                            )
            except:
                pass
            
            embed.add_field(
                name="⚠️ Avertissement Légal",
                value="Ces données sont publiques. Respect de la vie privée obligatoire.",
                inline=False
            )
            embed.set_footer(text="Discord OSINT Lookup | Données de sources publiques")
            
            await interaction.user.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la recherche: {str(e)}",
                color=discord.Color.red()
            )
            try:
                await interaction.user.send(embed=embed)
            except:
                await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="searchname", description="Recherche OSINT par nom (résultats en DM)")
    async def searchname(self, interaction: discord.Interaction, firstname: str, lastname: str):
        try:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("🔍 Recherche OSINT en cours... Les résultats vous seront envoyés en DM", ephemeral=True)
            
            results_found = False
            embed = discord.Embed(
                title=f"🔍 Résultats OSINT: {firstname} {lastname}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            email_found = None
            
            email_patterns = [
                f"{firstname.lower()}.{lastname.lower()}@gmail.com",
                f"{firstname.lower()}{lastname.lower()}@gmail.com",
                f"{firstname[0].lower()}{lastname.lower()}@gmail.com",
                f"{firstname.lower()}.{lastname.lower()}@outlook.com",
                f"{firstname.lower()}{lastname.lower()}@outlook.com",
                f"{firstname.lower()}.{lastname.lower()}@yahoo.com",
                f"{firstname.lower()}{lastname.lower()}@yahoo.com",
                f"{firstname.lower()}.{lastname.lower()}@hotmail.com",
                f"{firstname.lower()}@{lastname.lower()}.com",
            ]
            
            breached_emails = []
            for email in email_patterns:
                try:
                    hibp_response = requests.get(
                        f'https://haveibeenpwned.com/api/v3/breachedaccount/{email}',
                        headers={'User-Agent': 'Discord Bot OSINT'},
                        timeout=5
                    )
                    if hibp_response.status_code == 200:
                        breaches = hibp_response.json()
                        breach_count = len(breaches)
                        breached_emails.append((email, breach_count))
                    time.sleep(1)
                except:
                    pass
            
            if breached_emails:
                emails_text = "\n".join([f"`{e[0]}` - **{e[1]} fuite(s)**" for e in breached_emails])
                embed.add_field(
                    name="📧 Emails Trouvés dans les Fuites",
                    value=emails_text,
                    inline=False
                )
                results_found = True
            else:
                embed.add_field(
                    name="📧 Emails",
                    value="❌ Aucun email trouvé dans les bases de données compromises",
                    inline=False
                )
                results_found = True
            
            username_search = firstname.lower() + lastname.lower()
            found_accounts = []
            
            username_variants = [
                firstname.lower() + lastname.lower(),
                firstname.lower() + "." + lastname.lower(),
                firstname[0].lower() + lastname.lower(),
                firstname.lower() + lastname[0].lower()
            ]
            
            for username in username_variants:
                try:
                    response = requests.get(f'https://api.github.com/users/{username}', timeout=3)
                    if response.status_code == 200:
                        data = response.json()
                        github_url = data.get('html_url', f'https://github.com/{username}')
                        found_accounts.append((f'[🐙 GitHub]({github_url})', username, 0))
                        break
                except:
                    pass
            
            base_checks = {
                'twitter': lambda u: (f'https://twitter.com/{u}', None),
                'instagram': lambda u: (f'https://instagram.com/{u}', None),
                'reddit': lambda u: (f'https://reddit.com/user/{u}', f'https://www.reddit.com/user/{u}/about.json'),
                'tiktok': lambda u: (f'https://tiktok.com/@{u}', None),
                'twitch': lambda u: (f'https://twitch.tv/{u}', None),
                'youtube': lambda u: (f'https://youtube.com/@{u}', None),
            }
            
            for site, url_func in base_checks.items():
                for username in username_variants:
                    try:
                        url, api_url = url_func(username)
                        if site == 'reddit' and api_url:
                            response = requests.get(api_url, headers={'User-Agent': 'Discord Bot'}, timeout=3)
                            if response.status_code == 200:
                                found_accounts.append((f'[🔴 {site.capitalize()}]({url})', username, 0))
                                break
                        else:
                            response = requests.head(url, timeout=3, allow_redirects=True)
                            if response.status_code < 404:
                                found_accounts.append((f'[🌐 {site.capitalize()}]({url})', username, 0))
                                break
                    except:
                        pass
            
            if found_accounts:
                accounts_text = " • ".join([acc[0] for acc in found_accounts[:8]])
                embed.add_field(
                    name="🌐 Comptes Trouvés",
                    value=accounts_text,
                    inline=False
                )
                results_found = True
            
            if not results_found:
                embed.add_field(
                    name="📭 Aucun Résultat",
                    value="Aucune information trouvée pour cette personne",
                    inline=False
                )
            
            embed.add_field(
                name="⚠️ Avertissement Légal",
                value="Ces données sont publiques. Respect de la vie privée obligatoire.",
                inline=False
            )
            embed.set_footer(text="OSINT Search | Données de sources publiques")
            
            await interaction.user.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la recherche: {str(e)}",
                color=discord.Color.red()
            )
            try:
                await interaction.user.send(embed=embed)
            except:
                await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="useroslint", description="Recherche OSINT par Discord ID (résultats en DM)")
    async def useroslint(self, interaction: discord.Interaction, user_id: str):
        try:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("🔍 Recherche OSINT en cours... Les résultats vous seront envoyés en DM", ephemeral=True)
            
            try:
                user_id_int = int(user_id)
            except:
                embed = discord.Embed(
                    title="❌ ID Invalide",
                    description="L'ID Discord doit être un nombre",
                    color=discord.Color.red()
                )
                await interaction.user.send(embed=embed)
                return
            
            try:
                user = await self.bot.fetch_user(user_id_int)
            except:
                embed = discord.Embed(
                    title="❌ Utilisateur Non Trouvé",
                    description=f"L'utilisateur avec l'ID `{user_id}` n'existe pas",
                    color=discord.Color.red()
                )
                await interaction.user.send(embed=embed)
                return
            
            results_found = False
            embed = discord.Embed(
                title=f"🔍 OSINT Discord: {user}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="👤 Informations Discord",
                value=f"**Username:** {user.name}\n**ID:** `{user.id}`\n**Created:** {user.created_at.strftime('%d/%m/%Y')}",
                inline=False
            )
            
            if user.avatar:
                embed.set_thumbnail(url=user.avatar.url)
            
            results_found = True
            
            email_found = None
            
            email_patterns = [
                f"{user.name.lower()}@gmail.com",
                f"{user.name.lower().replace(' ', '.')}@gmail.com",
                f"{user.name.lower().replace(' ', '')}@gmail.com",
                f"{user.name.lower()}@outlook.com",
                f"{user.name.lower().replace(' ', '')}@outlook.com",
                f"{user.name.lower()}@yahoo.com",
                f"{user.name.lower().replace(' ', '')}@yahoo.com",
                f"{user.name.lower()}@hotmail.com",
            ]
            
            for email in email_patterns:
                try:
                    hibp_response = requests.get(
                        f'https://haveibeenpwned.com/api/v3/breachedaccount/{email}',
                        headers={'User-Agent': 'Discord Bot'},
                        timeout=5
                    )
                    if hibp_response.status_code == 200:
                        email_found = email
                        embed.add_field(
                            name="📧 Email Trouvé",
                            value=f"`{email_found}`",
                            inline=False
                        )
                        break
                except:
                    pass
            
            if email_found:
                try:
                    hibp_response = requests.get(
                        f'https://haveibeenpwned.com/api/v3/breachedaccount/{email_found}',
                        headers={'User-Agent': 'Discord Bot'},
                        timeout=5
                    )
                    if hibp_response.status_code == 200:
                        breaches = hibp_response.json()
                        breach_names = [b['Name'] for b in breaches[:5]]
                        embed.add_field(
                            name="⚠️ Fuites de Données",
                            value=f"Trouvé dans {len(breaches)} fuite(s):\n" + "\n".join(breach_names),
                            inline=False
                        )
                except:
                    pass
            
            username_variants = [
                user.name.lower(),
                user.name.lower().replace(" ", ""),
                user.name.lower().replace("_", ""),
            ]
            
            found_accounts = []
            
            for username in username_variants:
                try:
                    response = requests.get(f'https://api.github.com/users/{username}', timeout=3)
                    if response.status_code == 200:
                        data = response.json()
                        github_url = data.get('html_url', f'https://github.com/{username}')
                        found_accounts.append(f'[🐙 GitHub]({github_url})')
                        break
                except:
                    pass
            
            base_checks = {
                'twitter': lambda u: (f'https://twitter.com/{u}', None),
                'instagram': lambda u: (f'https://instagram.com/{u}', None),
                'reddit': lambda u: (f'https://reddit.com/user/{u}', f'https://www.reddit.com/user/{u}/about.json'),
                'tiktok': lambda u: (f'https://tiktok.com/@{u}', None),
                'twitch': lambda u: (f'https://twitch.tv/{u}', None),
                'youtube': lambda u: (f'https://youtube.com/@{u}', None),
            }
            
            for site, url_func in base_checks.items():
                for username in username_variants:
                    try:
                        url, api_url = url_func(username)
                        if site == 'reddit' and api_url:
                            response = requests.get(api_url, headers={'User-Agent': 'Discord Bot'}, timeout=3)
                            if response.status_code == 200:
                                found_accounts.append(f'[🔴 {site.capitalize()}]({url})')
                                break
                        else:
                            response = requests.head(url, timeout=3, allow_redirects=True)
                            if response.status_code < 404:
                                found_accounts.append(f'[🌐 {site.capitalize()}]({url})')
                                break
                    except:
                        pass
            
            if found_accounts:
                accounts_text = " • ".join(found_accounts[:8])
                embed.add_field(
                    name="🌐 Comptes Trouvés",
                    value=accounts_text,
                    inline=False
                )
            
            embed.add_field(
                name="⚠️ Avertissement Légal",
                value="Ces données sont publiques. Respect de la vie privée obligatoire.",
                inline=False
            )
            embed.set_footer(text="Discord OSINT | Données de sources publiques")
            
            await interaction.user.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la recherche: {str(e)}",
                color=discord.Color.red()
            )
            try:
                await interaction.user.send(embed=embed)
            except:
                await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(AllSlashCommands(bot))
