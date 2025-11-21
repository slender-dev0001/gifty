import discord
from discord.ext import commands
from datetime import datetime
import requests
import json
import os
import socket
from bs4 import BeautifulSoup
import time

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='serverinfo')
    async def serverinfo(self, ctx):
        guild = ctx.guild
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
        embed.add_field(name="Région", value=str(guild.region) if hasattr(guild, 'region') else "N/A", inline=True)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        await ctx.send(embed=embed)

    @commands.command(name='userinfo')
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(
            title=f"👤 {member}",
            color=member.color
        )
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Mention", value=member.mention, inline=True)
        embed.add_field(name="Compte créé", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Serveur rejoint", value=member.joined_at.strftime("%d/%m/%Y") if member.joined_at else "N/A", inline=True)
        embed.add_field(name="Bot?", value="✅ Oui" if member.bot else "❌ Non", inline=True)
        embed.add_field(name="Statut", value=str(member.status).upper(), inline=True)
        
        roles = [role.mention for role in member.roles if role != ctx.guild.default_role]
        if roles:
            embed.add_field(name=f"Rôles ({len(roles)})", value=", ".join(roles[:10]), inline=False)
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        await ctx.send(embed=embed)

    @commands.command(name='roleinfo')
    async def roleinfo(self, ctx, role: discord.Role):
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
        
        await ctx.send(embed=embed)

    @commands.command(name='channelinfo')
    async def channelinfo(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        embed = discord.Embed(
            title=f"#️⃣ {channel.name}",
            color=discord.Color.purple()
        )
        embed.add_field(name="ID", value=channel.id, inline=True)
        embed.add_field(name="Type", value="Texte" if isinstance(channel, discord.TextChannel) else "Vocal", inline=True)
        embed.add_field(name="Créé le", value=channel.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Sujet", value=channel.topic or "Aucun", inline=False)
        embed.add_field(name="NSFW", value="✅ Oui" if channel.is_nsfw() else "❌ Non", inline=True)
        
        if channel.slowmode_delay > 0:
            embed.add_field(name="Mode lent", value=f"{channel.slowmode_delay}s", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name='stats')
    async def stats(self, ctx):
        embed = discord.Embed(
            title="📈 Statistiques du Bot",
            color=discord.Color.green()
        )
        embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Serveurs", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Utilisateurs", value=len(self.bot.users), inline=True)
        embed.add_field(name="Extensions chargées", value=len(self.bot.cogs), inline=True)
        embed.add_field(name="Version", value="1.0.0", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name='commands')
    async def commands_list(self, ctx):
        try:
            commandes_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'COMMANDES.md')
            
            if not os.path.exists(commandes_path):
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Le fichier COMMANDES.md n'a pas été trouvé",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return
            
            with open(commandes_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            sections = []
            current_section = None
            exclude_sections = ['COMMANDES UTILITAIRES', 'AVERTISSEMENTS LÉGAUX', 'SYSTÈME DE SÉCURITÉ', 'EXEMPLES D\'UTILISATION']
            
            for line in content.split('\n'):
                if line.startswith('## '):
                    if current_section and current_section['title'] not in exclude_sections:
                        sections.append(current_section)
                    title = line.replace('## ', '')
                    current_section = {
                        'title': title,
                        'content': ''
                    }
                elif current_section:
                    current_section['content'] += line + '\n'
            
            if current_section and current_section['title'] not in exclude_sections:
                sections.append(current_section)
            
            for i, section in enumerate(sections):
                embed = discord.Embed(
                    title=section['title'],
                    color=discord.Color.blue()
                )
                
                description = section['content'].strip()
                
                if len(description) > 2048:
                    description = description[:2045] + "..."
                
                embed.description = description
                embed.set_footer(text=f"Page {i+1}/{len(sections)}")
                
                await ctx.send(embed=embed)
        
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

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
            
            embed.set_footer(text="Recherche d'IP | Alimenté par ip-api.com")
            
            await ctx.send(embed=embed)
        
        except requests.exceptions.Timeout:
            embed = discord.Embed(
                title="❌ Timeout",
                description="La requête a pris trop de temps",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except requests.exceptions.ConnectionError:
            embed = discord.Embed(
                title="❌ Erreur Connexion",
                description="Impossible de se connecter à l'API",
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

    @commands.command(name='searchname')
    async def searchname(self, ctx, firstname: str, lastname: str):
        try:
            await ctx.send("🔍 Recherche OSINT en cours... Les résultats vous seront envoyés en DM")
            
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
                        email_found = email
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
                        followers = data.get('followers', 0)
                        github_url = data.get('html_url', f'https://github.com/{username}')
                        found_accounts.append((f'[🐙 GitHub]({github_url})', username, followers))
                        break
                except:
                    pass
            
            base_checks = {
                'twitter': lambda u: (f'https://twitter.com/{u}', f'https://api.twitter.com/2/users/by/username/{u}'),
                'instagram': lambda u: (f'https://instagram.com/{u}', None),
                'reddit': lambda u: (f'https://reddit.com/user/{u}', f'https://www.reddit.com/user/{u}/about.json'),
                'tiktok': lambda u: (f'https://tiktok.com/@{u}', None),
                'twitch': lambda u: (f'https://twitch.tv/{u}', f'https://api.twitch.tv/kraken/users?login={u}'),
                'linkedin': lambda u: (f'https://linkedin.com/in/{u}', None),
                'youtube': lambda u: (f'https://youtube.com/@{u}', None),
            }
            
            for site, url_func in base_checks.items():
                for username in username_variants:
                    try:
                        url, api_url = url_func(username)
                        if site == 'reddit' and api_url:
                            response = requests.get(api_url, headers={'User-Agent': 'Discord Bot OSINT'}, timeout=3)
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
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la recherche: {str(e)}",
                color=discord.Color.red()
            )
            try:
                await ctx.author.send(embed=embed)
            except:
                await ctx.send(embed=embed)

    @commands.command(name='searchphone')
    async def searchphone(self, ctx, phone: str):
        try:
            await ctx.send("🔍 Recherche OSINT en cours... Les résultats vous seront envoyés en DM")
            
            phone_clean = ''.join(filter(str.isdigit, phone))
            
            if len(phone_clean) < 7:
                embed = discord.Embed(
                    title="❌ Numéro Invalide",
                    description="Le numéro de téléphone doit contenir au moins 7 chiffres",
                    color=discord.Color.red()
                )
                await ctx.author.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"🔍 OSINT Téléphone: {phone}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            results_found = False
            
            embed.add_field(
                name="📊 Informations Brutes",
                value=f"**Numéro:** `{phone_clean}`\n**Longueur:** {len(phone_clean)} chiffres\n**Format Original:** `{phone}`",
                inline=False
            )
            
            try:
                hibp_response = requests.get(
                    f'https://haveibeenpwned.com/api/v3/breachedaccount/{phone_clean}',
                    headers={'User-Agent': 'Discord Bot OSINT'},
                    timeout=5
                )
                if hibp_response.status_code == 200:
                    breaches = hibp_response.json()
                    breach_names = [b['Name'] for b in breaches[:8]]
                    embed.add_field(
                        name="⚠️ Fuites de Données",
                        value=f"🚨 Trouvé dans {len(breaches)} fuite(s):\n" + "\n".join(breach_names),
                        inline=False
                    )
                    results_found = True
            except:
                pass
            
            urls_to_check = [
                f"https://www.truecaller.com/search/FR/{phone_clean}",
                f"https://www.annuaire-inverse.fr/reverse-phone-lookup/{phone_clean}",
                f"https://www.pagesjaunes.fr/search?q={phone_clean}",
                f"https://www.annuairedelafrance.fr/{phone_clean}",
                f"https://www.infobel.com/FR/france/search?q={phone_clean}",
                f"https://www.editus.lu/en/search?searchText={phone_clean}",
                f"https://uk.pipl.com/search?phone={phone_clean}",
                f"https://www.whitepages.com/phone/{phone_clean}",
                f"https://www.truecaller.com/search/US/{phone_clean}",
            ]
            
            found_urls = []
            for url in urls_to_check:
                try:
                    response = requests.head(url, timeout=3, allow_redirects=True)
                    if response.status_code < 404:
                        site_name = url.split('/')[2].replace('www.', '')
                        found_urls.append(f"[🔍 {site_name}]({url})")
                        results_found = True
                except:
                    pass
            
            if found_urls:
                embed.add_field(
                    name="🌐 Sites de Recherche Disponibles",
                    value=" • ".join(found_urls[:5]),
                    inline=False
                )
            
            try:
                response = requests.get(
                    f'https://ip-api.com/json/{phone_clean}',
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        embed.add_field(
                            name="📍 Localisation Estimée",
                            value=f"**Pays:** {data.get('country', 'N/A')}\n**Ville:** {data.get('city', 'N/A')}\n**Région:** {data.get('regionName', 'N/A')}\n**ISP:** {data.get('isp', 'N/A')}",
                            inline=False
                        )
                        results_found = True
            except:
                pass
            
            try:
                response = requests.get(
                    f'https://www.google.com/search?q={phone_clean}',
                    headers={'User-Agent': 'Mozilla/5.0'},
                    timeout=5
                )
                if response.status_code == 200 and len(response.text) > 1000:
                    embed.add_field(
                        name="🔗 Résultats Google",
                        value=f"[Rechercher sur Google](https://www.google.com/search?q={phone_clean})",
                        inline=False
                    )
                    results_found = True
            except:
                pass
            
            try:
                response = requests.get(
                    f'https://www.linkedin.com/search/results/people/?keywords={phone_clean}',
                    headers={'User-Agent': 'Mozilla/5.0'},
                    timeout=5
                )
                if response.status_code == 200:
                    embed.add_field(
                        name="💼 LinkedIn",
                        value=f"[Rechercher sur LinkedIn](https://www.linkedin.com/search/results/people/?keywords={phone_clean})",
                        inline=False
                    )
                    results_found = True
            except:
                pass
            
            social_urls = {
                'Facebook': f'https://www.facebook.com/search/people/?q={phone_clean}',
                'Twitter': f'https://twitter.com/search?q={phone_clean}',
                'Reddit': f'https://www.reddit.com/search/?q={phone_clean}',
                'Instagram': f'https://www.instagram.com/explore/tags/{phone_clean}/'
            }
            
            social_found = []
            for name, url in social_urls.items():
                try:
                    response = requests.head(url, timeout=3, allow_redirects=True)
                    if response.status_code < 404:
                        social_found.append(f"[{name}]({url})")
                except:
                    pass
            
            if social_found:
                embed.add_field(
                    name="📱 Réseaux Sociaux",
                    value=" • ".join(social_found),
                    inline=False
                )
                results_found = True
            
            if not results_found:
                embed.add_field(
                    name="📭 Résultat",
                    value="Aucune information trouvée directement, mais consultez les liens ci-dessous",
                    inline=False
                )
            
            embed.add_field(
                name="⚠️ Avertissement Légal",
                value="Ces données sont publiques. Respect de la vie privée obligatoire. Usage légitime uniquement.",
                inline=False
            )
            embed.set_footer(text="Phone OSINT | Données de sources publiques")
            
            await ctx.author.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la recherche: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.author.send(embed=embed)

    @commands.command(name='useroslint')
    async def useroslint(self, ctx, user_id: str):
        try:
            await ctx.send("🔍 Recherche OSINT en cours... Les résultats vous seront envoyés en DM")
            
            try:
                user_id_int = int(user_id)
            except:
                embed = discord.Embed(
                    title="❌ ID Invalide",
                    description="L'ID Discord doit être un nombre",
                    color=discord.Color.red()
                )
                await ctx.author.send(embed=embed)
                return
            
            try:
                user = await self.bot.fetch_user(user_id_int)
            except:
                embed = discord.Embed(
                    title="❌ Utilisateur Non Trouvé",
                    description=f"L'utilisateur avec l'ID `{user_id}` n'existe pas",
                    color=discord.Color.red()
                )
                await ctx.author.send(embed=embed)
                return
            
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
                        headers={'User-Agent': 'Discord Bot OSINT'},
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
                        headers={'User-Agent': 'Discord Bot OSINT'},
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
                            response = requests.get(api_url, headers={'User-Agent': 'Discord Bot OSINT'}, timeout=3)
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
            
            await ctx.author.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la recherche: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.author.send(embed=embed)

    @commands.command(name='searchusername')
    async def searchusername(self, ctx, username: str):
        try:
            await ctx.send("🔍 Recherche OSINT en cours... Les résultats vous seront envoyés en DM")
            
            username_clean = username.lower()
            
            embed = discord.Embed(
                title=f"🔍 OSINT Username: {username_clean}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="👤 Informations",
                value=f"**Username:** `{username_clean}`",
                inline=False
            )
            
            found_accounts = []
            
            sites = {
                'GitHub': (f'https://api.github.com/users/{username_clean}', 'api'),
                'Twitter': (f'https://twitter.com/{username_clean}', 'head'),
                'Instagram': (f'https://instagram.com/{username_clean}', 'head'),
                'Reddit': (f'https://www.reddit.com/user/{username_clean}/about.json', 'api'),
                'TikTok': (f'https://tiktok.com/@{username_clean}', 'head'),
                'Twitch': (f'https://twitch.tv/{username_clean}', 'head'),
                'YouTube': (f'https://youtube.com/@{username_clean}', 'head'),
                'LinkedIn': (f'https://linkedin.com/in/{username_clean}', 'head'),
                'GitLab': (f'https://gitlab.com/{username_clean}', 'head'),
                'Telegram': (f'https://t.me/{username_clean}', 'head'),
                'Pastebin': (f'https://pastebin.com/u/{username_clean}', 'head'),
                'Medium': (f'https://medium.com/@{username_clean}', 'head'),
                'Dev.to': (f'https://dev.to/{username_clean}', 'head'),
            }
            
            for site_name, (url, method) in sites.items():
                try:
                    if method == 'api':
                        response = requests.get(url, headers={'User-Agent': 'Discord Bot OSINT'}, timeout=3)
                        if response.status_code == 200:
                            found_accounts.append(f'[{site_name}]({url.replace("/api.github.com/users/", "/github.com/").split("/about.json")[0]})')
                    else:
                        response = requests.head(url, timeout=3, allow_redirects=True)
                        if response.status_code < 404:
                            found_accounts.append(f'[{site_name}]({url})')
                except:
                    pass
            
            if found_accounts:
                accounts_text = " • ".join(found_accounts)
                embed.add_field(
                    name="🌐 Comptes Trouvés",
                    value=accounts_text,
                    inline=False
                )
            else:
                embed.add_field(
                    name="📭 Résultat",
                    value="Aucun compte trouvé avec ce username",
                    inline=False
                )
            
            google_url = f'https://www.google.com/search?q={username_clean}'
            duckduckgo_url = f'https://duckduckgo.com/?q={username_clean}'
            search_links = f"[Google]({google_url}) • [DuckDuckGo]({duckduckgo_url})"
            embed.add_field(
                name="🔗 Moteurs de Recherche",
                value=search_links,
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Avertissement Légal",
                value="Ces données sont publiques. Respect de la vie privée obligatoire.",
                inline=False
            )
            embed.set_footer(text="Username OSINT | Données de sources publiques")
            
            await ctx.author.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la recherche: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.author.send(embed=embed)

    @commands.command(name='searchurl')
    async def searchurl(self, ctx, url: str):
        try:
            await ctx.send("🔍 Analyse en cours... Les résultats vous seront envoyés en DM")
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            embed = discord.Embed(
                title=f"🔍 Analyse URL: {url}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            try:
                response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                
                embed.add_field(
                    name="📊 Réponse HTTP",
                    value=f"**Status Code:** `{response.status_code}`\n**Content-Type:** `{response.headers.get('content-type', 'N/A')}`",
                    inline=False
                )
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                title = soup.title.string if soup.title else "N/A"
                embed.add_field(
                    name="📝 Titre de la Page",
                    value=f"`{title}`" if len(str(title)) < 1024 else f"`{str(title)[:1020]}...`",
                    inline=False
                )
                
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    desc = meta_desc.get('content', 'N/A')
                    embed.add_field(
                        name="📄 Description",
                        value=f"`{desc}`" if len(desc) < 1024 else f"`{desc[:1020]}...`",
                        inline=False
                    )
                
                headers_info = f"**Server:** `{response.headers.get('server', 'N/A')}`\n**X-Powered-By:** `{response.headers.get('x-powered-by', 'N/A')}`"
                embed.add_field(
                    name="🔧 Headers",
                    value=headers_info,
                    inline=False
                )
                
                embed.add_field(
                    name="📏 Taille",
                    value=f"`{len(response.content)} bytes`",
                    inline=True
                )
                
            except requests.exceptions.Timeout:
                embed.add_field(
                    name="⚠️ Erreur",
                    value="Timeout lors de la connexion",
                    inline=False
                )
            except Exception as e:
                embed.add_field(
                    name="⚠️ Erreur",
                    value=f"Erreur: {str(e)}",
                    inline=False
                )
            
            try:
                hostname = url.split('//')[1].split('/')[0]
                ip = socket.gethostbyname(hostname)
                embed.add_field(
                    name="🌐 DNS",
                    value=f"**Hostname:** `{hostname}`\n**IP:** `{ip}`",
                    inline=False
                )
            except:
                pass
            
            embed.add_field(
                name="⚠️ Avertissement",
                value="Utilisez cette commande pour analyser des sites publics uniquement.",
                inline=False
            )
            embed.set_footer(text="URL Analysis | Données publiques")
            
            await ctx.author.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.author.send(embed=embed)

    @commands.command(name='searchlocation')
    async def searchlocation(self, ctx, latitude: str, longitude: str):
        try:
            await ctx.send("🔍 Recherche géographique en cours... Les résultats vous seront envoyés en DM")
            
            try:
                lat = float(latitude)
                lon = float(longitude)
            except:
                embed = discord.Embed(
                    title="❌ Coordonnées Invalides",
                    description="Format requis: `+searchlocation 48.8566 2.3522`",
                    color=discord.Color.red()
                )
                await ctx.author.send(embed=embed)
                return
            
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                embed = discord.Embed(
                    title="❌ Coordonnées Invalides",
                    description="Latitude: -90 à 90, Longitude: -180 à 180",
                    color=discord.Color.red()
                )
                await ctx.author.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"🔍 Localisation: {lat}, {lon}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📍 Coordonnées",
                value=f"**Latitude:** `{lat}`\n**Longitude:** `{lon}`",
                inline=False
            )
            
            try:
                nominatim_url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}'
                response = requests.get(nominatim_url, headers={'User-Agent': 'Discord Bot OSINT'}, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    address = data.get('address', {})
                    
                    location_info = f"**Adresse:** `{data.get('display_name', 'N/A')}`\n"
                    location_info += f"**Pays:** `{address.get('country', 'N/A')}`\n"
                    location_info += f"**Ville:** `{address.get('city', address.get('town', 'N/A'))}`\n"
                    location_info += f"**Région:** `{address.get('state', 'N/A')}`\n"
                    location_info += f"**Code Postal:** `{address.get('postcode', 'N/A')}`"
                    
                    embed.add_field(
                        name="🌍 Localisation",
                        value=location_info,
                        inline=False
                    )
            except:
                pass
            
            try:
                ip_api_url = f'https://ip-api.com/json/{lat},{lon}'
                response = requests.get(ip_api_url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        info = f"**Pays:** `{data.get('country', 'N/A')}`\n"
                        info += f"**Fuseau Horaire:** `{data.get('timezone', 'N/A')}`\n"
                        info += f"**ISP:** `{data.get('isp', 'N/A')}`"
                        
                        embed.add_field(
                            name="ℹ️ Informations",
                            value=info,
                            inline=False
                        )
            except:
                pass
            
            maps_link = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=15"
            embed.add_field(
                name="🗺️ Cartes",
                value=f"[OpenStreetMap]({maps_link}) • [Google Maps](https://maps.google.com/maps?q={lat},{lon})",
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Avertissement",
                value="Coordonnées publiques uniquement. Respect de la vie privée obligatoire.",
                inline=False
            )
            embed.set_footer(text="Geolocation OSINT | OpenStreetMap")
            
            await ctx.author.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.author.send(embed=embed)

    @commands.command(name='searchphone_reverse')
    async def searchphone_reverse(self, ctx, phone: str):
        try:
            await ctx.send("🔍 Recherche inversée en cours... Les résultats vous seront envoyés en DM")
            
            phone_clean = ''.join(filter(str.isdigit, phone))
            
            if len(phone_clean) < 7:
                embed = discord.Embed(
                    title="❌ Numéro Invalide",
                    description="Le numéro doit contenir au moins 7 chiffres",
                    color=discord.Color.red()
                )
                await ctx.author.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"🔍 Recherche Inversée: {phone}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📱 Numéro",
                value=f"**Format:** `{phone}`\n**Chiffres:** `{phone_clean}`\n**Longueur:** {len(phone_clean)}",
                inline=False
            )
            
            try:
                hibp_response = requests.get(
                    f'https://haveibeenpwned.com/api/v3/breachedaccount/{phone_clean}',
                    headers={'User-Agent': 'Discord Bot OSINT'},
                    timeout=5
                )
                if hibp_response.status_code == 200:
                    breaches = hibp_response.json()
                    breach_names = [b['Name'] for b in breaches[:8]]
                    embed.add_field(
                        name="⚠️ Fuites de Données",
                        value=f"🚨 Trouvé dans {len(breaches)} fuite(s):\n" + "\n".join(breach_names),
                        inline=False
                    )
            except:
                pass
            
            reverse_lookup_sites = [
                ("Truecaller France", f"https://www.truecaller.com/search/FR/{phone_clean}"),
                ("Annuaire Inverse", f"https://www.annuaire-inverse.fr/reverse-phone-lookup/{phone_clean}"),
                ("Pages Jaunes", f"https://www.pagesjaunes.fr/search?q={phone_clean}"),
                ("Infobel", f"https://www.infobel.com/FR/france/search?q={phone_clean}"),
                ("Truecaller USA", f"https://www.truecaller.com/search/US/{phone_clean}"),
                ("WhitePages", f"https://www.whitepages.com/phone/{phone_clean}"),
                ("Pipl", f"https://uk.pipl.com/search?phone={phone_clean}"),
                ("Spokeo", f"https://www.spokeo.com/phone/{phone_clean}"),
                ("ZoomInfo", f"https://www.zoominfo.com/search?q={phone_clean}"),
                ("Telegram", f"https://t.me/{phone_clean}"),
                ("WhatsApp", f"https://wa.me/{phone_clean}"),
            ]
            
            found_urls = []
            for site_name, url in reverse_lookup_sites:
                try:
                    response = requests.head(url, timeout=3, allow_redirects=True)
                    if response.status_code < 404:
                        found_urls.append(f"[{site_name}]({url})")
                except:
                    pass
            
            if found_urls:
                embed.add_field(
                    name="🔍 Sites de Recherche",
                    value=" • ".join(found_urls[:8]),
                    inline=False
                )
            
            try:
                response = requests.get(
                    f'https://ip-api.com/json/{phone_clean}',
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        embed.add_field(
                            name="📍 Localisation Estimée",
                            value=f"**Pays:** `{data.get('country', 'N/A')}`\n**Ville:** `{data.get('city', 'N/A')}`\n**ISP:** `{data.get('isp', 'N/A')}`",
                            inline=False
                        )
            except:
                pass
            
            social_searches = {
                'Google': f'https://www.google.com/search?q={phone_clean}',
                'LinkedIn': f'https://www.linkedin.com/search/results/people/?keywords={phone_clean}',
                'Facebook': f'https://www.facebook.com/search/people/?q={phone_clean}',
                'Twitter': f'https://twitter.com/search?q={phone_clean}',
                'Reddit': f'https://www.reddit.com/search/?q={phone_clean}',
            }
            
            social_links = " • ".join([f"[{name}]({url})" for name, url in social_searches.items()])
            embed.add_field(
                name="🌐 Moteurs de Recherche",
                value=social_links,
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Avertissement Légal",
                value="Données publiques. Usage légitime uniquement. Respect de la vie privée obligatoire.",
                inline=False
            )
            embed.set_footer(text="Reverse Phone Lookup | Sources publiques + Messaging Apps")
            
            await ctx.author.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.author.send(embed=embed)

    @commands.command(name='searchemail')
    async def searchemail(self, ctx, email: str):
        try:
            await ctx.send("🔍 Recherche OSINT en cours... Les résultats vous seront envoyés en DM")
            
            if '@' not in email or '.' not in email:
                embed = discord.Embed(
                    title="❌ Email Invalide",
                    description="L'email doit être au format: exemple@domaine.com",
                    color=discord.Color.red()
                )
                await ctx.author.send(embed=embed)
                return
            
            email_lower = email.lower()
            username, domain = email_lower.split('@')
            
            def extract_names_from_email(username):
                possible_names = []
                
                if '.' in username:
                    parts = username.split('.')
                    if len(parts) == 2:
                        firstname = parts[0].capitalize()
                        lastname = parts[1].capitalize()
                        possible_names.append(f"{firstname} {lastname}")
                
                if '_' in username:
                    parts = username.split('_')
                    if len(parts) == 2:
                        firstname = parts[0].capitalize()
                        lastname = parts[1].capitalize()
                        possible_names.append(f"{firstname} {lastname}")
                
                if len(username) > 2 and not any(c in username for c in '._'):
                    for i in range(1, len(username)):
                        first = username[:i].capitalize()
                        second = username[i:].capitalize()
                        possible_names.append(f"{first} {second}")
                
                return list(dict.fromkeys(possible_names))
            
            possible_names = extract_names_from_email(username)
            
            embed = discord.Embed(
                title=f"🔍 OSINT Email: {email_lower}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            names_text = "\n".join([f"• {name}" for name in possible_names[:3]])
            embed.add_field(
                name="📧 Informations Email",
                value=f"**Email:** `{email_lower}`\n**Username:** `{username}`\n**Domaine:** `{domain}`\n\n**👤 Noms Possibles:**\n{names_text}",
                inline=False
            )
            
            results_found = False
            
            try:
                hibp_response = requests.get(
                    f'https://haveibeenpwned.com/api/v3/breachedaccount/{email_lower}',
                    headers={'User-Agent': 'Discord Bot OSINT'},
                    timeout=5
                )
                if hibp_response.status_code == 200:
                    breaches = hibp_response.json()
                    breach_names = [b['Name'] for b in breaches[:8]]
                    embed.add_field(
                        name="⚠️ Fuites de Données",
                        value=f"🚨 Trouvé dans {len(breaches)} fuite(s):\n" + "\n".join(breach_names),
                        inline=False
                    )
                    results_found = True
                else:
                    embed.add_field(
                        name="✅ Fuites de Données",
                        value="Aucune fuite trouvée dans HaveIBeenPwned",
                        inline=False
                    )
                    results_found = True
            except:
                embed.add_field(
                    name="⚠️ Fuites de Données",
                    value="Vérification non disponible",
                    inline=False
                )
            
            username_variants = [
                username,
                username.replace('.', ''),
                username.replace('_', ''),
                username.split('.')[0] if '.' in username else username,
            ]
            
            found_accounts = []
            
            for variant in username_variants:
                try:
                    response = requests.get(f'https://api.github.com/users/{variant}', timeout=3)
                    if response.status_code == 200:
                        data = response.json()
                        github_url = data.get('html_url', f'https://github.com/{variant}')
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
                'linkedin': lambda u: (f'https://linkedin.com/in/{u}', None),
            }
            
            for site, url_func in base_checks.items():
                for variant in username_variants:
                    try:
                        url, api_url = url_func(variant)
                        if site == 'reddit' and api_url:
                            response = requests.get(api_url, headers={'User-Agent': 'Discord Bot OSINT'}, timeout=3)
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
                results_found = True
            
            try:
                google_url = f'https://www.google.com/search?q={email_lower}'
                linkedin_url = f'https://www.linkedin.com/search/results/people/?keywords={email_lower}'
                facebook_url = f'https://www.facebook.com/search/people/?q={email_lower}'
                twitter_url = f'https://twitter.com/search?q={email_lower}'
                reddit_url = f'https://www.reddit.com/search/?q={email_lower}'
                insta_url = f'https://www.instagram.com/explore/tags/{email_lower}/'
                
                search_links = f"[Google]({google_url}) • [LinkedIn]({linkedin_url}) • [Facebook]({facebook_url}) • [Twitter]({twitter_url}) • [Reddit]({reddit_url})"
                embed.add_field(
                    name="🔗 Moteurs de Recherche",
                    value=search_links,
                    inline=False
                )
                results_found = True
            except:
                pass
            
            embed.add_field(
                name="⚠️ Avertissement Légal",
                value="Ces données sont publiques. Respect de la vie privée obligatoire.",
                inline=False
            )
            embed.set_footer(text="Email OSINT | Données de sources publiques")
            
            await ctx.author.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la recherche: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.author.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
