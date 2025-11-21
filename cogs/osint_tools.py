# ...existing code...
import discord
from discord.ext import commands
import requests
import logging
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
import os

load_dotenv()
HIBP_API_KEY = os.getenv('HIBP_API_KEY')  # optionnel

logger = logging.getLogger(__name__)

class OSINTTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='reverseemail')
    async def reverse_email(self, ctx, email):
        if '@' not in email:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Format email invalide",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        loading_embed = discord.Embed(
            title="🔍 Recherche en cours...",
            description=f"Recherche de comptes pour: **{email}**",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            user_part, domain_part = email.split('@')
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            }

            urls_to_check = [
                f"https://www.facebook.com/{user_part}",
                f"https://twitter.com/{user_part}",
                f"https://instagram.com/{user_part}",
                f"https://github.com/{user_part}",
                f"https://linkedin.com/in/{user_part}",
                f"https://reddit.com/u/{user_part}",
            ]

            found_accounts = []
            for url in urls_to_check:
                try:
                    resp = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
                    if resp.status_code < 400:
                        platform = url.split('/')[2].replace('www.', '').split('.')[0].upper()
                        found_accounts.append((platform, url))
                except Exception:
                    pass

            embed = discord.Embed(
                title=f"📧 Reverse Email: {email}",
                color=discord.Color.green()
            )

            embed.add_field(name="👤 Utilisateur", value=user_part, inline=True)
            embed.add_field(name="🌐 Domaine", value=domain_part, inline=True)

            if found_accounts:
                embed.add_field(name="✅ Comptes Trouvés", value=f"{len(found_accounts)} compte(s)", inline=True)
                for platform, url in found_accounts:
                    embed.add_field(name=f"🔗 {platform}", value=f"[Voir profil]({url})", inline=True)
            else:
                embed.add_field(name="ℹ️ Résultat", value="Aucun compte trouvé sur les réseaux vérifiés", inline=False)

            embed.add_field(
                name="🔍 Recherche Manuelle",
                value="[Google](https://www.google.com/search?q=" + email.replace('@', '%40') + ")\n[Bing](https://www.bing.com/search?q=" + email.replace('@', '%40') + ")",
                inline=False
            )

            await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur reverseemail: {e}", exc_info=True)
            embed = discord.Embed(title="❌ Erreur", description="Une erreur est survenue", color=discord.Color.red())
            await loading_msg.edit(embed=embed)

    # ... autres commandes inchangées ...

    @commands.command(name='leaks')
    async def check_leaks(self, ctx, query):
        if '@' not in query and not query.isdigit():
            embed = discord.Embed(title="❌ Erreur", description="Entrez un email ou un téléphone", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        loading_msg = await ctx.send(embed=discord.Embed(title="🔍 Vérification en cours...", description=f"Vérification de: **{query}**", color=discord.Color.blue()))

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            # If HIBP key is available, provide it, otherwise use web-check (may be limited)
            if HIBP_API_KEY:
                headers['hibp-api-key'] = HIBP_API_KEY

            if '@' in query:
                url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{query}"
            else:
                url = f"https://haveibeenpwned.com/api/v3/breachedaccount/+{query}"

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 401:
                embed = discord.Embed(title="❌ API HIBP - Clé requise", description="Le service HaveIBeenPwned requiert une clé API (HIBP_API_KEY). Configurez-la ou attendez.", color=discord.Color.orange())
                await loading_msg.edit(embed=embed)
                return

            if response.status_code == 404:
                embed = discord.Embed(title="✅ Sécurisé", description=f"**{query}** n'a pas été trouvé dans les fuites connues", color=discord.Color.green())
                await loading_msg.edit(embed=embed)
                return

            if response.status_code == 200:
                try:
                    breaches = response.json()
                except Exception:
                    breaches = []
                embed = discord.Embed(title="⚠️ Données compromise!", description=f"**{query}** a été trouvé dans **{len(breaches)}** fuite(s)", color=discord.Color.red())
                for i, breach in enumerate(breaches[:5], 1):
                    embed.add_field(name=f"Fuite {i}: {breach.get('Name','?')}", value=f"📅 {breach.get('BreachDate','?')}\n🔢 {breach.get('PwnCount','?')} comptes", inline=False)
                await loading_msg.edit(embed=embed)
                return

            embed = discord.Embed(title="❓ Résultat inconnu", description="Impossible de vérifier pour l'instant", color=discord.Color.yellow())
            await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur leaks: {e}", exc_info=True)
            embed = discord.Embed(title="❌ Erreur", description="Impossible de vérifier les fuites", color=discord.Color.red())
            await loading_msg.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(OSINTTools(bot))
# ...existing code...