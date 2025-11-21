import discord
from discord.ext import commands
import requests
import logging
from datetime import datetime
import time
import re

logger = logging.getLogger(__name__)

class OSINTSearchPrefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='searchip')
    async def searchip(self, ctx, ip: str):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(f'http://ip-api.com/json/{ip}?lang=fr', timeout=5, headers=headers)
            
            if response.status_code != 200:
                embed = discord.Embed(
                    title="❌ Erreur",
                    description=f"Erreur API (Status: {response.status_code})\nEssayez dans quelques secondes",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return
            
            data = response.json()
            
            if data.get('status') != 'success':
                embed = discord.Embed(
                    title="❌ IP Invalide",
                    description=f"L'IP `{ip}` n'est pas valide ou introuvable",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
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
            
            embed.add_field(name="⚠️ Avertissement", value="Information publique. Respect de la vie privée obligatoire.", inline=False)
            embed.set_footer(text="Recherche d'IP | Alimenté par ip-api.com")
            
            await ctx.send(embed=embed)
        
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name='searchname')
    async def searchname(self, ctx, firstname: str, lastname: str):
        await ctx.send("🔍 Recherche OSINT en cours... Les résultats vous seront envoyés en DM")
        
        try:
            results_found = False
            embed = discord.Embed(
                title=f"🔍 Résultats OSINT: {firstname} {lastname}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
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
            
            username_variants = [
                firstname.lower() + lastname.lower(),
                firstname.lower() + "." + lastname.lower(),
                firstname[0].lower() + lastname.lower(),
                firstname.lower() + lastname[0].lower()
            ]
            
            found_accounts = []
            
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
            
            await ctx.author.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur searchname: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la recherche: {str(e)}",
                color=discord.Color.red()
            )
            try:
                await ctx.author.send(embed=embed)
            except:
                await ctx.send(embed=embed)

    @commands.command(name='useroslint')
    async def useroslint(self, ctx, user_id: str):
        await ctx.send("🔍 Recherche OSINT en cours... Les résultats vous seront envoyés en DM")
        
        try:
            try:
                user_id_int = int(user_id)
            except:
                embed = discord.Embed(
                    title="❌ ID invalide",
                    description=f"L'ID `{user_id}` n'est pas un numéro valide",
                    color=discord.Color.red()
                )
                await ctx.author.send(embed=embed)
                return
            
            try:
                user = await self.bot.fetch_user(user_id_int)
            except:
                embed = discord.Embed(
                    title="❌ Utilisateur non trouvé",
                    description=f"L'ID Discord `{user_id}` n'existe pas",
                    color=discord.Color.red()
                )
                await ctx.author.send(embed=embed)
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
                            if response.status_code < 400:
                                found_accounts.append(f'[{site.capitalize()}]({url})')
                    except:
                        pass
                    time.sleep(0.3)
                
                if found_accounts:
                    accounts_text = "\n".join(found_accounts[:8])
                    embed.add_field(
                        name="🌐 Comptes Sociaux Trouvés",
                        value=accounts_text,
                        inline=False
                    )
            except:
                pass
            
            embed.add_field(
                name="⚠️ Avertissement Légal",
                value="Ces données sont publiques. Respect de la vie privée obligatoire.",
                inline=False
            )
            embed.set_footer(text="OSINT Search | Données de sources publiques")
            
            await ctx.author.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur useroslint: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la recherche: {str(e)}",
                color=discord.Color.red()
            )
            try:
                await ctx.author.send(embed=embed)
            except:
                await ctx.send(embed=embed)

    @commands.command(name='searchusername')
    async def searchusername(self, ctx, username: str):
        await ctx.send("🔍 Recherche de username en cours... Les résultats vous seront envoyés en DM")
        
        try:
            embed = discord.Embed(
                title=f"🔍 Résultats pour: {username}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            found_accounts = []
            
            platforms = {
                'GitHub': f'https://github.com/{username}',
                'Twitter': f'https://twitter.com/{username}',
                'Instagram': f'https://instagram.com/{username}',
                'Reddit': f'https://reddit.com/user/{username}',
                'TikTok': f'https://tiktok.com/@{username}',
                'Twitch': f'https://twitch.tv/{username}',
                'YouTube': f'https://youtube.com/c/{username}',
                'LinkedIn': f'https://linkedin.com/in/{username}',
                'GitLab': f'https://gitlab.com/{username}',
                'Telegram': f'https://t.me/{username}',
                'Discord': f'https://discord.com/users/{username}',
            }
            
            for platform, url in platforms.items():
                try:
                    if platform == 'GitHub':
                        response = requests.get(f'https://api.github.com/users/{username}', timeout=3)
                        if response.status_code == 200:
                            found_accounts.append(f'[{platform}]({url})')
                    else:
                        response = requests.head(url, timeout=3, allow_redirects=True)
                        if response.status_code < 400:
                            found_accounts.append(f'[{platform}]({url})')
                except:
                    pass
                time.sleep(0.2)
            
            if found_accounts:
                accounts_text = "\n".join(found_accounts)
                embed.add_field(
                    name="🌐 Comptes Trouvés",
                    value=accounts_text,
                    inline=False
                )
            else:
                embed.add_field(
                    name="❌ Aucun compte trouvé",
                    value=f"Le username `{username}` n'a été trouvé sur aucune plateforme",
                    inline=False
                )
            
            embed.add_field(
                name="⚠️ Avertissement",
                value="Données publiques. Respect de la vie privée obligatoire.",
                inline=False
            )
            embed.set_footer(text="Username Search | Données de sources publiques")
            
            await ctx.author.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur searchusername: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur: {str(e)}",
                color=discord.Color.red()
            )
            try:
                await ctx.author.send(embed=embed)
            except:
                await ctx.send(embed=embed)

    @commands.command(name='searchurl')
    async def searchurl(self, ctx, url: str):
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        try:
            response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            
            embed = discord.Embed(
                title=f"🔍 Analyse: {url[:50]}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(name="📊 Code HTTP", value=f"`{response.status_code}`", inline=True)
            embed.add_field(name="📄 Content-Type", value=f"`{response.headers.get('Content-Type', 'N/A')}`", inline=True)
            embed.add_field(name="📏 Taille", value=f"`{len(response.content)} bytes`", inline=True)
            
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.title.string if soup.title else "N/A"
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                description = meta_desc['content'] if meta_desc else "N/A"
                
                embed.add_field(name="🏷️ Titre", value=f"`{title[:100]}`", inline=False)
                embed.add_field(name="📝 Description", value=f"`{description[:100]}`", inline=False)
            except:
                pass
            
            embed.add_field(
                name="⚠️ Avertissement",
                value="Analyse de site public. Respect des conditions légales obligatoire.",
                inline=False
            )
            embed.set_footer(text="URL Analysis | Données de sources publiques")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Impossible d'accéder à l'URL: {str(e)[:100]}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name='searchlocation')
    async def searchlocation(self, ctx, latitude: str, longitude: str):
        try:
            lat = float(latitude)
            lon = float(longitude)
            
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                embed = discord.Embed(
                    title="❌ Coordonnées invalides",
                    description="Latitude: -90 à 90\nLongitude: -180 à 180",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"📍 Localisation: {lat}, {lon}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            try:
                response = requests.get(f'http://ip-api.com/json/{lat},{lon}?lang=fr', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    embed.add_field(name="🌍 Pays", value=f"{data.get('country', 'N/A')}", inline=True)
                    embed.add_field(name="🏙️ Ville", value=f"{data.get('city', 'N/A')}", inline=True)
                    embed.add_field(name="📍 Région", value=f"{data.get('regionName', 'N/A')}", inline=True)
            except:
                pass
            
            embed.add_field(
                name="🗺️ Cartes",
                value=f"[OpenStreetMap](https://www.openstreetmap.org/?zoom=15&lat={lat}&lon={lon})\n[Google Maps](https://maps.google.com/?q={lat},{lon})",
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Avertissement",
                value="Données publiques. Respect de la vie privée obligatoire.",
                inline=False
            )
            embed.set_footer(text="Location Search | Données de sources publiques")
            
            await ctx.send(embed=embed)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Format invalide",
                description="Utilisation: `+searchlocation <latitude> <longitude>`\nExemple: `+searchlocation 48.8566 2.3522`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name='searchphone_reverse')
    async def searchphone_reverse(self, ctx, phone: str):
        phone_clean = re.sub(r'\D', '', phone)
        
        try:
            embed = discord.Embed(
                title=f"☎️ Recherche inversée: {phone}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            phone_formats = [
                phone,
                f"+{phone_clean}",
                f"+33{phone_clean[1:]}" if phone_clean.startswith('0') else f"+33{phone_clean}",
            ]
            
            embed.add_field(
                name="📞 Formats du Numéro",
                value="\n".join([f"`{fmt}`" for fmt in phone_formats[:3]]),
                inline=False
            )
            
            reverse_services = {
                "🔎 TrueCaller": f"https://www.truecaller.com/search/{phone_clean}",
                "📖 Annuaire Inverse": f"https://www.annuaireinversefrance.com/{phone_clean}",
                "📕 Pages Jaunes": f"https://www.pagesjaunes.fr/recherche/{phone_clean}",
                "🔍 Google": f"https://www.google.com/search?q={phone_clean}",
                "💬 WhatsApp": f"https://wa.me/{phone_clean}",
            }
            
            services_text = "\n".join([f"[{name}]({url})" for name, url in reverse_services.items()])
            embed.add_field(
                name="🔗 Services de Recherche Inverse",
                value=services_text,
                inline=False
            )
            
            if phone_clean.startswith('33'):
                embed.add_field(name="🌍 Pays", value="France 🇫🇷", inline=True)
            elif phone_clean.startswith('1'):
                embed.add_field(name="🌍 Pays", value="USA/Canada 🇺🇸", inline=True)
            elif phone_clean.startswith('44'):
                embed.add_field(name="🌍 Pays", value="United Kingdom 🇬🇧", inline=True)
            
            embed.add_field(
                name="⚠️ Avertissement Légal",
                value="NE PAS utiliser pour du harcèlement ou du stalking.\nRespect de la vie privée obligatoire.",
                inline=False
            )
            embed.set_footer(text="Phone Reverse Search | Données de sources publiques")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(OSINTSearchPrefix(bot))
