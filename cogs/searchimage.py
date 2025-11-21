import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class SearchImage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='searchimage')
    async def search_image(self, ctx, *, query):
        if not query or len(query.strip()) == 0:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Veuillez fournir un nom/prénom",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        loading_embed = discord.Embed(
            title="🔍 Recherche en cours...",
            description=f"Recherche d'images pour: **{query}**",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            search_url = f"https://www.bing.com/images/search?q={query.replace(' ', '+')}"
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            img_links = []
            
            for img in soup.find_all('img', limit=10):
                src = img.get('src')
                if src and ('http' in src):
                    img_links.append(src)
            
            if not img_links:
                error_embed = discord.Embed(
                    title="❌ Aucune image trouvée",
                    description=f"Pas de résultats pour: **{query}**",
                    color=discord.Color.red()
                )
                await loading_msg.edit(embed=error_embed)
                return
            
            embed = discord.Embed(
                title=f"🖼️ Images trouvées pour: {query}",
                description=f"**{len(img_links[:3])} image(s)** trouvée(s)",
                color=discord.Color.green()
            )
            
            for i, link in enumerate(img_links[:3], 1):
                embed.add_field(
                    name=f"Image {i}",
                    value=f"[Voir l'image]({link})",
                    inline=False
                )
            
            await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur searchimage: {e}")
            error_embed = discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur est survenue: {str(e)[:100]}",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=error_embed)

async def setup(bot):
    await bot.add_cog(SearchImage(bot))
