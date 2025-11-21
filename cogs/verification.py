import discord
from discord.ext import commands
from discord import ui
import random

class CaptchaModal(ui.Modal, title="🔐 Vérification Captcha"):
    answer = ui.TextInput(
        label="Résolvez: ",
        placeholder="Écrivez la réponse...",
        max_length=10
    )

    def __init__(self, correct_answer, bot):
        super().__init__()
        self.correct_answer = str(correct_answer)
        self.bot = bot
        self.answer.label = f"Résolvez: (réponse numérique)"

    async def on_submit(self, interaction: discord.Interaction):
        if str(self.answer.value).strip().lower() == self.correct_answer.lower():
            verified_role = discord.utils.get(interaction.guild.roles, name="Verified")
            
            if not verified_role:
                verified_role = await interaction.guild.create_role(name="Verified")
            
            await interaction.user.add_roles(verified_role)
            
            embed = discord.Embed(
                title="✅ Vérification Réussie!",
                description=f"{interaction.user.mention} a été vérifié!",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="❌ Vérification Échouée",
                description="La réponse est incorrecte. Réessayez avec `/verify`",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

class VerifyButton(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="✅ Se Vérifier", style=discord.ButtonStyle.green)
    async def verify_button(self, interaction: discord.Interaction, button: ui.Button):
        num1 = random.randint(1, 100)
        num2 = random.randint(1, 100)
        operation = random.choice(["+", "-", "*"])
        
        if operation == "+":
            answer = num1 + num2
        elif operation == "-":
            answer = num1 - num2
        else:
            answer = num1 * num2
        
        modal = CaptchaModal(answer, self.bot)
        modal.answer.label = f"Résolvez: {num1} {operation} {num2} = ?"
        
        await interaction.response.send_modal(modal)

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        verified_role = discord.utils.get(member.guild.roles, name="Verified")
        
        if not verified_role:
            verified_role = await member.guild.create_role(name="Verified")
        
        channel = discord.utils.get(member.guild.channels, name="verification")
        
        if channel:
            embed = discord.Embed(
                title=f"👋 Bienvenue {member.name}!",
                description="Veuillez vérifier votre compte pour accéder au serveur",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="🔐 Vérification",
                value="Cliquez sur le bouton ci-dessous pour résoudre un captcha",
                inline=False
            )
            
            await channel.send(f"{member.mention}", embed=embed, view=VerifyButton(self.bot))

    @commands.command(name='setupverification')
    @commands.has_permissions(manage_guild=True)
    async def setup_verification(self, ctx):
        verification_channel = discord.utils.get(ctx.guild.channels, name="verification")
        
        if not verification_channel:
            verification_channel = await ctx.guild.create_text_channel("verification")
        
        embed = discord.Embed(
            title="🔐 Vérification du Serveur",
            description="Cliquez sur le bouton pour vérifier votre compte",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📋 Processus",
            value="1. Cliquez sur 'Se Vérifier'\n2. Résolvez l'équation math\n3. Vous serez vérifié automatiquement!",
            inline=False
        )
        
        await verification_channel.send(embed=embed, view=VerifyButton(self.bot))
        await ctx.send(f"✅ Système de vérification créé dans {verification_channel.mention}")

    @commands.command(name='verify')
    async def verify(self, ctx):
        num1 = random.randint(1, 100)
        num2 = random.randint(1, 100)
        operation = random.choice(["+", "-", "*"])
        
        if operation == "+":
            answer = num1 + num2
        elif operation == "-":
            answer = num1 - num2
        else:
            answer = num1 * num2
        
        modal = CaptchaModal(answer, self.bot)
        modal.answer.label = f"Résolvez: {num1} {operation} {num2} = ?"
        
        await ctx.interaction.response.send_modal(modal) if hasattr(ctx, 'interaction') else await ctx.send("Utilisez `/verify` pour cette commande")

async def setup(bot):
    await bot.add_cog(Verification(bot))
