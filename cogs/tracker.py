import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime
import threading
from tracker import run_server, create_tracker_link, get_tracker_stats

class Tracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_flask_server()
    
    def start_flask_server(self):
        thread = threading.Thread(target=run_server, args=(self.bot,), daemon=True)
        thread.start()
    
    @commands.command(name='createtracker')
    async def create_link(self, ctx, url: str, *, description: str = "Sans description"):
        """Crée un lien tracker"""
        link_id = create_tracker_link(ctx.author.id, url, description)
        tracker_url = f"http://localhost:5000/track/{link_id}"
        tracker_url_with_user = f"http://localhost:5000/track/{link_id}?uid={ctx.author.id}"
        
        embed = discord.Embed(
            title="🔗 Lien Tracker Créé",
            color=discord.Color.green()
        )
        embed.add_field(name="Lien Tracker (sans user)", value=f"`{tracker_url}`", inline=False)
        embed.add_field(name="Lien Tracker (identifie toi)", value=f"`{tracker_url_with_user}`", inline=False)
        embed.add_field(name="Cible", value=url, inline=False)
        embed.add_field(name="Description", value=description, inline=False)
        embed.add_field(name="ID", value=link_id, inline=True)
        embed.set_footer(text=f"Créé par {ctx.author}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='trackstats')
    async def track_stats(self, ctx, link_id: str):
        """Affiche les stats d'un lien tracker"""
        stats = get_tracker_stats(link_id, ctx.author.id)
        
        if stats is None:
            await ctx.send("❌ Lien non trouvé ou vous n'êtes pas le créateur!")
            return
        
        embed = discord.Embed(
            title=f"📊 Stats du Lien: {link_id}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Total de clics", value=str(stats['total_clicks']), inline=False)
        
        if stats['clicks']:
            clicks_text = ""
            for i, click in enumerate(stats['clicks'][:15], 1):
                ip, browser, device, time, user_agent, user_id = click
                user_info = f"<@{user_id}>" if user_id else "❓ Anonyme"
                clicks_text += f"**{i}.** {user_info} | 📍 {ip} | 🌐 {browser} | 📱 {device} | ⏰ {time.split('T')[1][:5]}\n"
            
            embed.add_field(name="Derniers clics (max 15)", value=clicks_text, inline=False)
        
        embed.set_footer(text="Utilisez +trackinfo pour plus d'infos")
        await ctx.send(embed=embed)
    
    @commands.command(name='trackinfo')
    async def track_info(self, ctx):
        """Affiche les infos sur le système de tracking"""
        embed = discord.Embed(
            title="🔍 Système de Tracking",
            description="Créez des liens qui vous permettent de voir qui les clique!",
            color=discord.Color.purple()
        )
        
        embed.add_field(name="📝 Créer un lien", value="`+createtracker <url> <description>`", inline=False)
        embed.add_field(name="📊 Voir les stats", value="`+trackstats <link_id>`", inline=False)
        
        embed.add_field(name="📍 Infos tracées", value="""
• **IP Address** - Localisation
• **Browser** - Navigateur utilisé
• **Device Type** - Mobile/Desktop/Tablet
• **Timestamp** - Quand le lien a été cliqué
• **User-Agent** - Infos complètes du navigateur
        """, inline=False)
        
        embed.set_footer(text="⚠️ À utiliser de manière éthique!")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Tracker(bot))
