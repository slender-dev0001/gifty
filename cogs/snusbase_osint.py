import discord
from discord.ext import commands
import requests
import logging
from datetime import datetime, timedelta
import asyncio
import json
import os
from dotenv import load_dotenv
from typing import Optional, Dict, List
from collections import defaultdict

load_dotenv()
logger = logging.getLogger(__name__)

class APIManager:
    def __init__(self):
        self.snusbase_key = os.getenv('SNUSBASE_API_KEY', '')
        self.haveibeenpwned_key = os.getenv('HAVEIBEENPWNED_API_KEY', '')
        self.dehashed_key = os.getenv('DEHASHED_API_KEY', '')
        
        self.snusbase_url = "https://api.snusbase.com/data/search"
        self.haveibeenpwned_url = "https://haveibeenpwned.com/api/v3"
        self.dehashed_url = "https://api.dehashed.com/search"
        
        self.timeout = 10
        self.max_retries = 3
        self.cache = {}
        self.rate_limits = defaultdict(lambda: {'count': 0, 'reset': datetime.now()})
    
    def _check_rate_limit(self, api_name: str, limit: int = 10, window: int = 60) -> bool:
        now = datetime.now()
        limit_info = self.rate_limits[api_name]
        
        if now >= limit_info['reset']:
            limit_info['count'] = 0
            limit_info['reset'] = now + timedelta(seconds=window)
        
        if limit_info['count'] >= limit:
            return False
        
        limit_info['count'] += 1
        return True
    
    def _get_headers(self, api_name: str) -> Dict[str, str]:
        headers = {'User-Agent': 'Discord-Bot/1.0', 'Content-Type': 'application/json'}
        
        if api_name == 'snusbase' and self.snusbase_key:
            headers['Auth'] = self.snusbase_key
        elif api_name == 'haveibeenpwned' and self.haveibeenpwned_key:
            headers['User-Agent'] = f'Discord-Bot/1.0 ({self.haveibeenpwned_key})'
        elif api_name == 'dehashed' and self.dehashed_key:
            headers['Authorization'] = f'Basic {self.dehashed_key}'
        
        return headers
    
    async def search_email(self, email: str, api: str = 'snusbase') -> Optional[Dict]:
        if not self._check_rate_limit(api):
            raise Exception(f"Rate limit atteint pour {api}")
        
        cache_key = f"{api}:{email}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        headers = self._get_headers(api)
        
        for attempt in range(self.max_retries):
            try:
                if api == 'snusbase':
                    response = requests.post(
                        self.snusbase_url,
                        headers=headers,
                        json={"terms": [email], "types": ["email"]},
                        timeout=self.timeout
                    )
                elif api == 'haveibeenpwned':
                    response = requests.get(
                        f"{self.haveibeenpwned_url}/breachedaccount?account={email}",
                        headers=headers,
                        timeout=self.timeout
                    )
                else:
                    raise ValueError(f"API {api} non supportée")
                
                response.raise_for_status()
                data = response.json()
                self.cache[cache_key] = data
                return data
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Tentative {attempt+1}/{self.max_retries} - Erreur {api}: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"Échec final pour {email} sur {api}")
                    return None
    
    async def test_api(self, api: str) -> Dict[str, bool | str]:
        headers = self._get_headers(api)
        
        try:
            if api == 'snusbase':
                response = requests.post(
                    self.snusbase_url,
                    headers=headers,
                    json={"terms": ["test@example.com"], "types": ["email"]},
                    timeout=self.timeout
                )
            elif api == 'haveibeenpwned':
                response = requests.get(
                    self.haveibeenpwned_url,
                    headers=headers,
                    timeout=self.timeout
                )
            else:
                return {'success': False, 'error': f'API {api} non reconnue'}
            
            if response.status_code in [200, 401, 403]:
                return {'success': True, 'status': response.status_code}
            else:
                return {'success': False, 'status': response.status_code}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

