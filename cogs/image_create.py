import asyncio
import io
import os
import secrets
import sqlite3
import string
from pathlib import Path
from urllib.parse import urlparse

import discord
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError

load_dotenv()
DB_PATH = Path("links.db")

def resolve_base_url() -> str:
    """Résout l'URL de base depuis les variables d'environnement"""
    raw_url = os.getenv("BASE_URL", "gifty.up.railway.app")
    if not raw_url:
        return "https://googg.up.railway.app"
    parsed = urlparse(raw_url)
    if not parsed.scheme:
        return f"https://{raw_url}".rstrip("/")
    return raw_url.rstrip("/")

BASE_URL = resolve_base_url()

def ensure_tables() -> None:
    """Crée les tables nécessaires si elles n'existent pas"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS image_trackers (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                clicks INTEGER DEFAULT 0,
                image_data BLOB
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS image_clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracker_id TEXT NOT NULL,
                ip_address TEXT,
                browser TEXT,
                device_type TEXT,
                country TEXT,
                region TEXT,
                city TEXT,
                user_agent TEXT,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(tracker_id) REFERENCES image_trackers(id)
            )
            """
        )
        # Vérifier si la colonne image_data existe
        columns = {row[1] for row in cursor.execute("PRAGMA table_info(image_trackers)")}
        if "image_data" not in columns:
            cursor.execute("ALTER TABLE image_trackers ADD COLUMN image_data BLOB")

def generate_id(length: int = 8) -> str:
    """Génère un ID aléatoire unique"""
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))

def get_unique_id(cursor: sqlite3.Cursor, max_attempts: int = 20) -> str:
    """Génère un ID unique qui n'existe pas déjà dans la base"""
    for _ in range(max_attempts):
        candidate = generate_id()
        cursor.execute("SELECT 1 FROM image_trackers WHERE id = ?", (candidate,))
        if cursor.fetchone() is None:
            return candidate
    raise RuntimeError("Impossible de générer un identifiant unique")

def prepare_image(data: bytes) -> bytes:
    """Prépare l'image : redimensionne si nécessaire et convertit en PNG"""
    with Image.open(io.BytesIO(data)) as img:
        # Redimensionner si l'image est trop grande
        if max(img.size) > 2000:
            img.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
        # Convertir en RGB si nécessaire
        if img.mode != "RGB":
            img = img.convert("RGB")
        # Sauvegarder en PNG
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

class ImageCreate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        ensure_tables()

    @commands.command(name="imagecreate")
    async def imagecreate(self, ctx, *, title: str = "Image Tracker") -> None:
        """
        Crée une image trackée qui envoie l'IP en DM quand quelqu'un la charge
        Usage: +imagecreate [titre] (joindre une image PNG/JPG)
        """
        # Vérifier qu'une image est attachée
        if not ctx.message.attachments:
            embed = discord.Embed(
                title="❌ Aucune image détectée",
                description="Veuillez joindre une image PNG/JPG à votre message.\n\n**Usage:** `+imagecreate Mon Image` (avec image attachée)",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        attachment = ctx.message.attachments[0]
        
        # Vérifier le format
        if not attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            embed = discord.Embed(
                title="❌ Format invalide",
                description="Seules les images PNG/JPG sont acceptées.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Vérifier la taille (max 10 MB)
        if attachment.size > 10 * 1024 * 1024:
            embed = discord.Embed(
                title="❌ Fichier trop volumineux",
                description="L'image ne doit pas dépasser 10 MB.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Message de chargement
        loading_msg = await ctx.send("🔄 Création de l'image trackée en cours...")

        async with ctx.typing():
            try:
                # Télécharger l'image
                image_bytes = await attachment.read()
                
                # Traiter l'image (redimensionner, convertir)
                processed_image = await asyncio.to_thread(prepare_image, image_bytes)
                
                # Sauvegarder dans la base de données
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    tracker_id = get_unique_id(cursor)
                    cursor.execute(
                        """
                        INSERT INTO image_trackers (id, user_id, guild_id, title, image_data)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            tracker_id,
                            ctx.author.id,
                            ctx.guild.id if ctx.guild else 0,
                            title,
                            processed_image,
                        ),
                    )

                # Générer l'URL trackée
                image_url = f"{BASE_URL}/image/{tracker_id}"
                
                # Créer l'embed de succès
                embed = discord.Embed(
                    title="✅ Image Tracker Créée !",
                    description="Votre image trackée est prête ! **Partagez le lien ci-dessous pour tracker les visiteurs.**",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="📋 Informations",
                    value=f"**Titre:** {title}\n**ID:** `{tracker_id}`",
                    inline=False
                )
                embed.add_field(
                    name="🔗 Lien Tracker (PARTAGEZ CE LIEN)",
                    value=f"```{image_url}```\n⚠️ **Important:** Partagez uniquement ce lien pour tracker les visiteurs !",
                    inline=False
                )
                embed.add_field(
                    name="📊 Comment ça marche ?",
                    value=(
                        "**1.** Copiez le lien tracker ci-dessus\n"
                        "**2.** Partagez-le (Discord, messages, emails, etc.)\n"
                        "**3.** Quand quelqu'un charge l'image via ce lien, vous recevrez :\n"
                        "   • 📍 **Adresse IP complète**\n"
                        "   • 🌍 **Localisation** (pays, région, ville)\n"
                        "   • 🖥️ **Navigateur et système d'exploitation**\n"
                        "   • 📱 **Type d'appareil**\n"
                        "   • 🕐 **Date et heure du clic**\n"
                        "   • 📊 **User-Agent complet**"
                    ),
                    inline=False
                )
                embed.add_field(
                    name="💡 Commandes utiles",
                    value=f"`+imageclicks {tracker_id}` - Voir les statistiques détaillées\n`+imagestats` - Voir tous vos trackers",
                    inline=False
                )
                embed.add_field(
                    name="⚠️ IMPORTANT - Comment partager l'image",
                    value=(
                        "**✅ CORRECT:** Partagez directement le lien tracker\n"
                        "**❌ INCORRECT:** Ne copiez/collez PAS l'image depuis Discord\n"
                        "**❌ INCORRECT:** Ne téléchargez PAS puis ré-uploadez l'image\n\n"
                        "🔒 **Seul le lien tracker permet de recevoir les notifications !**"
                    ),
                    inline=False
                )
                embed.add_field(
                    name="⚠️ Avertissement légal",
                    value="Cette fonctionnalité est à utiliser de manière **éthique et légale** uniquement. Ne l'utilisez pas pour harceler ou traquer quelqu'un.",
                    inline=False
                )
                embed.set_footer(text="Les notifications seront envoyées en DM • Bots Discord ignorés")

                # Supprimer le message de chargement
                await loading_msg.delete()
                
                # Envoyer le résultat en DM
                try:
                    await ctx.author.send(embed=embed)
                    await ctx.send(f"✅ {ctx.author.mention} Image tracker créée ! **Lien envoyé en DM** 📨\n💡 Partagez le lien pour tracker les visiteurs !")
                except discord.Forbidden:
                    # Si les DM sont fermés, envoyer dans le canal
                    await ctx.send(embed=embed)

            except UnidentifiedImageError:
                await loading_msg.edit(content="❌ Impossible de lire cette image. Assurez-vous qu'il s'agit d'une image valide.")
            except RuntimeError as error:
                await loading_msg.edit(content=f"❌ {error}")
            except Exception as error:
                await loading_msg.edit(content=f"❌ Erreur lors du traitement de l'image: {error}")

async def setup(bot) -> None:
    await bot.add_cog(ImageCreate(bot))