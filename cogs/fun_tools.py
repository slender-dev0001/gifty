import discord
from discord.ext import commands
from io import BytesIO

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

class FunTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='qrcode')
    async def qrcode_gen(self, ctx, *, text):
        if not HAS_QRCODE:
            await ctx.send("❌ La bibliothèque `qrcode` n'est pas installée.\nExecutez: `pip install qrcode[pil]`")
            return
        
        if len(text) > 500:
            await ctx.send("❌ Le texte est trop long (max 500 caractères)")
            return
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        file = discord.File(buffer, filename="qrcode.png")
        embed = discord.Embed(
            title="📱 QR Code Généré",
            description=f"QR Code pour: `{text[:50]}...`" if len(text) > 50 else f"QR Code pour: `{text}`",
            color=discord.Color.blurple()
        )
        embed.set_image(url="attachment://qrcode.png")
        
        await ctx.send(embed=embed, file=file)

    @commands.command(name='ascii')
    async def ascii_art(self, ctx, *, text):
        ascii_arts = {
            'banner': self._banner_ascii,
            'wave': self._wave_ascii,
            'box': self._box_ascii,
        }
        
        if len(text) > 20:
            await ctx.send("❌ Le texte est trop long (max 20 caractères)")
            return
        
        art = self._banner_ascii(text)
        
        code_block = f"```\n{art}\n```"
        
        if len(code_block) > 2000:
            await ctx.send("❌ Le texte est trop long pour être affiché")
            return
        
        embed = discord.Embed(
            title="🎨 ASCII Art",
            description=code_block,
            color=discord.Color.gold()
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='asciistyles')
    async def ascii_styles(self, ctx):
        embed = discord.Embed(
            title="🎨 Styles ASCII disponibles",
            description="Utilisez `+ascii <texte>` pour générer",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="Style par défaut",
            value="```\n" + self._banner_ascii("TEST") + "\n```",
            inline=False
        )
        embed.add_field(
            name="Commande",
            value="`+ascii <texte>`",
            inline=False
        )
        
        await ctx.send(embed=embed)

    def _banner_ascii(self, text):
        chars = {
            'A': ['  █████ ', ' █     █', '███████ ', '█     █ ', '█     █ '],
            'B': ['██████ ', '█     █', '██████ ', '█     █', '██████ '],
            'C': [' █████ ', '█      ', '█      ', '█      ', ' █████ '],
            'D': ['██████ ', '█     █', '█     █', '█     █', '██████ '],
            'E': ['███████', '█      ', '██████ ', '█      ', '███████'],
            'F': ['███████', '█      ', '██████ ', '█      ', '█      '],
            'G': [' █████ ', '█      ', '█  ███ ', '█     █', ' █████ '],
            'H': ['█     █', '█     █', '███████', '█     █', '█     █'],
            'I': ['███████', '   █   ', '   █   ', '   █   ', '███████'],
            'J': ['███████', '    █  ', '    █  ', '█   █  ', ' ███   '],
            'K': ['█     █', '█    █ ', '█████  ', '█    █ ', '█     █'],
            'L': ['█      ', '█      ', '█      ', '█      ', '███████'],
            'M': ['█     █', '██   ██', '█ █ █ █', '█  █  █', '█     █'],
            'N': ['█     █', '██    █', '█ █   █', '█  █  █', '█   ██ '],
            'O': [' █████ ', '█     █', '█     █', '█     █', ' █████ '],
            'P': ['██████ ', '█     █', '██████ ', '█      ', '█      '],
            'Q': [' █████ ', '█     █', '█     █', ' █████ ', '      █'],
            'R': ['██████ ', '█     █', '██████ ', '█    █ ', '█     █'],
            'S': [' █████ ', '█      ', ' █████ ', '      █', '█████  '],
            'T': ['███████', '   █   ', '   █   ', '   █   ', '   █   '],
            'U': ['█     █', '█     █', '█     █', '█     █', ' █████ '],
            'V': ['█     █', '█     █', '█     █', ' █   █ ', '  █ █  '],
            'W': ['█     █', '█  █  █', '█ █ █ █', '██   ██', '█     █'],
            'X': ['█     █', ' █   █ ', '  █ █  ', ' █   █ ', '█     █'],
            'Y': ['█     █', ' █   █ ', '  █ █  ', '   █   ', '   █   '],
            'Z': ['███████', '     █ ', '    █  ', '   █   ', '███████'],
            ' ': ['       ', '       ', '       ', '       ', '       '],
        }
        
        result = ['', '', '', '', '']
        text = text.upper()[:10]
        
        for char in text:
            if char in chars:
                for i, line in enumerate(chars[char]):
                    result[i] += line + ' '
            else:
                for i in range(5):
                    result[i] += '   '
        
        return '\n'.join(result)

    def _wave_ascii(self, text):
        return f"~{text}~"

    def _box_ascii(self, text):
        width = len(text) + 4
        top = '┌' + '─' * (width - 2) + '┐'
        mid = '│ ' + text + ' │'
        bot = '└' + '─' * (width - 2) + '┘'
        return f"{top}\n{mid}\n{bot}"

async def setup(bot):
    await bot.add_cog(FunTools(bot))
