import discord
from discord.ext import commands, tasks
import random
from datetime import datetime, timedelta
import asyncio

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giveaways = {}

    @commands.command(name='giveaway')
    @commands.has_permissions(manage_guild=True)
    async def create_giveaway(self, ctx, duration: str, winners: int, *, prize):
        try:
            if duration.endswith('s'):
                seconds = int(duration[:-1])
            elif duration.endswith('m'):
                seconds = int(duration[:-1]) * 60
            elif duration.endswith('h'):
                seconds = int(duration[:-1]) * 3600
            elif duration.endswith('d'):
                seconds = int(duration[:-1]) * 86400
            else:
                await ctx.send("❌ Format invalide. Utilisez: 30s, 5m, 2h, 1d")
                return
            
            if winners <= 0:
                await ctx.send("❌ Le nombre de gagnants doit être positif")
                return
            
            if len(prize) > 100:
                await ctx.send("❌ Le prix est trop long (max 100 caractères)")
                return
            
            end_time = datetime.now() + timedelta(seconds=seconds)
            
            embed = discord.Embed(
                title="🎉 Giveaway!",
                description=f"**Réagissez avec 🎉 pour participer!**\n\n**Prix:** {prize}\n**Gagnants:** {winners}",
                color=discord.Color.gold()
            )
            embed.add_field(name="⏰ Fin", value=f"<t:{int(end_time.timestamp())}:R>", inline=True)
            embed.add_field(name="👥 Participants", value="0", inline=True)
            embed.set_footer(text=f"ID Giveaway: {len(self.giveaways)}")
            
            message = await ctx.send(embed=embed)
            await message.add_reaction("🎉")
            
            giveaway_id = len(self.giveaways)
            self.giveaways[giveaway_id] = {
                'message_id': message.id,
                'channel_id': ctx.channel.id,
                'end_time': end_time,
                'winners': winners,
                'prize': prize,
                'creator': ctx.author.id,
                'guild_id': ctx.guild.id,
                'ended': False
            }
            
            await ctx.send(f"✅ Giveaway créé! Durée: {duration}")
            
            await asyncio.sleep(seconds)
            await self.end_giveaway(giveaway_id)
            
        except ValueError:
            await ctx.send("❌ Format invalide. Utilisez: 30s, 5m, 2h, 1d")

    async def end_giveaway(self, giveaway_id):
        giveaway = self.giveaways.get(giveaway_id)
        
        if not giveaway or giveaway['ended']:
            return
        
        giveaway['ended'] = True
        
        try:
            channel = self.bot.get_channel(giveaway['channel_id'])
            message = await channel.fetch_message(giveaway['message_id'])
            
            reactions = message.reactions
            
            participants = set()
            for reaction in reactions:
                if str(reaction.emoji) == "🎉":
                    async for user in reaction.users():
                        if user.id != self.bot.user.id:
                            participants.add(user.id)
            
            if len(participants) < giveaway['winners']:
                winners = list(participants)
            else:
                winners = random.sample(list(participants), giveaway['winners'])
            
            if winners:
                embed = discord.Embed(
                    title="🎉 Giveaway Terminé!",
                    description=f"**Gagnants pour {giveaway['prize']}:**",
                    color=discord.Color.green()
                )
                
                winner_mentions = []
                for winner_id in winners:
                    winner = self.bot.get_user(winner_id)
                    if winner:
                        winner_mentions.append(f"<@{winner_id}>")
                
                embed.add_field(name="👑 Gagnants", value="\n".join(winner_mentions) if winner_mentions else "Aucun gagnant", inline=False)
                embed.add_field(name="📊 Participants", value=str(len(participants)), inline=True)
                embed.set_footer(text=f"Créé par {self.bot.get_user(giveaway['creator'])}")
                
                await channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="🎉 Giveaway Terminé!",
                    description=f"Pas assez de participants pour {giveaway['prize']}",
                    color=discord.Color.orange()
                )
                await channel.send(embed=embed)
        
        except Exception as e:
            print(f"Erreur lors de la fermeture du giveaway: {e}")

    @commands.command(name='giveaways')
    async def list_giveaways(self, ctx):
        active = [g for g in self.giveaways.values() if not g['ended'] and g['guild_id'] == ctx.guild.id]
        
        if not active:
            await ctx.send("❌ Aucun giveaway actif")
            return
        
        embed = discord.Embed(
            title="🎉 Giveaways Actifs",
            color=discord.Color.gold()
        )
        
        for i, g in enumerate(active[:10], 1):
            embed.add_field(
                name=f"{i}. {g['prize']}",
                value=f"Fin: <t:{int(g['end_time'].timestamp())}:R>\nGagnants: {g['winners']}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='endgiveaway')
    @commands.has_permissions(manage_guild=True)
    async def force_end_giveaway(self, ctx, giveaway_id: int):
        if giveaway_id not in self.giveaways:
            await ctx.send("❌ Giveaway non trouvé")
            return
        
        await self.end_giveaway(giveaway_id)
        await ctx.send("✅ Giveaway terminé manuellement")

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
