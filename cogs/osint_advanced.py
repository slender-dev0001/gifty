import discord
from discord.ext import commands
import requests
import logging
import whois
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class OSINTAdvanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='metadata')
    async def metadata(self, ctx):
        if not ctx.message.attachments:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Joignez une image à votre message",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        loading_embed = discord.Embed(
            title="🔍 Analyse en cours...",
            description="Extraction des métadonnées",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            attachment = ctx.message.attachments[0]
            
            if not attachment.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Format d'image invalide",
                    color=discord.Color.red()
                )
                await loading_msg.edit(embed=embed)
                return
            
            image_data = await attachment.read()
            
            try:
                from PIL import Image
                from PIL.ExifTags import TAGS
                import io
                
                img = Image.open(io.BytesIO(image_data))
                exif_data = img._getexif()
                
                embed = discord.Embed(
                    title=f"🖼️ Métadonnées: {attachment.filename}",
                    description=f"Dimensions: {img.width}x{img.height}px",
                    color=discord.Color.green()
                )
                
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        if tag_name not in ['MakerNote', 'UserComment']:
                            embed.add_field(
                                name=tag_name,
                                value=str(value)[:100],
                                inline=True
                            )
                else:
                    embed.add_field(
                        name="EXIF",
                        value="Aucune données EXIF trouvée",
                        inline=False
                    )
                
                embed.add_field(
                    name="Format",
                    value=img.format,
                    inline=True
                )
                
                await loading_msg.edit(embed=embed)
                
            except Exception as e:
                logger.error(f"Erreur parsing EXIF: {e}")
                embed = discord.Embed(
                    title="⚠️ Info basique",
                    description=f"Fichier: **{attachment.filename}**\nTaille: **{attachment.size}** bytes",
                    color=discord.Color.yellow()
                )
                await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur metadata: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur est survenue: {str(e)[:100]}",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed)

    @commands.command(name='phonelocation')
    async def phone_location(self, ctx, phone_number):
        phone = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        if not phone.isdigit() or len(phone) < 10:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Numéro de téléphone invalide",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        loading_embed = discord.Embed(
            title="🔍 Recherche en cours...",
            description=f"Analyse de: **{phone_number}**",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            phone_prefix = phone[:2]
            
            country_codes = {
                '33': {'pays': 'France', '🇫🇷': 'France'},
                '32': {'pays': 'Belgique', '🇧🇪': 'Belgique'},
                '41': {'pays': 'Suisse', '🇨🇭': 'Suisse'},
                '49': {'pays': 'Allemagne', '🇩🇪': 'Allemagne'},
                '44': {'pays': 'Royaume-Uni', '🇬🇧': 'Royaume-Uni'},
                '39': {'pays': 'Italie', '🇮🇹': 'Italie'},
                '34': {'pays': 'Espagne', '🇪🇸': 'Espagne'},
                '31': {'pays': 'Pays-Bas', '🇳🇱': 'Pays-Bas'},
                '43': {'pays': 'Autriche', '🇦🇹': 'Autriche'},
                '45': {'pays': 'Danemark', '🇩🇰': 'Danemark'},
                '1': {'pays': 'États-Unis', '🇺🇸': 'États-Unis'},
            }
            
            operators_fr = {
                '600': 'Orange',
                '601': 'Orange',
                '602': 'Orange',
                '603': 'Orange',
                '604': 'Orange',
                '605': 'Orange',
                '606': 'Orange',
                '607': 'Orange',
                '608': 'Orange',
                '609': 'Orange',
                '610': 'Orange',
                '611': 'Orange',
                '612': 'Orange',
                '613': 'Orange',
                '614': 'Orange',
                '615': 'Orange',
                '616': 'Orange',
                '617': 'Orange',
                '618': 'Orange',
                '619': 'Orange',
                '620': 'SFR',
                '621': 'SFR',
                '622': 'SFR',
                '623': 'SFR',
                '624': 'SFR',
                '625': 'SFR',
                '626': 'SFR',
                '627': 'SFR',
                '628': 'SFR',
                '629': 'SFR',
                '630': 'Bouygues',
                '631': 'Bouygues',
                '632': 'Bouygues',
                '633': 'Bouygues',
                '634': 'Bouygues',
                '635': 'Bouygues',
                '636': 'Bouygues',
                '637': 'Bouygues',
                '638': 'Bouygues',
                '639': 'Bouygues',
                '650': 'Free',
                '651': 'Free',
                '652': 'Free',
                '653': 'Free',
                '654': 'Free',
                '655': 'Free',
                '656': 'Free',
                '657': 'Free',
                '658': 'Free',
                '659': 'Free',
            }
            
            country_info = country_codes.get(phone_prefix, {'pays': 'Pays inconnu'})
            country_name = country_info.get('pays', 'Inconnu')
            
            operator = "Non identifié"
            line_type = "Mobile"
            
            if phone_prefix == '33':
                prefix_3 = phone[2:5]
                operator = operators_fr.get(prefix_3, "Non identifié")
            
            embed = discord.Embed(
                title=f"☎️ Analyse Numéro: {phone_number}",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📍 Pays",
                value=f"{country_name}",
                inline=True
            )
            
            embed.add_field(
                name="🌍 Code Pays",
                value=f"+{phone_prefix}",
                inline=True
            )
            
            embed.add_field(
                name="📏 Longueur",
                value=f"{len(phone)} chiffres",
                inline=True
            )
            
            embed.add_field(
                name="📱 Type de Ligne",
                value=line_type,
                inline=True
            )
            
            embed.add_field(
                name="🏢 Opérateur",
                value=operator,
                inline=True
            )
            
            embed.add_field(
                name="✅ Validité",
                value="À vérifier (format valide)",
                inline=True
            )
            
            embed.add_field(
                name="🔢 Format International",
                value=f"+{phone[:2]} {phone[2:5]} {phone[5:8]} {phone[8:]}",
                inline=False
            )
            
            embed.add_field(
                name="🔍 Recherche en Ligne",
                value=f"**[Truecaller](https://www.truecaller.com/search/{phone})**\n**[NumLookup](https://www.numlookup.com/)**\n**[TrueCaller App](https://www.truecaller.com/)**",
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Note",
                value="Données basées sur le format du numéro\nPour plus de précision, utilisez Truecaller",
                inline=False
            )
            
            await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur phonelocation: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur est survenue",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed)

    @commands.command(name='whois')
    async def whois_lookup(self, ctx, domain):
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
            title="🔍 Recherche WHOIS en cours...",
            description=f"Infos pour: **{domain}**",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            whois_data = whois.whois(domain)
            
            embed = discord.Embed(
                title=f"🌐 WHOIS: {domain}",
                color=discord.Color.green()
            )
            
            if whois_data.registrar:
                embed.add_field(
                    name="Registrar",
                    value=whois_data.registrar,
                    inline=True
                )
            
            if whois_data.creation_date:
                date = whois_data.creation_date
                if isinstance(date, list):
                    date = date[0]
                embed.add_field(
                    name="Date de création",
                    value=date.strftime("%d/%m/%Y") if hasattr(date, 'strftime') else str(date),
                    inline=True
                )
            
            if whois_data.expiration_date:
                date = whois_data.expiration_date
                if isinstance(date, list):
                    date = date[0]
                embed.add_field(
                    name="Date d'expiration",
                    value=date.strftime("%d/%m/%Y") if hasattr(date, 'strftime') else str(date),
                    inline=True
                )
            
            if whois_data.name_servers:
                ns = whois_data.name_servers
                if isinstance(ns, list):
                    ns = ', '.join(ns[:3])
                embed.add_field(
                    name="Name Servers",
                    value=ns,
                    inline=False
                )
            
            if whois_data.registrant:
                embed.add_field(
                    name="Propriétaire",
                    value=str(whois_data.registrant)[:100],
                    inline=False
                )
            
            if whois_data.emails:
                emails = whois_data.emails
                if isinstance(emails, list):
                    emails = ', '.join(emails[:2])
                embed.add_field(
                    name="Emails",
                    value=emails,
                    inline=False
                )
            
            await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur whois: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Domaine non trouvé ou erreur: {str(e)[:100]}",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(OSINTAdvanced(bot))
