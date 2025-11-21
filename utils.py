import discord
from discord.ext import commands

ADMIN_ID = 1203944242867863613

def is_admin_or_owner(ctx):
    """Vérifier si l'utilisateur est l'admin spécifié ou a les permissions admin du serveur"""
    return ctx.author.id == ADMIN_ID or ctx.author.guild_permissions.administrator

def admin_or_owner():
    """Décorateur pour les commandes admin"""
    def predicate(ctx):
        return is_admin_or_owner(ctx)
    return commands.check(predicate)

def admin_only():
    """Alias pour admin_or_owner"""
    return admin_or_owner()
