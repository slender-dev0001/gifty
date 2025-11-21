import discord
from discord.ext import commands
import requests
import logging
from datetime import datetime
import os
from dotenv import load_dotenv
import json
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
logger = logging.getLogger(__name__)
SNUSBASE_API_KEY = os.getenv('SNUSBASE_API_KEY', '')

class LookupAdvanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.snusbase_url = "https://api-experimental.snusbase.com/data/search"

    async def snusbase_search(self, query, search_type='all'):
        """Recherche sur Snusbase"""
        try:
            headers = {
                'Auth': SNUSBASE_API_KEY,
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0'
            }
            
            payload = {
                'terms': [query],
                'types': [search_type] if search_type != 'all' else ['email', 'username', 'password', 'phone']
            }
            
            response = requests.post(
                self.snusbase_url,
                headers=headers,
                json=payload,
                timeout=10,
                verify=False
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                logger.error(f"Clé API invalide. Status: {response.status_code}, Response: {response.text[:100]}")
                return None
            elif response.status_code == 429:
                logger.error("Rate limit Snusbase atteint")
                return None
            else:
                logger.warning(f"Snusbase status {response.status_code}: {response.text[:200]}")
                return None
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connexion refusée: {str(e)[:100]}")
            return None
        except Exception as e:
            logger.error(f"Erreur snusbase_search: {e}")
            return None

    @commands.command(name='lookupusername')
    async def lookup_username(self, ctx, username: str):
        """Recherche un username en ligne"""
        try:
            if len(username) < 3:
                await ctx.send("❌ Username minimum 3 caractères")
                return

            status = await ctx.send(f"🔍 Recherche du username `{username}`...")

            response = f"👤 **Lookup: {username}**\n\n"
            
            platforms = [
                ("GitHub", f"https://github.com/{username}"),
                ("Twitter", f"https://twitter.com/{username}"),
                ("Instagram", f"https://instagram.com/{username}"),
                ("Reddit", f"https://reddit.com/u/{username}"),
                ("TikTok", f"https://tiktok.com/@{username}"),
            ]
            
            found = []
            for platform, url in platforms:
                try:
                    resp = requests.head(url, timeout=3, allow_redirects=True)
                    if resp.status_code < 400:
                        found.append(f"✅ [{platform}]({url})")
                except:
                    pass
            
            if found:
                response += "**Comptes trouvés:**\n" + "\n".join(found)
            else:
                response += "❌ Aucun compte trouvé sur les réseaux vérifiés"
            
            await status.delete()
            await ctx.send(response)

        except Exception as e:
            logger.error(f"Erreur lookupusername: {e}")
            await ctx.send(f"❌ Erreur: {str(e)[:100]}")

    @commands.command(name='lookupip')
    async def lookup_ip(self, ctx, ip: str):
        """Recherche géolocalisation & infos d'une IP"""
        try:
            if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
                await ctx.send("❌ Format IP invalide (ex: 192.168.1.1)")
                return

            status = await ctx.send(f"🌍 Analyse de l'IP `{ip}`...")

            embed = discord.Embed(
                title=f"🌍 Lookup IP: {ip}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )

            try:
                geo_response = requests.get(f"https://ip-api.com/json/{ip}", timeout=5)
                if geo_response.status_code == 200:
                    geo_data = geo_response.json()
                    if geo_data.get('status') == 'success':
                        embed.add_field(
                            name="📍 Géolocalisation",
                            value=f"**Pays:** {geo_data.get('country', '?')}\n**Région:** {geo_data.get('regionName', '?')}\n**Ville:** {geo_data.get('city', '?')}",
                            inline=True
                        )
                        embed.add_field(
                            name="🌐 Infos ISP",
                            value=f"**ISP:** {geo_data.get('isp', '?')}\n**Org:** {geo_data.get('org', '?')}\n**AS:** {geo_data.get('as', '?')}",
                            inline=True
                        )
            except:
                pass

            try:
                abusedb_response = requests.get(
                    f"https://api.abuseipdb.com/api/v2/check",
                    params={"ipAddress": ip, "maxAgeInDays": 90},
                    headers={"Key": "5b0ad6e4b6923fa07e8f2d3ae4c0c1f50c77f7bb0a1ad3cbe6b6f9f0f8f8f"},
                    timeout=5
                )
                if abusedb_response.status_code == 200:
                    abuse_data = abusedb_response.json().get('data', {})
                    abuse_score = abuse_data.get('abuseConfidenceScore', 0)
                    embed.add_field(
                        name="⚠️ AbuseIPDB",
                        value=f"Confiance d'abus: **{abuse_score}%**",
                        inline=False
                    )
            except:
                pass

            embed.set_footer(text="Sources: ip-api.com, AbuseIPDB")
            await status.delete()
            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Erreur lookupip: {e}")
            await ctx.send(f"❌ Erreur: {str(e)[:100]}")

    @commands.command(name='lookupdomain')
    async def lookup_domain(self, ctx, domain: str):
        """Recherche infos d'un domaine (WHOIS, DNS, SSL)"""
        try:
            domain = domain.lower().strip()
            if '.' not in domain or domain.startswith('.'):
                await ctx.send("❌ Domaine invalide")
                return

            status = await ctx.send(f"🔍 Analyse du domaine `{domain}`...")

            embed = discord.Embed(
                title=f"🌐 Lookup Domaine: {domain}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )

            try:
                dns_response = requests.get(
                    f"https://dns.google/resolve?name={domain}",
                    params={"type": "A"},
                    timeout=5
                )
                if dns_response.status_code == 200:
                    dns_data = dns_response.json()
                    if dns_data.get('Answer'):
                        ips = [ans.get('data') for ans in dns_data['Answer'][:3]]
                        embed.add_field(
                            name="🔗 Records DNS (A)",
                            value="\n".join([f"`{ip}`" for ip in ips if ip]),
                            inline=False
                        )
            except:
                pass

            try:
                crt_response = requests.get(
                    f"https://crt.sh/?q=%.{domain}&output=json",
                    timeout=5
                )
                if crt_response.status_code == 200:
                    crt_data = crt_response.json()
                    if isinstance(crt_data, list) and len(crt_data) > 0:
                        embed.add_field(
                            name="🔐 Certificats SSL",
                            value=f"**{len(crt_data)}** certificat(s) trouvé(s)",
                            inline=False
                        )
            except:
                pass

            embed.add_field(
                name="💡 Outils recommandés",
                value="[Shodan](https://shodan.io)\n[Censys](https://censys.io)\n[Whois](https://whois.domaintools.com)",
                inline=False
            )

            embed.set_footer(text="Sources: DNS, crt.sh")
            await status.delete()
            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Erreur lookupdomain: {e}")
            await ctx.send(f"❌ Erreur: {str(e)[:100]}")

    @commands.command(name='lookukhash')
    async def lookup_hash(self, ctx, hash_value: str):
        """Recherche un hash MD5/SHA256 (virustotal, md5decrypt, etc)"""
        try:
            hash_value = hash_value.lower().strip()
            hash_len = len(hash_value)
            
            if hash_len not in [32, 40, 64, 128]:
                await ctx.send("❌ Hash invalide (MD5, SHA1, SHA256, SHA512)")
                return

            hash_types = {32: "MD5", 40: "SHA1", 64: "SHA256", 128: "SHA512"}
            hash_type = hash_types[hash_len]

            status = await ctx.send(f"🔍 Recherche {hash_type}: `{hash_value[:16]}...`")

            embed = discord.Embed(
                title=f"🔐 Lookup Hash: {hash_type}",
                description=f"`{hash_value}`",
                color=discord.Color.purple(),
                timestamp=datetime.now()
            )

            try:
                md5_response = requests.get(
                    f"https://md5decrypt.net/en/api/api.php?hash={hash_value}&hash_type={hash_type.lower()}",
                    timeout=5
                )
                if md5_response.status_code == 200 and md5_response.text != "0":
                    embed.add_field(
                        name="✅ Déchiffré",
                        value=f"`{md5_response.text}`",
                        inline=False
                    )
                    embed.color = discord.Color.green()
            except:
                pass

            if embed.color == discord.Color.purple():
                embed.add_field(
                    name="⏹️ Non déchiffré",
                    value="Hash pas trouvé dans les bases de données",
                    inline=False
                )

            embed.add_field(
                name="🔍 Outils de recherche",
                value="[VirusTotal](https://www.virustotal.com)\n[CrackStation](https://crackstation.net)\n[Online Hash Crack](https://www.onlinehashcrack.com)",
                inline=False
            )

            embed.set_footer(text="Sources: md5decrypt.net")
            await status.delete()
            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Erreur lookukhash: {e}")
            await ctx.send(f"❌ Erreur: {str(e)[:100]}")

    @commands.command(name='lookupcrypto')
    async def lookup_crypto(self, ctx, address: str):
        """Recherche un portefeuille crypto (Bitcoin, Ethereum)"""
        try:
            address = address.strip()
            
            embed = discord.Embed(
                title=f"💰 Lookup Crypto",
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )

            if len(address) == 34 and address.startswith(('1', '3', 'b')):
                embed.add_field(
                    name="🔗 Bitcoin Address",
                    value=f"`{address}`",
                    inline=False
                )
                try:
                    btc_response = requests.get(f"https://blockchain.info/q/addressbalance/{address}", timeout=5)
                    if btc_response.status_code == 200:
                        balance = int(btc_response.text) / 1e8
                        embed.add_field(name="💾 Balance", value=f"**{balance} BTC**", inline=True)
                except:
                    pass
                
                embed.add_field(
                    name="🔍 Voir sur",
                    value="[Blockchain.info](https://www.blockchain.com/explorer)\n[BlockScan](https://blockscan.com)",
                    inline=False
                )
            
            elif len(address) == 42 and address.startswith('0x'):
                embed.add_field(
                    name="🔗 Ethereum Address",
                    value=f"`{address}`",
                    inline=False
                )
                embed.add_field(
                    name="🔍 Voir sur",
                    value="[Etherscan](https://etherscan.io)\n[BlockScan](https://blockscan.com)",
                    inline=False
                )
            
            else:
                embed.description = "Format d'adresse non reconnu"
                embed.color = discord.Color.red()

            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Erreur lookupcrypto: {e}")
            await ctx.send(f"❌ Erreur: {str(e)[:100]}")

    @commands.command(name='lookupphone')
    async def lookup_phone(self, ctx, phone: str):
        """Recherche infos d'un numéro téléphone"""
        try:
            phone_clean = re.sub(r'\D', '', phone)
            
            if len(phone_clean) < 7:
                await ctx.send("❌ Numéro invalide")
                return

            status = await ctx.send(f"☎️ Recherche de `{phone}`...")

            try:
                geo_response = requests.get(
                    f"https://api.country-state-city.com/v1/countries",
                    timeout=5
                )
                
                country_code = phone_clean[:2]
                countries = {
                    '33': '🇫🇷 France',
                    '1': '🇺🇸 USA/Canada',
                    '44': '🇬🇧 UK',
                    '49': '🇩🇪 Allemagne',
                    '39': '🇮🇹 Italie',
                    '34': '🇪🇸 Espagne',
                    '31': '🇳🇱 Pays-Bas',
                    '32': '🇧🇪 Belgique',
                }
                
                country = countries.get(country_code, '❓ Pays inconnu')
                
                response = f"☎️ **Lookup: {phone}**\n"
                response += f"Pays: {country}\n"
                response += f"Code: `+{country_code}`\n"
                response += f"Numéro: `{phone_clean}`\n\n"
                response += "⚠️ API Snusbase actuellement indisponible"
                
                await status.delete()
                await ctx.send(response)
                
            except Exception as e:
                await status.delete()
                await ctx.send(f"❌ Erreur: {str(e)[:100]}")

        except Exception as e:
            logger.error(f"Erreur lookupphone: {e}")
            await ctx.send(f"❌ Erreur: {str(e)[:100]}")

    @commands.command(name='lookupemail')
    async def lookup_email(self, ctx, email: str):
        """Vérifie un email sur HIBP et autres services"""
        try:
            if '@' not in email or '.' not in email:
                await ctx.send("❌ Email invalide")
                return

            status = await ctx.send(f"📧 Vérification de `{email}`...")

            response = f"📧 **Lookup: {email}**\n\n"
            
            try:
                hibp_response = requests.get(
                    f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                    headers={'User-Agent': 'Mozilla/5.0'},
                    timeout=5
                )
                
                if hibp_response.status_code == 200:
                    breaches = hibp_response.json()
                    response += f"⚠️ **Trouvé dans {len(breaches)} fuite(s):**\n"
                    for breach in breaches[:10]:
                        response += f"• {breach.get('Name')} ({breach.get('BreachDate')})\n"
                elif hibp_response.status_code == 404:
                    response += "✅ **Aucune fuite détectée**"
                else:
                    response += f"⚠️ Statut: {hibp_response.status_code}"
            except:
                response += "⚠️ Impossible de vérifier HIBP"
            
            await status.delete()
            await ctx.send(response)

        except Exception as e:
            logger.error(f"Erreur lookukemail: {e}")
            await ctx.send(f"❌ Erreur: {str(e)[:100]}")

    @commands.command(name='snustestapi')
    async def test_snusbase_api(self, ctx):
        """Teste la connexion à Snusbase"""
        status = await ctx.send("🔄 Test de connexion Snusbase...")
        
        try:
            headers = {'Auth': SNUSBASE_API_KEY}
            response = requests.post(
                "https://api-experimental.snusbase.com/data/search",
                headers=headers,
                json={"terms": ["test"], "types": ["email"]},
                timeout=10,
                verify=False
            )
            
            if response.status_code == 200:
                await status.edit(content="✅ API Snusbase fonctionne!\n" + response.text[:200])
            elif response.status_code == 401:
                await status.edit(content="❌ Clé API invalide ou expirée\nContact: https://snusbase.com")
            else:
                await status.edit(content=f"⚠️ Status {response.status_code}\n{response.text[:200]}")
        except requests.exceptions.ConnectionError:
            await status.edit(content="❌ Impossible de se connecter à api-experimental.snusbase.com\n\n**Solutions:**\n1. Vérifier l'URL correcte de Snusbase\n2. Vérifier la connectivité réseau\n3. Vérifier les pare-feu")
        except Exception as e:
            await status.edit(content=f"❌ Erreur: {str(e)[:150]}")

async def setup(bot):
    await bot.add_cog(LookupAdvanced(bot))
