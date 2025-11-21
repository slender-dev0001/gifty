import discord
from discord.ext import commands
from discord import ui
import datetime

class TicketView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="📩 Créer Ticket", style=discord.ButtonStyle.blurple)
    async def create_ticket(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="tickets")
        
        if not category:
            category = await guild.create_category("tickets")
        
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            topic=f"Ticket de {interaction.user.mention}"
        )
        
        await ticket_channel.set_permissions(
            interaction.guild.default_role,
            view=False
        )
        
        await ticket_channel.set_permissions(
            interaction.user,
            view=True,
            send_messages=True,
            read_messages=True
        )
        
        embed = discord.Embed(
            title="🎫 Nouveau Ticket",
            description=f"Ticket créé pour {interaction.user.mention}",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Support", value="L'équipe de support va vous aider bientôt!", inline=False)
        
        await ticket_channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"✅ Ticket créé: {ticket_channel.mention}", ephemeral=True)

class CloseTicketView(ui.View):
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)

    @ui.button(label="❌ Fermer le Ticket", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        channel = interaction.channel
        
        embed = discord.Embed(
            title="🎫 Ticket Fermé",
            description=f"Ticket fermé par {interaction.user.mention}",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Messages", value=f"{len(await channel.history(limit=None).flatten()) if hasattr(await channel.history(limit=1).__anext__(), 'id') else 'N/A'}", inline=False)
        
        await channel.send(embed=embed)
        await channel.delete(reason=f"Ticket fermé par {interaction.user.name}")

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ticketsystem')
    @commands.has_permissions(manage_channels=True)
    async def setup_tickets(self, ctx):
        category = discord.utils.get(ctx.guild.categories, name="tickets")
        
        if not category:
            category = await ctx.guild.create_category("tickets")
        
        embed = discord.Embed(
            title="🎫 Système de Support",
            description="Cliquez sur le bouton ci-dessous pour créer un ticket",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📋 Comment ça marche?",
            value="1. Cliquez sur 'Créer Ticket'\n2. Un canal privé sera créé\n3. Explicitez votre problème\n4. Cliquez sur 'Fermer le Ticket' quand c'est résolu",
            inline=False
        )
        
        await ctx.send(embed=embed, view=TicketView(self.bot))
        await ctx.send("✅ Système de tickets configuré!")

    @commands.command(name='ticket')
    async def ticket_info(self, ctx):
        embed = discord.Embed(
            title="🎫 Tickets Disponibles",
            description="Utilisez `+ticketsystem` pour créer la base de tickets",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
