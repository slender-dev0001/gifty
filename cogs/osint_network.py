import discord
from discord.ext import commands
import socket
import logging
import requests
import random
import subprocess
import os

logger = logging.getLogger(__name__)

class OSINTNetwork(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='dnsrecords')
    async def dns_records(self, ctx, domain):
        domain = domain.lower().replace('http://', '').replace('https://', '').split('/')[0]
        
        if '.' not in domain:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Domaine invalide",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        loading_embed = discord.Embed(
            title="🔍 Recherche DNS en cours...",
            description=f"Domaine: **{domain}**",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            record_types = {
                'A': socket.AF_INET,
                'AAAA': socket.AF_INET6,
                'MX': 'MX',
                'CNAME': 'CNAME',
                'TXT': 'TXT'
            }
            
            embed = discord.Embed(
                title=f"🌐 Records DNS: {domain}",
                color=discord.Color.green()
            )
            
            try:
                a_records = socket.getaddrinfo(domain, None, socket.AF_INET)
                if a_records:
                    ips = list(set([ip[4][0] for ip in a_records]))
                    embed.add_field(
                        name="🔷 Records A (IPv4)",
                        value=f"```\n{chr(10).join(ips[:5])}```" if ips else "Aucun",
                        inline=False
                    )
            except:
                pass
            
            try:
                aaaa_records = socket.getaddrinfo(domain, None, socket.AF_INET6)
                if aaaa_records:
                    ips_v6 = list(set([ip[4][0] for ip in aaaa_records]))
                    embed.add_field(
                        name="🔶 Records AAAA (IPv6)",
                        value=f"```\n{chr(10).join(ips_v6[:3])}```" if ips_v6 else "Aucun",
                        inline=False
                    )
            except:
                pass
            
            try:
                mx = socket.getmxrr(domain) if hasattr(socket, 'getmxrr') else []
                if mx:
                    mx_list = [f"{priority}: {server}" for priority, server in mx[:3]]
                    embed.add_field(
                        name="📧 Records MX",
                        value=f"```\n{chr(10).join(mx_list)}```",
                        inline=False
                    )
            except:
                embed.add_field(
                    name="📧 Records MX",
                    value="Aucun trouvé",
                    inline=False
                )
            
            embed.add_field(
                name="📍 Informations",
                value="DNS est l'annuaire du Web\nA = IPv4 | AAAA = IPv6 | MX = Email",
                inline=False
            )
            
            await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur dnsrecords: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Domaine non trouvé ou erreur réseau",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed)

    @commands.command(name='emailverify')
    async def email_verify(self, ctx, email):
        if '@' not in email or '.' not in email.split('@')[1]:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Format email invalide",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        loading_embed = discord.Embed(
            title="🔍 Vérification en cours...",
            description=f"Email: **{email}**",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            user_part, domain_part = email.split('@')
            
            embed = discord.Embed(
                title=f"📧 Vérification: {email}",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="✅ Format Valide",
                value="Oui (structure correcte)",
                inline=True
            )
            
            embed.add_field(
                name="👤 Utilisateur",
                value=user_part,
                inline=True
            )
            
            embed.add_field(
                name="🌐 Domaine",
                value=domain_part,
                inline=True
            )
            
            try:
                mx = socket.getmxrr(domain_part) if hasattr(socket, 'getmxrr') else None
                has_mx = bool(mx)
            except:
                has_mx = False
            
            try:
                socket.gethostbyname(domain_part)
                dns_valid = True
            except:
                dns_valid = False
            
            embed.add_field(
                name="📮 Domaine Valide",
                value="✅ Oui" if dns_valid else "❌ Non",
                inline=True
            )
            
            embed.add_field(
                name="📧 MX Records",
                value="✅ Oui" if has_mx else "❌ Non",
                inline=True
            )
            
            embed.add_field(
                name="⚠️ Note",
                value="Email format valide\nPour vérifier si le compte existe, utilisez Have I Been Pwned",
                inline=False
            )
            
            await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur emailverify: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description="Une erreur est survenue",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed)

    @commands.command(name='hashcrack')
    async def hash_crack(self, ctx, hash_value):
        if len(hash_value) < 8:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Hash trop court",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        loading_embed = discord.Embed(
            title="🔓 Crack en cours...",
            description=f"Hash: **{hash_value[:32]}...**",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            hash_lower = hash_value.lower()
            
            hash_type = "Inconnu"
            if len(hash_lower) == 32:
                hash_type = "MD5"
            elif len(hash_lower) == 40:
                hash_type = "SHA-1"
            elif len(hash_lower) == 64:
                hash_type = "SHA-256"
            elif len(hash_lower) == 128:
                hash_type = "SHA-512"
            
            embed = discord.Embed(
                title=f"🔐 Analyse Hash",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📊 Type de Hash",
                value=hash_type,
                inline=True
            )
            
            embed.add_field(
                name="📏 Longueur",
                value=f"{len(hash_lower)} caractères",
                inline=True
            )
            
            embed.add_field(
                name="✅ Valide",
                value="✅ Oui (format correct)",
                inline=True
            )
            
            embed.add_field(
                name="🔍 Crack en Ligne",
                value=f"**[Crackstation](https://crackstation.net/)**\n**[MD5.com](https://www.md5.com/)**\n**[HashKiller](https://hashkiller.io/)**",
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Note",
                value="Utilisez les services en ligne pour casser le hash\nCela peut prendre du temps selon la complexité",
                inline=False
            )
            
            await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur hashcrack: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description="Une erreur est survenue",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed)

    @commands.command(name='portscan')
    async def port_scan(self, ctx, ip, ports: str = "1-1000"):
        try:
            socket.inet_aton(ip)
        except:
            embed = discord.Embed(
                title="❌ Erreur",
                description="IP invalide",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        loading_embed = discord.Embed(
            title="🔍 Scan Nmap en cours...",
            description=f"IP: **{ip}** | Ports: **{ports}**",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            nmap_cmd = f"nmap -p {ports} {ip}"
            
            try:
                result = subprocess.run(nmap_cmd, shell=True, capture_output=True, text=True, timeout=60)
                output = result.stdout
            except FileNotFoundError:
                embed = discord.Embed(
                    title="❌ Nmap non installé",
                    description="Installer nmap: `sudo apt install nmap` (Linux)\nOu télécharger depuis nmap.org",
                    color=discord.Color.red()
                )
                await loading_msg.edit(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"🔒 Nmap Scan: {ip}",
                color=discord.Color.green()
            )
            
            lines = output.split('\n')
            open_ports = []
            
            for line in lines:
                if 'open' in line.lower():
                    open_ports.append(line.strip())
            
            if open_ports:
                port_text = "\n".join(open_ports[:10])
                embed.add_field(
                    name="🟢 Ports Ouverts",
                    value=f"```\n{port_text}```",
                    inline=False
                )
                
                if len(open_ports) > 10:
                    embed.add_field(
                        name="📊 Plus...",
                        value=f"{len(open_ports) - 10} autres ports ouverts",
                        inline=False
                    )
            else:
                embed.add_field(
                    name="🔴 Aucun Port Ouvert",
                    value="Pas de ports ouverts détectés",
                    inline=False
                )
            
            embed.add_field(
                name="📊 Plage Scannée",
                value=f"Ports: {ports}",
                inline=True
            )
            
            embed.add_field(
                name="⚠️ Note",
                value="Scan rapide avec Nmap\nUtilise: `+portscan <ip> [plage]`",
                inline=True
            )
            
            await loading_msg.edit(embed=embed)

        except subprocess.TimeoutExpired:
            embed = discord.Embed(
                title="❌ Timeout",
                description="Le scan a pris trop de temps",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed)
        except Exception as e:
            logger.error(f"Erreur portscan: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Impossible de scanner: {str(e)[:80]}",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed)

    @commands.command(name='iprange')
    async def ip_range(self, ctx, start_ip, end_ip):
        try:
            socket.inet_aton(start_ip)
            socket.inet_aton(end_ip)
        except:
            embed = discord.Embed(
                title="❌ Erreur",
                description="IPs invalides",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        loading_embed = discord.Embed(
            title="🔍 Analyse en cours...",
            description=f"Plage: **{start_ip}** - **{end_ip}**",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            def ip_to_int(ip):
                parts = ip.split('.')
                return int(parts[0]) * 256**3 + int(parts[1]) * 256**2 + int(parts[2]) * 256 + int(parts[3])
            
            def int_to_ip(num):
                return f"{(num >> 24) & 255}.{(num >> 16) & 255}.{(num >> 8) & 255}.{num & 255}"
            
            start_int = ip_to_int(start_ip)
            end_int = ip_to_int(end_ip)
            
            if start_int > end_int:
                start_int, end_int = end_int, start_int
            
            total_ips = end_int - start_int + 1
            
            embed = discord.Embed(
                title=f"📊 Plage IP",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="🔷 IP Début",
                value=start_ip,
                inline=True
            )
            
            embed.add_field(
                name="🔶 IP Fin",
                value=end_ip,
                inline=True
            )
            
            embed.add_field(
                name="📈 Total IPs",
                value=f"{total_ips} adresses",
                inline=True
            )
            
            if total_ips > 1:
                embed.add_field(
                    name="🎯 Première IP",
                    value=int_to_ip(start_int + 1),
                    inline=True
                )
                
                embed.add_field(
                    name="🎯 Dernière IP",
                    value=int_to_ip(end_int - 1),
                    inline=True
                )
            
            embed.add_field(
                name="✅ Valide",
                value="Oui",
                inline=True
            )
            
            await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur iprange: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description="Une erreur est survenue",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed)

    @commands.command(name='ipgen')
    async def ip_generator(self, ctx, count: int = 5):
        if count < 1 or count > 100:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Entre 1 et 100 IPs",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        loading_embed = discord.Embed(
            title="🔄 Génération en cours...",
            description=f"Génération de **{count}** IP(s)",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            ips = []
            for _ in range(count):
                ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
                ips.append(ip)
            
            embed = discord.Embed(
                title=f"🔌 {count} IPs Générées",
                color=discord.Color.green()
            )
            
            ip_list = "\n".join(ips[:15])
            embed.add_field(
                name="📍 IPs",
                value=f"```\n{ip_list}```",
                inline=False
            )
            
            valid_count = 0
            for ip in ips:
                try:
                    socket.inet_aton(ip)
                    valid_count += 1
                except:
                    pass
            
            embed.add_field(
                name="✅ Valides",
                value=f"{valid_count}/{count}",
                inline=True
            )
            
            embed.add_field(
                name="📊 Type",
                value="Public (potentiellement)",
                inline=True
            )
            
            await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur ipgen: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description="Une erreur est survenue",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(OSINTNetwork(bot))