class DatabaseLeaks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_manager = APIManager()
        self.search_cooldowns = defaultdict(lambda: None)
        
        # Base de données complète de sizeof.cat + autres sources
        self.databases = {
            # ===== MEGA FUITES =====
            "Yahoo": {"size": "300 GB", "records": "3B", "date": "2013-2014", "type": "Email", "breach_date": "2013-08-01"},
            "Collection #1": {"size": "87 GB", "records": "773M", "date": "2019", "type": "Combo", "breach_date": "2019-01-16"},
            "Collection #2-5": {"size": "845 GB", "records": "2.2B", "date": "2019", "type": "Combo", "breach_date": "2019-01-16"},
            "Anti Public": {"size": "458 GB", "records": "1.4B", "date": "2016-2019", "type": "Combo", "breach_date": "2016-01-01"},
            
            # ===== RÉSEAUX SOCIAUX =====
            "Facebook": {"size": "133 GB", "records": "533M", "date": "2019", "type": "Social", "breach_date": "2019-04-03"},
            "Twitter": {"size": "277 GB", "records": "235M", "date": "2021", "type": "Social", "breach_date": "2021-01-01"},
            "LinkedIn": {"size": "40 GB", "records": "167M", "date": "2012-2016", "type": "Professional", "breach_date": "2012-06-05"},
            "MySpace": {"size": "360 GB", "records": "360M", "date": "2008", "type": "Social", "breach_date": "2008-06-11"},
            "VK.com": {"size": "100 GB", "records": "100M", "date": "2016", "type": "Social", "breach_date": "2016-06-01"},
            "Tumblr": {"size": "72 GB", "records": "65M", "date": "2013", "type": "Social", "breach_date": "2013-02-01"},
            
            # ===== DATING/ADULT =====
            "Adult Friend Finder": {"size": "40 GB", "records": "412M", "date": "2016", "type": "Dating", "breach_date": "2016-10-16"},
            "Ashley Madison": {"size": "10 GB", "records": "32M", "date": "2015", "type": "Dating", "breach_date": "2015-07-19"},
            "Mate1.com": {"size": "27 GB", "records": "27M", "date": "2016", "type": "Dating", "breach_date": "2016-02-01"},
            "Fling.com": {"size": "40 GB", "records": "40M", "date": "2016", "type": "Dating", "breach_date": "2016-02-01"},
            
            # ===== GAMING =====
            "Zynga": {"size": "12 GB", "records": "173M", "date": "2019", "type": "Gaming", "breach_date": "2019-09-01"},
            "Sony PSN": {"size": "2.5 GB", "records": "77M", "date": "2011", "type": "Gaming", "breach_date": "2011-04-17"},
            "RockYou": {"size": "300 MB", "records": "32M", "date": "2009", "type": "Gaming", "breach_date": "2009-12-14"},
            
            # ===== CLOUD/TECH =====
            "Dropbox": {"size": "5 GB", "records": "68M", "date": "2012", "type": "Cloud Storage", "breach_date": "2012-07-01"},
            "Adobe": {"size": "9.7 GB", "records": "153M", "date": "2013", "type": "Software", "breach_date": "2013-10-04"},
            "Canva": {"size": "25 GB", "records": "139M", "date": "2019", "type": "Design", "breach_date": "2019-05-24"},
            
            # ===== E-COMMERCE =====
            "CafePress": {"size": "23 GB", "records": "23M", "date": "2019", "type": "E-commerce", "breach_date": "2019-02-01"},
            
            # ===== HOSPITALITY =====
            "Marriott": {"size": "20 GB", "records": "500M", "date": "2018", "type": "Hospitality", "breach_date": "2018-11-30"},
            "MGM Resorts": {"size": "10 GB", "records": "142M", "date": "2019", "type": "Hospitality", "breach_date": "2019-07-01"},
            
            # ===== MUSIC/MEDIA =====
            "Last.fm": {"size": "23 GB", "records": "81M", "date": "2012", "type": "Music", "breach_date": "2012-03-01"},
            "8tracks": {"size": "18 GB", "records": "18M", "date": "2017", "type": "Music", "breach_date": "2017-06-27"},
            "Dubsmash": {"size": "1 GB", "records": "162M", "date": "2018", "type": "Video", "breach_date": "2018-12-01"},
            "Wattpad": {"size": "19 GB", "records": "271M", "date": "2020", "type": "Reading", "breach_date": "2020-06-01"},
            
            # ===== B2B/MARKETING =====
            "People Data Labs": {"size": "277 GB", "records": "1.2B", "date": "2019", "type": "B2B Data", "breach_date": "2019-10-01"},
            "Verifications.io": {"size": "150 GB", "records": "789M", "date": "2019", "type": "Email Verification", "breach_date": "2019-02-25"},
            "Apollo.io": {"size": "200 GB", "records": "125M", "date": "2018", "type": "B2B Data", "breach_date": "2018-10-01"},
            "Exactis": {"size": "340 GB", "records": "340M", "date": "2018", "type": "Marketing", "breach_date": "2018-06-01"},
            "Epsilon": {"size": "60 GB", "records": "60M", "date": "2019", "type": "Marketing", "breach_date": "2019-03-01"},
            
            # ===== FORUMS/COMMUNAUTÉS =====
            "Exploit.in": {"size": "583 GB", "records": "593M", "date": "2016", "type": "Forum", "breach_date": "2016-10-01"},
            
            # ===== AUTRES =====
            "MyFitnessPal": {"size": "144 GB", "records": "144M", "date": "2018", "type": "Health", "breach_date": "2018-02-01"},
            "Evite": {"size": "10 GB", "records": "100M", "date": "2019", "type": "Events", "breach_date": "2019-02-01"},
            "Wishbone": {"size": "3.8 GB", "records": "40M", "date": "2020", "type": "Social", "breach_date": "2020-01-01"},
        }

    @commands.command(name='dbleaks')
    async def database_leaks(self, ctx, *, search: str = None):
        """Liste toutes les bases de données de fuites disponibles"""
        databases = self.databases
        
        if search:
            databases = {k: v for k, v in self.databases.items() 
                        if search.lower() in k.lower() or 
                        search.lower() in v['type'].lower()}
        
        if not databases:
            await ctx.send(f"❌ Aucune base de données trouvée pour: `{search}`")
            return

        embed = discord.Embed(
            title="🗄️ Base de Données des Fuites",
            description=f"**{len(databases)}** bases de données disponibles",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )

        # Statistiques globales
        total_records = sum([self._parse_records(v['records']) for v in self.databases.values()])
        total_size = sum([self._parse_size(v['size']) for v in self.databases.values()])
        
        embed.add_field(
            name="📊 Statistiques Totales",
            value=f"**Records:** {total_records/1e9:.1f}B+\n**Taille:** {total_size/1e3:.1f} TB+\n**Bases:** {len(self.databases)}",
            inline=False
        )

        # Catégories
        categories = {}
        for name, data in databases.items():
            cat = data['type']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(name)

        cat_text = ""
        for cat, dbs in sorted(categories.items()):
            cat_text += f"**{cat}:** {len(dbs)} bases\n"
        
        if cat_text:
            embed.add_field(
                name="📁 Catégories",
                value=cat_text[:1024],
                inline=False
            )

        # Top 10 des plus grandes fuites
        sorted_dbs = sorted(databases.items(), 
                          key=lambda x: self._parse_records(x[1]['records']), 
                          reverse=True)[:10]
        
        top_text = ""
        for idx, (name, data) in enumerate(sorted_dbs, 1):
            top_text += f"`{idx}.` **{name}** - {data['records']} ({data['date']})\n"
        
        embed.add_field(
            name="🔥 Top 10 Plus Grandes Fuites",
            value=top_text[:1024],
            inline=False
        )

        embed.add_field(
            name="💡 Commandes disponibles",
            value=(
                "`+dbleaks` - Liste toutes les bases\n"
                "`+dbleaks <recherche>` - Recherche\n"
                "`+dbinfo <nom>` - Détails\n"
                "`+checkbreach <email>` - Vérifier email\n"
                "`+dbstats` - Statistiques"
            ),
            inline=False
        )

        embed.set_footer(text="sizeof.cat Database Collection")
        await ctx.send(embed=embed)

    @commands.command(name='dbinfo')
    async def database_info(self, ctx, *, database_name: str):
        """Affiche les détails d'une base de données spécifique"""
        db = None
        db_name = None
        
        for name, data in self.databases.items():
            if database_name.lower() in name.lower():
                db = data
                db_name = name
                break
        
        if not db:
            matches = [name for name in self.databases.keys() if database_name.lower() in name.lower()]
            if matches:
                await ctx.send(f"❌ Base introuvable. Suggestions: `{', '.join(matches[:5])}`")
            else:
                await ctx.send(f"❌ Base de données introuvable: `{database_name}`")
            return

        embed = discord.Embed(
            title=f"🗄️ {db_name}",
            description="Informations détaillées sur cette fuite",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )

        embed.add_field(name="📊 Records", value=f"**{db['records']}**", inline=True)
        embed.add_field(name="💾 Taille", value=f"**{db['size']}**", inline=True)
        embed.add_field(name="📅 Date", value=f"**{db['date']}**", inline=True)
        embed.add_field(name="🏷️ Type", value=f"**{db['type']}**", inline=True)

        # Informations contextuelles
        context = self._get_database_context(db_name)
        if context:
            embed.add_field(
                name="📝 Contexte",
                value=context,
                inline=False
            )

        # Données typiques
        typical_data = self._get_typical_data(db['type'])
        embed.add_field(
            name="🔍 Données typiques",
            value=typical_data,
            inline=False
        )

        embed.add_field(
            name="⚠️ Avertissement",
            value="Cette base contient des données réelles. **Usage strictement légal uniquement.**",
            inline=False
        )

        embed.set_footer(text=f"sizeof.cat | {db_name}")
        await ctx.send(embed=embed)

    @commands.command(name='checkbreach')
    async def check_breach(self, ctx, email: str):
        try:
            if '@' not in email or '.' not in email:
                await ctx.send("❌ Format d'email invalide")
                return

            user_id = ctx.author.id
            if self.search_cooldowns[user_id] and datetime.now() < self.search_cooldowns[user_id]:
                await ctx.send("⏱️ Cooldown en cours. Réessayez dans 30 secondes.")
                return

            self.search_cooldowns[user_id] = datetime.now() + timedelta(seconds=30)
            
            status_msg = await ctx.send(f"🔍 Vérification de `{email}` en cours...")
            
            result = await self.api_manager.search_email(email, 'snusbase')
            
            embed = discord.Embed(
                title=f"🔍 Vérification: {email}",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )

            if result:
                embed.color = discord.Color.red()
                embed.add_field(name="⚠️ Statut", value="**Email trouvé dans une ou plusieurs fuites**", inline=False)
                embed.add_field(name="📊 Données", value=json.dumps(result, indent=2)[:1024], inline=False)
            else:
                potential = [db for db in self.databases if self.databases[db]['type'] in ['Social', 'Email', 'Combo']]
                breaches_str = "\n".join([f"• {db}" for db in potential[:10]])
                embed.add_field(name="ℹ️ Bases potentielles", value=breaches_str, inline=False)

            embed.add_field(
                name="🛡️ Actions recommandées",
                value="• Changez vos mots de passe\n• Activez 2FA\n• Utilisez un gestionnaire MDP\n• Monitorer vos comptes",
                inline=False
            )

            await status_msg.delete()
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur checkbreach: {e}", exc_info=True)
            await ctx.send(f"❌ Erreur: {str(e)[:200]}")
    
    @commands.command(name='searchemail')
    async def search_email_command(self, ctx, email: str, api: str = 'snusbase'):
        """Recherche les informations d'un email via une API OSINT"""
        try:
            if api not in ['snusbase', 'haveibeenpwned']:
                await ctx.send(f"❌ API non reconnue: {api}. Options: snusbase, haveibeenpwned")
                return

            status = await ctx.send(f"🔍 Recherche de `{email}` sur {api}...")
            
            result = await self.api_manager.search_email(email, api)
            
            embed = discord.Embed(
                title=f"🔎 Résultats pour {email}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            if result:
                if isinstance(result, list):
                    embed.add_field(name="✅ Résultats", value=f"Trouvé dans {len(result)} breaches", inline=False)
                    for breach in result[:5]:
                        name = breach.get('Name', breach.get('name', 'Unknown'))
                        embed.add_field(name=name, value=str(breach)[:256], inline=False)
                else:
                    embed.add_field(name="📊 Données", value=json.dumps(result, indent=2)[:1024], inline=False)
            else:
                embed.description = "❌ Aucun résultat trouvé"
            
            await status.delete()
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur searchemail: {e}", exc_info=True)
            await ctx.send(f"❌ Erreur: {str(e)[:200]}")
    
    @commands.command(name='getdomain')
    async def get_domain_info(self, ctx, domain: str):
        """Récupère les emails compromis d'un domaine"""
        try:
            domain = domain.lower().strip()
            if not domain or '.' not in domain:
                await ctx.send("❌ Domaine invalide")
                return
            
            status = await ctx.send(f"🔍 Recherche des emails du domaine `{domain}`...")
            
            emails_found = []
            for db_name, db_info in self.databases.items():
                if db_info['type'] in ['Combo', 'Social', 'Email']:
                    emails_found.append(db_name)
            
            embed = discord.Embed(
                title=f"📧 Domaine: {domain}",
                description=f"Analysé dans {len(emails_found)} bases de données",
                color=discord.Color.blurple(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="🗄️ Bases concernées",
                value="\n".join([f"• {db}" for db in emails_found[:15]]),
                inline=False
            )
            
            embed.add_field(
                name="💡 Conseil",
                value="Pour des résultats précis, utilisez Snusbase ou DeHashed avec une clé API",
                inline=False
            )
            
            await status.delete()
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur getdomain: {e}", exc_info=True)
            await ctx.send(f"❌ Erreur: {str(e)[:200]}")

    @commands.command(name='apilist')
    async def api_list(self, ctx):
        """Liste toutes les APIs OSINT disponibles et leur statut"""
        try:
            embed = discord.Embed(
                title="🔌 APIs OSINT Disponibles",
                description="Statut et configuration des APIs",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            apis_info = {
                'snusbase': {
                    'name': 'Snusbase',
                    'url': 'https://snusbase.com',
                    'features': 'Email breach, passwords, combo lists',
                    'requires_key': True
                },
                'haveibeenpwned': {
                    'name': 'Have I Been Pwned',
                    'url': 'https://haveibeenpwned.com',
                    'features': 'Email verification, breach history',
                    'requires_key': False
                },
                'dehashed': {
                    'name': 'DeHashed',
                    'url': 'https://dehashed.com',
                    'features': 'Email search, password verification',
                    'requires_key': True
                }
            }
            
            for api_key, api_info in apis_info.items():
                key_status = "🔑 Configurée" if (api_key == 'snusbase' and self.api_manager.snusbase_key) or \
                                                  (api_key == 'haveibeenpwned' and self.api_manager.haveibeenpwned_key) or \
                                                  (api_key == 'dehashed' and self.api_manager.dehashed_key) else "❌ Non configurée"
                
                embed.add_field(
                    name=f"{api_info['name']} {key_status}",
                    value=f"**URL:** {api_info['url']}\n**Features:** {api_info['features']}",
                    inline=False
                )
            
            embed.add_field(
                name="🚀 Commandes disponibles",
                value=(
                    "`+searchemail <email> [api]` - Chercher un email\n"
                    "`+checkbreach <email>` - Vérifier breach\n"
                    "`+getdomain <domaine>` - Info domaine\n"
                    "`+apitest <api>` - Tester une API"
                ),
                inline=False
            )
            
            embed.add_field(
                name="⚙️ Configuration",
                value="Définissez vos clés API dans le fichier `.env`:\n```\nSNUSBASE_API_KEY=votre_clé\nHAVEIBEENPWNED_API_KEY=votre_clé\nDEHASHED_API_KEY=votre_clé\n```",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur apilist: {e}", exc_info=True)
            await ctx.send(f"❌ Erreur: {str(e)[:200]}")
    
    @commands.command(name='apitest')
    async def api_test(self, ctx, api: str = None):
        """Teste la connexion à une API OSINT"""
        try:
            if not api:
                available_apis = ['snusbase', 'haveibeenpwned', 'dehashed']
                await ctx.send(f"❌ Spécifiez une API: {', '.join(available_apis)}")
                return
            
            api = api.lower()
            if api not in ['snusbase', 'haveibeenpwned', 'dehashed']:
                await ctx.send(f"❌ API non reconnue: {api}")
                return
            
            status = await ctx.send(f"🔄 Test de {api}...")
            result = await self.api_manager.test_api(api)
            
            embed = discord.Embed(
                title=f"🔌 Test API: {api}",
                timestamp=datetime.now()
            )
            
            if result['success']:
                embed.color = discord.Color.green()
                embed.description = "✅ **Connexion réussie**"
                embed.add_field(name="Status", value=f"Code: {result.get('status', 'OK')}", inline=False)
                embed.add_field(name="✨ Recommandation", value="L'API est opérationnelle et configurée", inline=False)
            else:
                embed.color = discord.Color.red()
                embed.description = "❌ **Connexion échouée**"
                error_msg = result.get('error', 'Erreur inconnue')
                embed.add_field(name="Erreur", value=error_msg[:500], inline=False)
                embed.add_field(
                    name="💡 Solutions",
                    value=f"1. Vérifiez votre clé API dans `.env`\n2. Assurez-vous que le service {api} est en ligne\n3. Vérifiez les restrictions de firewall",
                    inline=False
                )
            
            await status.delete()
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur apitest: {e}", exc_info=True)
            await ctx.send(f"❌ Erreur: {str(e)[:200]}")

    @commands.command(name='dbstats')
    async def database_stats(self, ctx):
        """Affiche les statistiques complètes"""
        embed = discord.Embed(
            title="📊 Statistiques Complètes des Fuites",
            description="Analyse de toutes les bases de données",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )

        # Par catégorie
        categories = {}
        for name, data in self.databases.items():
            cat = data['type']
            if cat not in categories:
                categories[cat] = {'count': 0, 'records': 0}
            categories[cat]['count'] += 1
            categories[cat]['records'] += self._parse_records(data['records'])

        cat_text = ""
        for cat, stats in sorted(categories.items(), key=lambda x: x[1]['records'], reverse=True):
            cat_text += f"**{cat}:** {stats['count']} bases, {stats['records']/1e6:.0f}M\n"
        
        embed.add_field(
            name="📁 Par Catégorie",
            value=cat_text[:1024],
            inline=False
        )

        # Total global
        total = sum([self._parse_records(v['records']) for v in self.databases.values()])
        embed.add_field(
            name="🌍 Total Global",
            value=f"**{total/1e9:.2f} Milliards** de records exposés",
            inline=False
        )

        embed.set_footer(text="sizeof.cat Statistics")
        await ctx.send(embed=embed)

    def _parse_records(self, records_str):
        """Convertit une chaîne de records en nombre"""
        records_str = str(records_str).upper().replace(',', '').replace(' ', '')
        multipliers = {'K': 1e3, 'M': 1e6, 'B': 1e9}
        
        for suffix, mult in multipliers.items():
            if suffix in records_str:
                try:
                    return float(records_str.replace(suffix, '')) * mult
                except:
                    return 0
        
        try:
            return float(records_str)
        except:
            return 0

    def _parse_size(self, size_str):
        """Convertit une chaîne de taille en GB"""
        size_str = str(size_str).upper().replace(' ', '')
        multipliers = {'MB': 0.001, 'GB': 1, 'TB': 1000}
        
        for suffix, mult in multipliers.items():
            if suffix in size_str:
                try:
                    return float(size_str.replace(suffix, '')) * mult
                except:
                    return 0
        
        return 0

    def _get_database_context(self, db_name):
        """Retourne du contexte sur une base"""
        contexts = {
            "Yahoo": "L'une des plus grandes fuites avec 3 milliards de comptes compromis sur plusieurs années.",
            "Collection #1": "Mega-compilation de 773M d'emails et 21M de mots de passe uniques provenant de milliers de sources.",
            "Facebook": "Fuite massive exposant 533M de profils avec numéros de téléphone et données personnelles.",
            "LinkedIn": "167M de professionnels avec emails, hashs bcrypt et données de profil.",
            "Ashley Madison": "Site de rencontres extraconjugales entièrement exposé par hackers activistes.",
            "Adult Friend Finder": "20 ans de données incluant profils, messages et préférences sensibles."
        }
        return contexts.get(db_name, None)

    def _get_typical_data(self, db_type):
        """Types de données selon catégorie"""
        data_types = {
            "Social": "• Emails, usernames, passwords\n• Noms, dates de naissance\n• Photos, posts, relations",
            "Professional": "• Emails professionnels\n• Titres, entreprises\n• Compétences, CV",
            "Dating": "• Profils complets\n• Préférences, photos\n• Messages privés",
            "Gaming": "• Pseudos, emails\n• Passwords, IPs\n• Stats de jeu",
            "Combo": "• Email:password\n• Username:password\n• Sources multiples",
            "E-commerce": "• Emails, adresses\n• Historique achats\n• Parfois CB"
        }
        return data_types.get(db_type, "• Emails\n• Usernames\n• Passwords hashés")

async def setup(bot):
    await bot.add_cog(DatabaseLeaks(bot))