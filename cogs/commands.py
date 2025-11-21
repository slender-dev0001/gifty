import discord
from discord.ext import commands

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command(name='help')
    # async def help_command(self, ctx):
    #     embed = discord.Embed(
    #         title="📚 Bot Discord Complet - Commandes",
    #         description="**90+ Commandes Disponibles**",
    #         color=discord.Color.blue()
    #     )
    #
    #     embed.add_field(
    #         name="🎮 **Basiques**",
    #         value="`+hello` • `+ping` • `+say <msg>` • `+avatar [@user]`",
    #         inline=False
    #     )
    #
    #     embed.add_field(
    #         name="📊 **Slash Commands** (Modernes avec /)",
    #         value="`/slashhelp` • `/ping` • `/usercard [@user]` • `/leaderboard` • `/about`",
    #         inline=False
    #     )
    #
    #     embed.add_field(
    #         name="ℹ️ **Informations**",
    #         value="`+serverinfo` • `+userinfo [@u]` • `+roleinfo <role>` • `+channelinfo [channel]` • `+stats`",
    #         inline=False
    #     )
    #
    #     embed.add_field(
    #         name="🛡️ **Modération** (Admin)",
    #         value="`+clear <n>` • `+kick @user` • `+ban @user` • `+unban <name>` • `+mute @user` • `+unmute @user`",
    #         inline=False
    #     )
    #
    #     embed.add_field(
    #         name="🎮 **Interactions Avancées**",
    #         value="`+buttons` • `+select` • `+modal` (Buttons, Menus, Modales)",
    #         inline=False
    #     )
    #
    #     embed.add_field(
    #         name="🎭 **Événements & Rôles**",
    #         value="`+autoroles <role>` • `+reactionrole <id> <emoji> <role>` • `+welcome` • `+setuplogs`",
    #         inline=False
    #     )
    #
    #     embed.add_field(
    #         name="👤 **Profils & XP**",
    #         value="`+profile [@u]` • `+setbio <bio>` • `+balance [@u]` • `+addbal @user <n>` • `+leaderboard`",
    #         inline=False
    #     )
    #
    #     embed.add_field(
    #         name="⚙️ **Customisation Serveur** (Admin)",
    #         value="`+prefix <new>` • `+setwelcome <msg>` • `+setleave <msg>` • `+setautorole <role>`",
    #         inline=False
    #     )
    #
    #     embed.add_field(
    #         name="👥 **Invitations**",
    #         value="`+invites [@user]` • `+inviteleaderboard` (Tracker d'invitations)",
    #         inline=False
    #     )
    #
    #     embed.add_field(
    #         name="🎫 **Support & Tickets** (Admin)",
    #         value="`+ticketsystem` - Créer la base de tickets",
    #         inline=False
    #     )
    #
    #     embed.add_field(
    #         name="🔐 **Vérification** (Admin)",
    #         value="`+setupverification` - Captcha mathématique auto",
    #         inline=False
    #     )
    #
    #     embed.add_field(
    #         name="🎉 **Giveaways** (Admin)",
    #         value="`+giveaway <durée> <winners> <prize>` • `+giveaways` • `+endgiveaway <id>`",
    #         inline=False
    #     )
    #
    #     embed.add_field(
    #         name="🎨 **Outils Créatifs**",
    #         value="`+qrcode <texte>` (QR Code) • `+ascii <texte>` (ASCII Art)",
    #         inline=False
    #     )
    #
    #     embed.add_field(
    #         name="🎲 **Jeux & Plaisir**",
    #         value="`+dice` • `+flip` • `+8ball <question>`",
    #         inline=False
    #     )
    #
    #     embed.set_footer(text="✨ Réaction-rôles • Logs complets • XP système • BD SQLite • Prefix personnalisé • Tracker d'invitations")
    #
    #     await ctx.send(embed=embed)

    # @commands.command(name='hello')
    # async def hello(self, ctx):
    #     await ctx.send(f'Bonjour {ctx.author.mention}! 👋')

    # @commands.command(name='say')
    # async def say(self, ctx, *, message):
    #     await ctx.send(message)

    # @commands.command(name='ping')
    # async def ping(self, ctx):
    #     latence = round(self.bot.latency * 1000)
    #     await ctx.send(f'🏓 Pong! Latence: {latence}ms')

    # @commands.command(name='avatar')
    # async def avatar(self, ctx, member: discord.Member = None):
    #     member = member or ctx.author
    #     embed = discord.Embed(
    #         title=f"Avatar de {member}",
    #         color=member.color
    #     )
    #     embed.set_image(url=member.avatar.url if member.avatar else None)
    #     await ctx.send(embed=embed)

    @commands.command(name='help')
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="📋 INVENTAIRE COMPLET DES COMMANDES",
            description="**Dernière mise à jour:** 20/11/2025 - **MISE À JOUR TERMINÉE ✅**\n**50+ Commandes Disponibles**",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="🎯 COMMANDES D'AIDE & INFORMATION",
            value="`+aide` ✅ - Affiche l'aide complète du bot\n`+googlehint` ✅ - Guide Google Dorking pour l'OSINT\n`+helplink` ✅ - Répertoire complet des commandes",
            inline=False
        )

        embed.add_field(
            name="⚙️ CONFIGURATION SERVEUR",
            value="`+prefix <nouveau>` ✅ - Changer le préfixe du bot\n`+setwelcome <message>` ✅ - Message de bienvenue\n`+setleave <message>` ✅ - Message de départ\n`+setautorole <role>` ✅ - Rôle automatique",
            inline=False
        )

        embed.add_field(
            name="🔗 LIENS COURTS & SUIVI",
            value="`+createlink <URL>` ✅ - Créer un lien court\n`+getlink <ID>` ✅ - Récupérer les infos d'un lien\n`+mylinks` ✅ - Voir tous vos liens\n`+linkvisits <ID>` ✅ - Voir les visiteurs\n`+createtracker <URL>` ✅ - Créer un tracker\n`+trackstats <id>` ✅ - Voir les stats",
            inline=False
        )

        embed.add_field(
            name="🔍 OSINT & RECHERCHE (13 Commandes)",
            value="`+searchip <IP>` ✅ - Géolocalisation IP\n`+searchname <prénom> <nom>` ✅ - Recherche OSINT par nom\n`+useroslint <user_id>` ✅ - Recherche OSINT Discord\n`+searchusername <username>` ✅ - Cherche username\n`+searchurl <URL>` ✅ - Analyse URL\n`+searchlocation <lat> <lon>` ✅ - Coordonnées GPS\n`+searchphone_reverse <numéro>` ✅ - Recherche téléphone\n`+searchemail <email>` ✅ - Analyser email\n`+reverseemail <email>` ✅ - Recherche inversée email\n`+checkemail <email>` ✅ - Vérifier si compromis\n`+checkip <IP>` ✅ - Vérifier si compromise\n`+checkusername <username>` ✅ - Vérifier username",
            inline=False
        )

        embed.add_field(
            name="📊 INFORMATIONS SERVEUR & UTILISATEUR",
            value="`+serverinfo` ✅ - Infos du serveur\n`+userinfo [@user]` ✅ - Infos utilisateur\n`+roleinfo <rôle>` ✅ - Infos du rôle\n`+channelinfo [#salon]` ✅ - Infos du salon\n`+stats` ✅ - Stats du bot",
            inline=False
        )

        embed.add_field(
            name="👤 PROFILS & ÉCONOMIE",
            value="`+profile [@user]` ✅ - Voir le profil\n`+setbio <bio>` ✅ - Définir une bio\n`+balance [@user]` ✅ - Voir la balance\n`+addbal <@user> <montant>` ✅ - Ajouter des coins (Admin)\n`+leaderboard` ✅ - Classement XP/Level",
            inline=False
        )

        embed.add_field(
            name="👥 INVITATIONS",
            value="`+invites [@user]` ✅ - Statistiques d'invitations\n`+inviteleaderboard` ✅ - Classement des invitations",
            inline=False
        )

        embed.add_field(
            name="🎉 GIVEAWAYS (Admin)",
            value="`+giveaway <durée> <winners> <prix>` ✅ - Créer un giveaway\n`+giveaways` ✅ - Lister les actifs\n`+endgiveaway <id>` ✅ - Terminer un giveaway",
            inline=False
        )

        embed.add_field(
            name="🎨 OUTILS CRÉATIFS",
            value="`+qrcode <texte>` ✅ - Générer un QR Code\n`+ascii <texte>` ✅ - Art ASCII\n`+asciistyles` ✅ - Styles ASCII disponibles",
            inline=False
        )

        embed.add_field(
            name="💬 SLASH COMMANDS (Avec /)",
            value="`/hello` `/say` `/avatar` `/clear` `/kick` `/ban` `/unban` `/mute` `/unmute` `/serverinfo` `/userinfo` `/roleinfo` `/channelinfo` `/stats` `/createlink` `/getlink` `/mylinks` `/linkvisits` `/searchip` `/searchname` `/useroslint`",
            inline=False
        )

        embed.add_field(
            name="🛡️ MODÉRATION (Admin)",
            value="`+clear <nombre>` - Supprimer des messages\n`+kick <@user> [raison]` - Expulser\n`+ban <@user> [raison]` - Bannir\n`+unban <nom>` - Débannir\n`+mute <@user>` - Rendre muet\n`+unmute <@user>` - Retirer le mute\n`+warn <@user> <raison>` - Avertir\n`+warnings [@user]` - Voir les avertissements",
            inline=False
        )

        embed.set_footer(text="✨ 50+ Commandes Disponibles • Tapez +aide pour plus détails • Préfixe: +")

        await ctx.send(embed=embed)

    @commands.command(name='aide')
    async def aide(self, ctx):
        embed = discord.Embed(
            title="🤖 Aide du Bot Discord",
            description="Liste des commandes disponibles",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="ℹ️ **Informations**",
            value="`+helplink` - Liens d'aide\n`+googlehint` - Conseils de recherche Google",
            inline=False
        )

        embed.add_field(
            name="⚙️ **Configuration**",
            value="`+prefix <nouveau>` - Changer le préfixe du bot\n`+setwelcome <message>` - Définir le message de bienvenue\n`+setleave <message>` - Définir le message de départ\n`+setautorole <role>` - Définir le rôle automatique\n`+autoroles <role>` - Configurer les rôles automatiques\n`+reactionrole <emoji> <role>` - Configurer réaction-rôle\n`+welcome` - Tester le message de bienvenue",
            inline=False
        )

        embed.add_field(
            name="🎉 **Giveaways**",
            value="`+giveaway <durée> <gagnants> <prix>` - Créer un giveaway\n`+giveaways` - Lister les giveaways actifs\n`+endgiveaway <id>` - Terminer un giveaway",
            inline=False
        )

        embed.add_field(
            name="📊 **Invitations**",
            value="`+invites` - Voir vos statistiques d'invitations\n`+inviteleaderboard` - Classement des invitations",
            inline=False
        )

        embed.add_field(
            name="📝 **Logs**",
            value="`+setuplogs` - Créer le canal de logs",
            inline=False
        )

        embed.add_field(
            name="👤 **Profils**",
            value="`+profile [@user]` - Voir le profil d'un utilisateur\n`+setbio <bio>` - Définir votre bio\n`+balance [@user]` - Voir la balance de coins\n`+addbal <@user> <montant>` - Ajouter des coins (Admin)\n`+leaderboard` - Classement des utilisateurs",
            inline=False
        )

        embed.add_field(
            name="🎮 **Commandes Slash**",
            value="`/hello` - Salutation du bot\n`/avatar [@user]` - Afficher l'avatar d'un utilisateur\n`/clear <nombre>` - Supprimer des messages (Admin)\n`/kick <@user> [raison]` - Expulser un utilisateur (Admin)\n`/ban <@user> [raison]` - Bannir un utilisateur (Admin)\n`/unban <nom#tag>` - Débannir un utilisateur (Admin)\n`/mute <@user> [raison]` - Rendre muet un utilisateur (Admin)\n`/unmute <@user>` - Retirer le mute d'un utilisateur (Admin)\n`/serverinfo` - Informations du serveur\n`/userinfo [@user]` - Informations d'un utilisateur\n`/roleinfo <role>` - Informations d'un rôle\n`/channelinfo [#salon]` - Informations d'un salon\n`/stats` - Statistiques du bot\n`/usercard` - Voir votre carte de profil\n`/setemail <email>` - Définir votre email\n`/getemail` - Afficher votre email",
            inline=False
        )

        embed.add_field(
            name="🛡️ **Modération (Admin)**",
            value="`+clear <nombre>` - Supprimer des messages\n`+kick <@user> [raison]` - Expulser un utilisateur\n`+ban <@user> [raison]` - Bannir un utilisateur\n`+unban <nom#tag>` - Débannir un utilisateur\n`+mute <@user> [raison]` - Rendre muet un utilisateur\n`+unmute <@user>` - Retirer le mute d'un utilisateur\n`+embed <titre> <description>` - Créer un embed\n`+warn <@user> <raison>` - Avertir un utilisateur\n`+warnings [@user]` - Voir les avertissements\n`+lock [#salon]` - Verrouiller un salon\n`+unlock [#salon]` - Déverrouiller un salon\n`+settings` - Paramètres du serveur",
            inline=False
        )

        embed.add_field(
            name="💰 **Économie**",
            value="`+balance [@user]` - Voir la balance de coins\n`+addbal <@user> <montant>` - Ajouter des coins (Admin)\n`+leaderboard` - Classement XP/Level",
            inline=False
        )

        embed.set_footer(text="Tapez +help pour plus d'informations • Préfixe actuel: +")

        await ctx.send(embed=embed)

    @commands.command(name='googlehint')
    async def googlehint(self, ctx):
        embed = discord.Embed(
            title="🔍 Google Dorking - Guide Complet",
            description="Techniques avancées de recherche Google pour l'OSINT",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="🎯 **Syntaxe de Base**",
            value="`site:` Limiter à un site\n`intitle:` Chercher dans le titre\n`inurl:` Chercher dans l'URL\n`intext:` Chercher dans le texte",
            inline=False
        )
        
        embed.add_field(
            name="📁 **Fichiers & Types**",
            value="`filetype:pdf` Documents PDF\n`filetype:doc` Documents Word\n`filetype:xls` Feuilles Excel\n`filetype:ppt` Présentations\n`filetype:zip` Archives\n`filetype:sql` Bases de données",
            inline=False
        )
        
        embed.add_field(
            name="🔗 **Opérateurs Avancés**",
            value="`\"exact phrase\"` Recherche exacte\n`word1 OR word2` Ou (OR)\n`word1 -word2` Exclure (NOT)\n`*` Joker (remplace des mots)",
            inline=False
        )
        
        embed.add_field(
            name="👤 **Recherche Personnelle**",
            value="`site:facebook.com \"prénom nom\"` Facebook\n`site:linkedin.com \"prénom nom\"` LinkedIn\n`site:twitter.com username` Twitter\n`site:instagram.com username` Instagram",
            inline=False
        )
        
        embed.add_field(
            name="📧 **Email & Contact**",
            value="`inurl:contact site:example.com` Pages de contact\n`\"email@example.com\"` Email spécifique\n`intext:\"@example.com\" filetype:pdf` Emails dans PDFs",
            inline=False
        )
        
        embed.add_field(
            name="🔐 **Configurations Dangereuses**",
            value="`intitle:\"index of\"` Répertoires non protégés\n`inurl:admin inurl:login` Pages admin\n`intitle:\"Apache\" \"Index of\"` Serveurs exposés\n`inurl:.git` Repos Git exposés",
            inline=False
        )
        
        embed.add_field(
            name="💾 **Données Sensibles**",
            value="`filetype:env` Fichiers .env (secrets)\n`filetype:sql intext:password` Bases de données\n`intext:\"password\" site:pastebin.com` Passwords leakés\n`filetype:conf` Fichiers de configuration",
            inline=False
        )
        
        embed.add_field(
            name="🌐 **Informations Techniques**",
            value="`inurl:robots.txt site:example.com` Fichier robots\n`inurl:sitemap.xml` Sitemaps\n`inurl:backup` Fichiers de backup\n`inurl:install.php` Scripts d'installation",
            inline=False
        )
        
        embed.add_field(
            name="📊 **Exemples Pratiques**",
            value="`site:linkedin.com \"CTO\" \"France\"` Trouver des CTOs\n`site:github.com \"api_key\"` Clés API exposées\n`\"@company.fr\" filetype:pdf` Documents de l'entreprise\n`inurl:webcam inurl:view.shtml` Webcams IoT",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ **Avertissement Légal**",
            value="✅ **Légal**: Données publiques, recherche responsable\n❌ **Illégal**: Accès non autorisé, exploitation malveillante\n\n**Utilisation éthique obligatoire**",
            inline=False
        )
        
        embed.set_footer(text="💡 Consultez +aide pour tous les outils OSINT")
        
        await ctx.send(embed=embed)

    @commands.command(name='helplink')
    async def helplink(self, ctx):
        embed = discord.Embed(
            title="📚 Guide Complet - Toutes les Commandes",
            description="Répertoire de toutes les commandes disponibles",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎮 **Commandes Basiques**",
            value="`+hello` Salutation\n`+ping` Latence du bot\n`+say <msg>` Répéter un message\n`+avatar [@user]` Afficher l'avatar",
            inline=False
        )
        
        embed.add_field(
            name="📊 **Informations Serveur & Utilisateur**",
            value="`+serverinfo` Info du serveur\n`+userinfo [@user]` Info utilisateur\n`+roleinfo <role>` Info du rôle\n`+channelinfo [salon]` Info du salon\n`+stats` Stats du bot",
            inline=False
        )
        
        embed.add_field(
            name="👤 **Profils & XP**",
            value="`+profile [@user]` Voir le profil\n`+setbio <bio>` Définir une bio\n`+balance [@user]` Voir le solde\n`+addbal @user <montant>` Ajouter des coins\n`+leaderboard` Top 10 utilisateurs",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ **Modération (Admin)**",
            value="`+clear <nombre>` Supprimer des messages\n`+kick @user [raison]` Expulser\n`+ban @user [raison]` Bannir\n`+unban <nom>` Débannir\n`+mute @user` Mute un utilisateur\n`+unmute @user` Unmute un utilisateur",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ **Configuration Serveur (Admin)**",
            value="`+prefix <nouveau>` Changer le prefix\n`+setwelcome <msg>` Message de bienvenue\n`+setleave <msg>` Message de départ\n`+setautorole <role>` Rôle automatique",
            inline=False
        )
        
        embed.add_field(
            name="🎮 **Interactions Avancées**",
            value="`+buttons` Boutons interactifs\n`+select` Menu déroulant\n`+modal` Formulaire avec modale",
            inline=False
        )
        
        embed.add_field(
            name="👥 **Invitations**",
            value="`+invites [@user]` Voir les invitations\n`+inviteleaderboard` Leaderboard des invitations",
            inline=False
        )
        
        embed.add_field(
            name="🔗 **Liens Courts & Suivi**",
            value="`+createlink <url>` Créer un lien court\n`+getlink <id>` Récupérer un lien\n`+mylinks` Voir vos liens\n`+linkvisits <id>` 📊 Voir les visiteurs authentifiés (OAuth2)",
            inline=False
        )
        
        embed.add_field(
            name="🔍 **OSINT & Recherche**",
            value="`+aide` 🔥 Tous les outils OSINT\n`+searchip <ip>` Géolocalisation d'une IP\n`+searchname <prénom> <nom>` Recherche OSINT par nom (résultats en DM)\n`/useroslint <id>` 🕵️ Lookup Discord → Infos OSINT en DM",
            inline=False
        )
        
        embed.add_field(
            name="🎨 **Outils Créatifs**",
            value="`+qrcode <texte>` Générer un QR Code\n`+ascii <texte>` Art ASCII\n`+asciistyles` Voir les styles ASCII\n`+imagecreate [titre]` Créer une image tracker\n`+imageclicks <id>` Statistiques d'une image\n`+imagestats` Résumé global des trackers",
            inline=False
        )
        
        embed.add_field(
            name="🎉 **Giveaways (Admin)**",
            value="`+giveaway <durée> <winners> <prix>` Créer un giveaway\n`+giveaways` Liste des giveaways actifs\n`+endgiveaway <id>` Terminer un giveaway",
            inline=False
        )
        
        embed.add_field(
            name="🔐 **Vérification (Admin)**",
            value="`+setupverification` Configurer la vérification\n`+verify` Se vérifier manuellement",
            inline=False
        )
        
        embed.add_field(
            name="🎫 **Support & Tickets (Admin)**",
            value="`+ticketsystem` Créer la base de tickets\n`+ticket` Info sur les tickets",
            inline=False
        )
        
        embed.add_field(
            name="📊 **Slash Commands Modernes** (Avec /)",
            value="`/help` Aide complète\n`/ping` Latence\n`/usercard [@user]` Carte de profil\n`/leaderboard` Top 10\n`/about` À propos\n`/hello` Salutation\n`/say <msg>` Répéter\n`/avatar [@user]` Avatar\n`/dice` Dé\n`/flip` Pile/Face\n`/8ball` Boule magique\n`/createimage <titre>` Créer une image tracker\n`/imageclicks <id>` Statistiques d'une image\n`/clear <n>` Supprimer messages\n`/kick` `/ban` `/unban` `/mute` `/unmute` (Modération)\n`/serverinfo` `/userinfo` `/roleinfo` `/channelinfo` `/stats` (Info)",
            inline=False
        )
        
        embed.set_footer(text="✨ 90+ Commandes • Prefix: + • Slash Commands: / • Support: +helplink")
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Commands(bot))
