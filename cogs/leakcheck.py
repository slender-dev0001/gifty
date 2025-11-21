import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

load_dotenv()
LEAKCHECK_API_KEY = os.getenv("LEAKCHECK_API_KEY", "1c687bab7c9893dc0d147b2c6e3803f449ebd7fd")

class LeakCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='checkemail')
    async def check_email(self, ctx, email: str):
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

    @commands.command(name='checkip')
    async def check_ip(self, ctx, ip: str):
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
    async def check_username(self, ctx, username: str):
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

async def setup(bot):
    await bot.add_cog(LeakCheck(bot))
