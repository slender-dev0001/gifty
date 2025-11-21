import discord
from discord.ext import commands
from discord import ui

class MainView(ui.View):
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)

    @ui.button(label="✅ Confirmer", style=discord.ButtonStyle.green)
    async def confirm_button(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(
            title="✅ Confirmé!",
            description=f"{interaction.user.mention} a confirmé!",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label="❌ Annuler", style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(
            title="❌ Annulé!",
            description=f"{interaction.user.mention} a annulé!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class SelectMenu(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Bleu", value="bleu", emoji="🔵"),
            discord.SelectOption(label="Rouge", value="rouge", emoji="🔴"),
            discord.SelectOption(label="Vert", value="vert", emoji="🟢"),
        ]
        super().__init__(
            placeholder="Choisis une couleur...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎨 Couleur sélectionnée",
            description=f"Tu as choisi: **{self.values[0]}**",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class SelectMenuView(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(SelectMenu())

class FormModal(ui.Modal, title="Formulaire d'Inscription"):
    name = ui.TextInput(label="Nom", placeholder="Ton nom...", max_length=50)
    age = ui.TextInput(label="Âge", placeholder="Ton âge...", max_length=3)
    bio = ui.TextInput(
        label="Bio",
        placeholder="Dis-moi quelque chose de toi...",
        style=discord.TextStyle.long,
        max_length=200
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📋 Inscription confirmée",
            color=discord.Color.green()
        )
        embed.add_field(name="Nom", value=self.name.value, inline=True)
        embed.add_field(name="Âge", value=self.age.value, inline=True)
        embed.add_field(name="Bio", value=self.bio.value, inline=False)
        embed.set_footer(text=f"Inscription de {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class Interactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='buttons')
    async def buttons(self, ctx):
        embed = discord.Embed(
            title="🎮 Boutons Interactifs",
            description="Clique sur les boutons ci-dessous",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=MainView())

    @commands.command(name='select')
    async def select(self, ctx):
        embed = discord.Embed(
            title="🎨 Menu Déroulant",
            description="Sélectionne une option",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=SelectMenuView())

    @commands.command(name='modal')
    async def show_modal(self, ctx):
        await ctx.send("📋 Ouvre la modale (pas visible directement)")
        
        class ModalButton(ui.View):
            @ui.button(label="Ouvrir le formulaire", style=discord.ButtonStyle.blurple)
            async def modal_button(self, interaction: discord.Interaction, button: ui.Button):
                await interaction.response.send_modal(FormModal())
        
        message = await ctx.send("Clique pour ouvrir le formulaire:", view=ModalButton())

async def setup(bot):
    await bot.add_cog(Interactions(bot))
