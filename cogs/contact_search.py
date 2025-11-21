import discord
from discord.ext import commands
import requests
import logging
from datetime import datetime
import time
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class ContactSearch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def generate_email_patterns(self, firstname, lastname):
        patterns = [
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
        return patterns

    async def search_hibp_leaks(self, query):
        leaks_data = []
        try:
            response = requests.get(
                f'https://haveibeenpwned.com/api/v3/breachedaccount/{query}',
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
                timeout=5
            )
            if response.status_code == 200:
                breaches = response.json()
                for breach in breaches[:5]:
                    leaks_data.append({
                        'source': breach.get('Name', 'Unknown'),
                        'date': breach.get('BreachDate', 'Unknown'),
                        'count': breach.get('PwnCount', 'Unknown'),
                        'title': breach.get('Title', '')
                    })
            time.sleep(1)
        except:
            pass
        
        return leaks_data

    async def search_email_details(self, email):
        details = {}
        try:
            response = requests.get(
                f'https://www.emailrep.io/query?email={email}',
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                details = {
                    'reputation': data.get('reputation', 'unknown'),
                    'suspicious': data.get('suspicious', False),
                    'blacklisted': data.get('blacklisted', False),
                    'known_credentials': len(data.get('details', {}).get('known_credentials', [])) > 0,
                    'credentials_leaked': len(data.get('details', {}).get('credentials_leaked', [])) > 0
                }
            time.sleep(0.5)
        except:
            pass
        
        return details

    async def search_phone_info(self, phone):
        info = {}
        phone_clean = re.sub(r'\D', '', phone)
        
        try:
            response = requests.get(
                f'https://api.country-state-city.com/v1/countries',
                timeout=5,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            if response.status_code == 200:
                if phone_clean.startswith('33'):
                    info['country'] = 'France'
                elif phone_clean.startswith('1'):
                    info['country'] = 'USA/Canada'
                elif phone_clean.startswith('44'):
                    info['country'] = 'United Kingdom'
                else:
                    info['country'] = 'Détection par code pays'
        except:
            pass
        
        try:
            response = requests.get(
                f'https://search.truecaller.com/api/v1/searchPhoneNumber?phoneNumber={phone_clean}&countryCode=auto',
                timeout=5,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    info['name'] = data['data'].get('name', 'Unknown')
                    info['carrier'] = data['data'].get('carrier', 'Unknown')
        except:
            pass
        
        return info

    async def search_social_media(self, firstname, lastname, email=None):
        socials = []
        username = f"{firstname.lower()}.{lastname.lower()}".replace(' ', '')
        
        platforms = [
            ('LinkedIn', f'https://www.linkedin.com/search/results/people/?keywords={firstname}%20{lastname}'),
            ('GitHub', f'https://github.com/{username}'),
            ('Twitter', f'https://twitter.com/search?q={firstname}%20{lastname}'),
            ('Instagram', f'https://www.instagram.com/{username}'),
            ('Facebook', f'https://www.facebook.com/search/people?q={firstname}%20{lastname}'),
            ('TikTok', f'https://www.tiktok.com/@{username}'),
            ('Reddit', f'https://www.reddit.com/r/all?q={firstname}%20{lastname}'),
        ]
        
        for platform, url in platforms:
            try:
                response = requests.head(url, timeout=3, allow_redirects=True)
                if response.status_code < 400:
                    socials.append({'platform': platform, 'url': url})
            except:
                pass
            time.sleep(0.3)
        
        return socials

    async def search_google_advanced(self, firstname, lastname, email=None, phone=None):
        results = []
        queries = [
            f'"{firstname} {lastname}"',
            f'{firstname} {lastname} contact',
            f'{firstname} {lastname} email',
            f'{firstname} {lastname} phone',
        ]
        
        if email:
            queries.append(f'"{email}"')
        if phone:
            queries.append(f'"{phone}"')
        
        for query in queries[:3]:
            try:
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(search_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    for link in soup.find_all('a', limit=5):
                        href = link.get('href', '')
                        if href.startswith('/url?q='):
                            url = href.split('/url?q=')[1].split('&')[0]
                            text = link.get_text()
                            if text and url:
                                results.append({'text': text[:60], 'url': url[:100]})
            except:
                pass
            time.sleep(0.5)
        
        return results[:5]

    async def search_nameapi(self, firstname):
        info = {}
        try:
            response = requests.get(
                f'https://api.nationalize.io?name={firstname}',
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                countries = data.get('country', [])
                if countries:
                    countries_list = ', '.join([f"{c['country_id']} ({c['probability']*100:.0f}%)" for c in countries[:3]])
                    info['countries'] = countries_list
        except:
            pass
        
        return info

    async def search_age_gender(self, firstname):
        info = {}
        try:
            response = requests.get(
                f'https://api.genderize.io?name={firstname}',
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                info['gender'] = data.get('gender', 'unknown')
                info['gender_confidence'] = f"{data.get('probability', 0)*100:.0f}%"
        except:
            pass
        
        try:
            response = requests.get(
                f'https://api.agify.io?name={firstname}',
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                info['estimated_age'] = data.get('age', 'unknown')
        except:
            pass
        
        return info

    @commands.command(name='searchcontact')
    async def search_contact(self, ctx, firstname: str, lastname: str):
        loading_embed = discord.Embed(
            title="🔍 Recherche avancée en cours...",
            description=f"Recherche de **{firstname} {lastname}**",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            embeds = []
            
            main_embed = discord.Embed(
                title=f"🔍 Profil Complet: {firstname} {lastname}",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            
            name_info = await self.search_nameapi(firstname)
            age_info = await self.search_age_gender(firstname)
            
            if age_info:
                age_text = f"Estimé: **{age_info.get('estimated_age', '?')}** ans • Genre: **{age_info.get('gender', '?')}** ({age_info.get('gender_confidence', '?')})"
                main_embed.add_field(name="👤 Infos Démographiques", value=age_text, inline=False)
            
            if name_info:
                main_embed.add_field(name="🌍 Pays Probables", value=name_info.get('countries', 'N/A'), inline=False)
            
            patterns = self.generate_email_patterns(firstname, lastname)
            main_embed.add_field(
                name="📧 Patterns Email Possibles",
                value="\n".join([f"`{e}`" for e in patterns[:6]]),
                inline=False
            )
            
            leaks_all = []
            for email in patterns:
                leaks = await self.search_hibp_leaks(email)
                leaks_all.extend([(email, l) for l in leaks])
                time.sleep(0.5)
            
            if leaks_all:
                leaks_text = "\n".join([f"📧 `{l[0]}` → **{l[1]['source']}** ({l[1]['date']}) - {l[1]['count']} comptes" for l in leaks_all[:5]])
                main_embed.add_field(
                    name="⚠️ Fuites Détectées",
                    value=leaks_text,
                    inline=False
                )
            
            socials = await self.search_social_media(firstname, lastname)
            if socials:
                socials_text = "\n".join([f"[{s['platform']}]({s['url']})" for s in socials])
                main_embed.add_field(
                    name="📱 Réseaux Sociaux",
                    value=socials_text,
                    inline=False
                )
            
            google_results = await self.search_google_advanced(firstname, lastname)
            if google_results:
                google_text = "\n".join([f"[{r['text']}]({r['url']})" for r in google_results[:3]])
                main_embed.add_field(
                    name="🔗 Résultats Web",
                    value=google_text[:1024],
                    inline=False
                )
            
            main_embed.set_footer(text="Sources: HIBP, EmailRep, APIs publiques | Utilisation responsable")
            embeds.append(main_embed)
            
            if embeds:
                await loading_msg.edit(embed=embeds[0])
                for embed in embeds[1:]:
                    await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Erreur searchcontact: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur est survenue: {str(e)[:100]}",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed)

    @commands.command(name='searchemail')
    async def search_email(self, ctx, email: str):
        loading_msg = await ctx.send(embed=discord.Embed(
            title="🔍 Analyse email en cours...",
            description=f"Vérification de **{email}**",
            color=discord.Color.blue()
        ))

        try:
            embed = discord.Embed(
                title=f"📧 Analyse: {email}",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            
            details = await self.search_email_details(email)
            if details:
                details_text = f"Réputation: **{details.get('reputation', '?')}**\n"
                details_text += f"Suspect: **{'Oui' if details.get('suspicious') else 'Non'}**\n"
                details_text += f"Blacklisté: **{'Oui' if details.get('blacklisted') else 'Non'}**\n"
                details_text += f"Credentials leakés: **{'Oui' if details.get('credentials_leaked') else 'Non'}**"
                embed.add_field(name="📊 Détails", value=details_text, inline=False)
            
            leaks = await self.search_hibp_leaks(email)
            if leaks:
                leaks_text = "\n".join([f"**{l['source']}** ({l['date']}) - {l['count']} comptes" for l in leaks[:5]])
                embed.add_field(name="⚠️ Fuites Trouvées", value=leaks_text, inline=False)
            else:
                embed.add_field(name="✅ Fuites", value="Aucune fuite détectée", inline=False)
            
            embed.set_footer(text="Source: HaveIBeenPwned, EmailRep")
            await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur searchemail: {e}")
            embed = discord.Embed(title="❌ Erreur", description="Une erreur est survenue", color=discord.Color.red())
            await loading_msg.edit(embed=embed)

    @commands.command(name='searchphone')
    async def search_phone(self, ctx, phone: str):
        loading_msg = await ctx.send(embed=discord.Embed(
            title="☎️ Analyse téléphone en cours...",
            description=f"Vérification de **{phone}**",
            color=discord.Color.blue()
        ))

        try:
            embed = discord.Embed(
                title=f"☎️ Analyse: {phone}",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            
            info = await self.search_phone_info(phone)
            if info:
                info_text = f"Pays: **{info.get('country', '?')}**\n"
                if 'name' in info:
                    info_text += f"Propriétaire: **{info.get('name')}**\n"
                if 'carrier' in info:
                    info_text += f"Opérateur: **{info.get('carrier')}**"
                embed.add_field(name="📞 Infos", value=info_text, inline=False)
            
            phone_patterns = [
                f"+{phone}",
                f"({phone})",
                phone
            ]
            
            embed.add_field(name="📊 Formats du Numéro", value="\n".join([f"`{p}`" for p in phone_patterns]), inline=False)
            
            embed.set_footer(text="Source: APIs publiques")
            await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur searchphone: {e}")
            embed = discord.Embed(title="❌ Erreur", description="Une erreur est survenue", color=discord.Color.red())
            await loading_msg.edit(embed=embed)


async def setup(bot):
    await bot.add_cog(ContactSearch(bot))
