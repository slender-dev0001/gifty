import asyncio
import io
import os
import secrets
import sqlite3
from pathlib import Path
from typing import Iterable, Tuple
from urllib.parse import urlparse

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()
DB_PATH = Path("links.db")
DEFAULT_BASE_URL = "https://gifty.up.railway.app"

def resolve_base_url(default: str = DEFAULT_BASE_URL) -> str:
    raw_url = os.getenv("BASE_URL", default)
    if not raw_url:
        return default
    parsed = urlparse(raw_url)
    if not parsed.scheme:
        return f"https://{raw_url}".rstrip("/")
    return raw_url.rstrip("/")

BASE_URL = resolve_base_url()

def ensure_tables() -> None:
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
        columns = {row[1] for row in cursor.execute("PRAGMA table_info(image_trackers)")}
        if "image_data" not in columns:
            cursor.execute("ALTER TABLE image_trackers ADD COLUMN image_data BLOB")

class ImageTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        ensure_tables()

    def _generate_unique_tracker_id(self, cursor: sqlite3.Cursor, max_attempts: int = 20) -> str:
        for _ in range(max_attempts):
            candidate = secrets.token_urlsafe(6)
            cursor.execute("SELECT 1 FROM image_trackers WHERE id = ?", (candidate,))
            if cursor.fetchone() is None:
                return candidate
        raise RuntimeError("Impossible de générer un identifiant unique")

    def _fetch_tracker_data(self, tracker_id: str) -> Tuple[sqlite3.Row | None, Iterable[sqlite3.Row]]:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, user_id, title, clicks, created_at
                FROM image_trackers
                WHERE id = ?
                """,
                (tracker_id,),
            )
            tracker = cursor.fetchone()
            if tracker is None:
                return None, []
            cursor.execute(
                """
                SELECT ip_address, browser, device_type, country, region, city, clicked_at
                FROM image_clicks
                WHERE tracker_id = ?
                ORDER BY clicked_at DESC
                LIMIT 10
                """,
                (tracker_id,),
            )
            return tracker, cursor.fetchall()

    def _fetch_user_summary(self, user_id: int) -> tuple[int, int, list[tuple[str, str, int]], str | None]:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*), COALESCE(SUM(clicks), 0)
                FROM image_trackers
                WHERE user_id = ?
                """,
                (user_id,),
            )
            total_trackers, total_clicks = cursor.fetchone()
            cursor.execute(
                """
                SELECT id, title, clicks
                FROM image_trackers
                WHERE user_id = ?
                ORDER BY clicks DESC, created_at DESC
                LIMIT 3
                """,
                (user_id,),
            )
            top_entries = cursor.fetchall()
            cursor.execute(
                """
                SELECT clicked_at
                FROM image_clicks
                WHERE tracker_id IN (SELECT id FROM image_trackers WHERE user_id = ?)
                ORDER BY clicked_at DESC
                LIMIT 1
                """,
                (user_id,),
            )
            last_click_row = cursor.fetchone()
        return (
            total_trackers or 0,
            total_clicks or 0,
            [(row[0], row[1], row[2]) for row in top_entries],
            last_click_row[0] if last_click_row else None,
        )

    async def _create_tracker(self, user_id: int, guild_id: int, title: str) -> Tuple[str, bytes]:
        image_bytes = await asyncio.to_thread(self.create_tracking_image, title)
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            tracker_id = self._generate_unique_tracker_id(cursor)
            cursor.execute(
                """
                INSERT INTO image_trackers (id, user_id, guild_id, title, image_data)
                VALUES (?, ?, ?, ?, ?)
                """,
                (tracker_id, user_id, guild_id, title, image_bytes),
            )
        return tracker_id, image_bytes

    @staticmethod
    def _format_location(values: Iterable[str | None]) -> str:
        parts = [value for value in values if value and value.strip() and value.strip().lower() != "inconnu"]
        return ", ".join(parts) if parts else "Non disponible"

    @staticmethod
    def _format_click(row: sqlite3.Row) -> str:
        location = ImageTracker._format_location((row[5], row[4], row[3]))
        ip_value = row[0] or "Non disponible"
        browser = row[1] or "Inconnu"
        device = row[2] or "Inconnu"
        timestamp = row[6] or "Inconnu"
        return (
            f"**IP:** `{ip_value}`\n"
            f"📍 {location}\n"
            f"🌐 {browser} | 📱 {device}\n"
            f"🕐 {timestamp}"
        )

    @staticmethod
    def _build_stats_embed(tracker_id: str, tracker: sqlite3.Row, clicks: Iterable[sqlite3.Row]) -> discord.Embed:
        embed = discord.Embed(
            title=f"📊 Statistiques : {tracker['title']}",
            description=f"**Total de clics :** {tracker['clicks']}",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name="📋 Informations",
            value=f"**ID:** `{tracker_id}`\n**Créé le:** {tracker['created_at']}",
            inline=False,
        )
        click_list = list(clicks)
        if click_list:
            for index, row in enumerate(click_list, 1):
                embed.add_field(
                    name=f"Clic #{index}",
                    value=ImageTracker._format_click(row),
                    inline=False,
                )
        else:
            embed.add_field(
                name="📭 Aucun clic",
                value="Cette image n'a pas encore été cliquée",
                inline=False,
            )
        return embed

    def create_tracking_image(self, title: str) -> bytes:
        width, height = 800, 400
        image = Image.new("RGB", (width, height), color=(88, 101, 242))
        draw = ImageDraw.Draw(image)
        for y in range(height):
            color_value = int(88 + (y / height) * 50)
            draw.rectangle([(0, y), (width, y + 1)], fill=(color_value, 101, 242))
        try:
            font_large = ImageFont.truetype("arial.ttf", 50)
            font_small = ImageFont.truetype("arial.ttf", 30)
        except OSError:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        title_text = title if len(title) <= 30 else f"{title[:27]}..."
        bbox_title = draw.textbbox((0, 0), title_text, font=font_large)
        title_width = bbox_title[2] - bbox_title[0]
        title_height = bbox_title[3] - bbox_title[1]
        title_x = (width - title_width) // 2
        title_y = (height - title_height) // 2 - 30
        draw.text((title_x + 2, title_y + 2), title_text, fill=(0, 0, 0), font=font_large)
        draw.text((title_x, title_y), title_text, fill=(255, 255, 255), font=font_large)
        subtitle = "🎁 Cliquez pour voir"
        bbox_subtitle = draw.textbbox((0, 0), subtitle, font=font_small)
        subtitle_width = bbox_subtitle[2] - bbox_subtitle[0]
        subtitle_x = (width - subtitle_width) // 2
        subtitle_y = title_y + title_height + 20
        draw.text((subtitle_x + 1, subtitle_y + 1), subtitle, fill=(0, 0, 0), font=font_small)
        draw.text((subtitle_x, subtitle_y), subtitle, fill=(255, 255, 255), font=font_small)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    @app_commands.command(name="createimage", description="Créer une image qui track les clics avec l'IP")
    async def createimage(self, interaction: discord.Interaction, title: str):
        await interaction.response.defer(ephemeral=True)
        try:
            tracker_id, image_bytes = await self._create_tracker(
                interaction.user.id,
                interaction.guild.id if interaction.guild else 0,
                title,
            )
            filename = f"tracker_{tracker_id}.png"
            embed = discord.Embed(
                title="✅ Image Tracker Créée !",
                description="Votre image tracker est prête !",
                color=discord.Color.green(),
            )
            embed.add_field(
                name="📋 Informations",
                value=f"**Titre:** {title}\n**ID:** `{tracker_id}`",
                inline=False,
            )
            embed.add_field(
                name="📊 Utilisation",
                value=(
                    "L'image PNG est jointe à ce message.\n"
                    "Utilisez `/imageclicks` ou `+imagestats` pour retrouver le lien tracker et consulter les statistiques.\n"
                    "En cas de chargement via ce lien, vous recevrez :\n"
                    "• 📍 Adresse IP\n"
                    "• 🌍 Localisation (pays, région, ville)\n"
                    "• 🖥️ Navigateur et appareil\n"
                    "• 🕐 Date et heure du clic"
                ),
                inline=False,
            )
            embed.add_field(
                name="⚠️ Avertissement",
                value="Cette fonctionnalité est à utiliser de manière éthique et légale uniquement.",
                inline=False,
            )
            embed.set_footer(text="Les notifications seront envoyées en DM")
            file = discord.File(io.BytesIO(image_bytes), filename=filename)
            await interaction.followup.send(embed=embed, file=file, ephemeral=True)
            if interaction.channel:
                public_embed = discord.Embed(
                    title="🖼️ Nouvelle Image",
                    description=f"**{title}**",
                    color=discord.Color.blue(),
                )
                public_embed.set_image(url=f"attachment://{filename}")
                public_embed.set_footer(text=f"Créé par {interaction.user.name}")
                await interaction.channel.send(
                    embed=public_embed,
                    file=discord.File(io.BytesIO(image_bytes), filename=filename),
                )
        except Exception as error:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la création de l'image : {error}",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="imageclicks", description="Voir les statistiques de votre image tracker")
    async def imageclicks(self, interaction: discord.Interaction, tracker_id: str):
        await interaction.response.defer(ephemeral=True)
        try:
            tracker, clicks = self._fetch_tracker_data(tracker_id)
            if tracker is None:
                embed = discord.Embed(
                    title="❌ Tracker non trouvé",
                    description=f"Aucune image tracker avec l'ID `{tracker_id}`",
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            if tracker["user_id"] != interaction.user.id:
                embed = discord.Embed(
                    title="❌ Accès refusé",
                    description="Vous n'êtes pas le propriétaire de cette image tracker",
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            embed = self._build_stats_embed(tracker_id, tracker, clicks)
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as error:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur : {error}",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @commands.command(name="createimage")
    async def createimage_prefix(self, ctx, *, title: str):
        try:
            tracker_id, image_bytes = await self._create_tracker(
                ctx.author.id,
                ctx.guild.id if ctx.guild else 0,
                title,
            )
            filename = f"tracker_{tracker_id}.png"
            embed = discord.Embed(
                title="✅ Image Tracker Créée !",
                description="Votre image tracker est prête !",
                color=discord.Color.green(),
            )
            embed.add_field(
                name="📋 Informations",
                value=f"**Titre:** {title}\n**ID:** `{tracker_id}`",
                inline=False,
            )
            embed.add_field(
                name="📊 Commandes",
                value=(
                    f"`+imageclicks {tracker_id}` - Statistiques détaillées\n"
                    "`+imagestats` - Résumé global et liens"
                ),
                inline=False,
            )
            embed.set_image(url=f"attachment://{filename}")
            embed.set_footer(text="⚠️ À utiliser de manière éthique")
            file = discord.File(io.BytesIO(image_bytes), filename=filename)
            await ctx.send(embed=embed, file=file)
        except Exception as error:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur : {error}",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)

    @commands.command(name="imagestats")
    async def imagestats_prefix(self, ctx):
        trackers_count, total_clicks, top_entries, last_click = self._fetch_user_summary(ctx.author.id)
        if trackers_count == 0:
            await ctx.send("❌ Vous n'avez pas encore d'image tracker.")
            return
        embed = discord.Embed(
            title="📈 Statistiques Image Tracker",
            color=discord.Color.purple(),
        )
        embed.add_field(
            name="Résumé",
            value=(
                f"**Trackers actifs:** {trackers_count}\n"
                f"**Total de clics:** {total_clicks}\n"
                f"**Dernier clic:** {last_click or 'Aucun'}"
            ),
            inline=False,
        )
        if top_entries:
            lines = []
            for index, (tracker_id, title, clicks) in enumerate(top_entries, 1):
                tracker_title = title or "Sans titre"
                lines.append(
                    f"**#{index}** {tracker_title} • {clicks} clic(s)\n{BASE_URL}/image/{tracker_id}"
                )
            embed.add_field(
                name="Top 3",
                value="\n".join(lines),
                inline=False,
            )
        await ctx.send(embed=embed)

    @commands.command(name="imageclicks")
    async def imageclicks_prefix(self, ctx, tracker_id: str):
        try:
            tracker, clicks = self._fetch_tracker_data(tracker_id)
            if tracker is None:
                await ctx.send("❌ Tracker non trouvé")
                return
            if tracker["user_id"] != ctx.author.id:
                await ctx.send("❌ Accès refusé")
                return
            embed = self._build_stats_embed(tracker_id, tracker, clicks)
            await ctx.send(embed=embed)
        except Exception as error:
            await ctx.send(f"❌ Erreur : {error}")

async def setup(bot):
    await bot.add_cog(ImageTracker(bot))
