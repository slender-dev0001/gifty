# 📋 Documentation Complète du Bot Discord

## 🔗 COMMANDES DE LIEN COURT

### **+createlink <URL>** / **/createlink <URL>**
**Utilité:** Créer un lien court personnalisé qui redirige vers une URL longue.
Permet de tracker les visites de manière sécurisée via un court ID.

**Usage:** `+createlink https://www.example.com/long/url`

---

### **+getlink <ID>** / **/getlink <ID>**
**Utilité:** Récupérer les informations d'un lien court (URL originale, nombre de clics).

**Usage:** `+getlink abc123`

---

### **+mylinks** / **/mylinks**
**Utilité:** Afficher la liste de tous vos liens courts créés avec le nombre de visites.

**Usage:** `+mylinks`

---

### **+linkvisits <ID>** / **/linkvisits <ID>**
**Utilité:** Voir tous les visiteurs authentifiés d'un lien court (Discord ID, username, IP, localisation, appareil).

**Usage:** `+linkvisits abc123`

---

## 🔍 COMMANDES OSINT

### **+searchip <IP>** / **/searchip <IP>**
**Utilité:** Rechercher les informations géographiques et techniques d'une adresse IP.

**Données retournées:**
- Pays, Région, Ville
- Fuseau horaire
- Coordonnées GPS (Latitude/Longitude)
- Fournisseur Internet (FAI)
- Organisation
- Code pays

**Usage:** `+searchip 8.8.8.8`

**⚠️ Comment utiliser:** Cette commande permet une reconnaissance passive d'une adresse IP. Les résultats proviennent d'une base de données publique (ip-api.com). C'est légal car les données sont publiques. À utiliser pour identifier l'emplacement d'un serveur, une connexion douteuse, ou des fins de sécurité réseau.

---

### **+searchname <PRENOM> <NOM>** / **/searchname <PRENOM> <NOM>**
**Utilité:** Recherche OSINT complète sur une personne par son nom et prénom.

**Données retournées:**
- Email(s) trouvé(s) correspondant aux patterns communs
- Fuites de données (HaveIBeenPwned)
- Comptes sociaux trouvés (GitHub, Twitter, Instagram, Reddit, TikTok, Twitch, YouTube)
- Variantes de noms d'utilisateur possibles

**Usage:** `+searchname John Doe`

**⚠️ Comment utiliser:** Cette commande utilise uniquement des données publiques disponibles sur internet. Elle teste des patterns d'email courants (firstname.lastname@gmail.com, etc) et vérifie s'ils ont été compromis dans des fuites publiques. Elle cherche aussi les comptes sociaux en testant différentes variantes du nom. À utiliser pour vérifier si quelqu'un a eu ses données compromises, retrouver un compte social public, ou faire une vérification d'identité. NE PAS utiliser pour du harcèlement ou du doxxing. Les résultats sont envoyés en DM.

---

### **+useroslint <DISCORD_ID>**
**Utilité:** Recherche OSINT sur un utilisateur Discord en utilisant son ID.

**Données retournées:**
- Nom d'utilisateur Discord
- ID Discord
- Date de création du compte
- Email(s) possibles basés sur le nom Discord
- Comptes sociaux (GitHub, Twitter, Instagram, Reddit, TikTok, Twitch, YouTube)
- Fuites de données associées à l'email

**Usage:** `+useroslint 123456789012345678`

**⚠️ Comment utiliser:** Cette commande cherche un utilisateur par son ID Discord et effectue une recherche OSINT similaire à +searchname. Elle est utile pour vérifier les comptes sociaux d'un utilisateur ou vérifier si ses données ont été compromises. Les résultats sont basés sur des données publiques uniquement. À utiliser pour la sécurité, les modérations, ou les vérifications. Les résultats sont envoyés en DM.

---

### **+searchphone <NUMERO>**
**Utilité:** Recherche OSINT complète sur un numéro de téléphone.

**Données retournées:**
- Vérification des fuites de données (HaveIBeenPwned)
- Sites de recherche inverse disponibles (Annuaire inverse français, Pages Jaunes, Truecaller, etc)
- Localisation estimée (Pays, Région, Ville, FAI)
- Liens directs vers les moteurs de recherche (Google, LinkedIn, Facebook, Twitter, Reddit, Instagram)

**Format accepté:** Tous les formats sont acceptés automatiquement (0612345678, +33612345678, (06) 12-34-56-78, etc)

**Usage:** `+searchphone 0612345678` ou `+searchphone +33612345678`

**⚠️ Comment utiliser:** Cette commande recherche un numéro de téléphone dans des bases de données publiques et fournit des liens vers des sites de recherche inverse. Les données directement retournées (fuites, localisation) proviennent de sources publiques. Les liens fournis pointent vers des services de recherche inverse légaux. À utiliser pour identifier un numéro inconnu, vérifier si un numéro a été compromis, ou tracer l'origine géographique. NE PAS utiliser pour du harcèlement. Les résultats sont envoyés en DM.

---

### **+searchemail <EMAIL>**
**Utilité:** Recherche OSINT complète sur une adresse email.

**Données retournées:**
- Vérification des fuites de données (HaveIBeenPwned)
- Validation du domaine email
- Comptes sociaux associés (GitHub, Twitter, Instagram, Reddit, TikTok, Twitch, YouTube, LinkedIn)
- Liens directs vers les moteurs de recherche (Google, LinkedIn, Facebook, Twitter, Reddit, Instagram)
- Informations sur le domaine de l'email

**Format accepté:** Tout format d'email valide (exemple@domain.com)

**Usage:** `+searchemail john.doe@gmail.com`

**⚠️ Comment utiliser:** Cette commande recherche une adresse email dans des bases de données publiques et vérifie si elle a été compromise dans des fuites de données. Elle teste les comptes sociaux associés à cet email. À utiliser pour vérifier si votre email a été compromis, retrouver les comptes associés à un email, ou faire de la reconnaissance. NE PAS utiliser pour du harcèlement ou du phishing. Les résultats sont envoyés en DM.

---

### **+searchusername <USERNAME>**
**Utilité:** Recherche un username sur plusieurs réseaux sociaux et plateformes.

**Données retournées:**
- Comptes trouvés sur 13+ réseaux (GitHub, Twitter, Instagram, Reddit, TikTok, Twitch, YouTube, LinkedIn, GitLab, Telegram, Pastebin, Medium, Dev.to)
- Liens directs vers les profils trouvés
- Résultats de recherche (Google, DuckDuckGo)

**Format accepté:** N'importe quel username sans espaces

**Usage:** `+searchusername john_doe`

**⚠️ Comment utiliser:** Cette commande teste un username sur les principaux réseaux sociaux. Utile pour vérifier la disponibilité d'un username, retrouver les comptes d'une personne, ou faire de la reconnaissance de personnes publiques. NE PAS utiliser pour du harcèlement. Les résultats sont envoyés en DM.

---

### **+searchurl <URL>**
**Utilité:** Analyser une URL et extraire des informations sur le site.

**Données retournées:**
- Code de statut HTTP et Content-Type
- Titre de la page et métadescription
- Headers du serveur (Server, X-Powered-By)
- Taille du contenu
- Informations DNS (Hostname, IP)

**Format accepté:** URL complète ou partielle (exemple.com ou https://exemple.com)

**Usage:** `+searchurl https://www.example.com` ou `+searchurl example.com`

**⚠️ Comment utiliser:** Cette commande analyse un site web public pour extraire les métadonnées et informations techniques. Utile pour identifier les technologies utilisées, vérifier l'état d'un site, ou faire de la reconnaissance de domaines. Analysez uniquement des sites publics. Les résultats sont envoyés en DM.

---

### **+searchlocation <LATITUDE> <LONGITUDE>**
**Utilité:** Recherche d'informations géographiques détaillées pour des coordonnées GPS.

**Données retournées:**
- Adresse complète (street, code postal, ville, pays)
- Localisation estimée (ville, région, pays)
- Fuseau horaire
- Liens directs vers les cartes (OpenStreetMap, Google Maps)

**Format accepté:** Latitude et longitude en décimal (48.8566 2.3522)

**Usage:** `+searchlocation 48.8566 2.3522`

**⚠️ Comment utiliser:** Cette commande utilise OpenStreetMap pour localiser des coordonnées GPS publiques. Utile pour identifier un lieu à partir de coordonnées, rechercher les informations à proximité d'une location, ou faire de la reconnaissance. Respect de la vie privée obligatoire. Les résultats sont envoyés en DM.

---

### **+searchphone_reverse <NUMERO>**
**Utilité:** Recherche inversée complète sur un numéro de téléphone avec sources étendues.

**Données retournées:**
- Vérification des fuites de données (HaveIBeenPwned)
- Sites de recherche inverse (Truecaller, Annuaire inverse, Pages Jaunes, etc)
- Applications de messagerie (WhatsApp, Telegram, Signal)
- Localisation estimée (Pays, Ville, FAI)
- Liens vers moteurs de recherche sociaux

**Format accepté:** Tous les formats (0612345678, +33612345678, (06) 12-34-56-78)

**Usage:** `+searchphone_reverse 0612345678` ou `+searchphone_reverse +33612345678`

**⚠️ Comment utiliser:** Cette commande fait une recherche inversée complète incluant les sites de lookup, les apps de messaging, et les données publiques. À utiliser pour identifier un numéro inconnu, vérifier un numéro douteux, ou retrouver les apps associées. NE PAS utiliser pour du harcèlement ou stalking. Les résultats sont envoyés en DM.

---

## 📊 COMMANDES UTILITAIRES

### **+serverinfo** / **/serverinfo**
**Utilité:** Afficher les informations complètes du serveur (nom, ID, nombre de membres, salons, rôles, etc).

### **+userinfo** / **/userinfo** [membre]
**Utilité:** Afficher les informations d'un utilisateur (ID, date de création, rôles, statut).

### **+roleinfo** / **/roleinfo** <rôle>
**Utilité:** Afficher les informations d'un rôle (position, couleur, nombre de membres).

### **+channelinfo** / **/channelinfo** [salon]
**Utilité:** Afficher les informations d'un salon (type, NSFW, mode lent).

### **+stats** / **/stats**
**Utilité:** Afficher les statistiques du bot (ping, nombre de serveurs, utilisateurs, extensions).

### **/clear <NOMBRE>** (Admin)
**Utilité:** Supprimer un nombre spécifique de messages (max 100).

### **/kick <UTILISATEUR> [RAISON]** (Admin)
**Utilité:** Expulser un utilisateur du serveur.

### **/ban <UTILISATEUR> [RAISON]** (Admin)
**Utilité:** Bannir un utilisateur du serveur.

### **/unban <NOM>** (Admin)
**Utilité:** Débannir un utilisateur du serveur.

---

## ⚠️ AVERTISSEMENTS LÉGAUX

**OSINT - Open Source Intelligence:**

L'OSINT est la collecte et l'analyse d'informations provenant de sources publiques légales. Les commandes OSINT du bot utilisent UNIQUEMENT:
- Les données déjà publiques en ligne
- Les API publiques (HaveIBeenPwned, GitHub, etc)
- Les moteurs de recherche
- Les annuaires publics

**Légalité:**
- ✅ **LÉGAL**: Collecter des informations publiques
- ✅ **LÉGAL**: Vérifier si vos données ont été compromises
- ✅ **LÉGAL**: Identifier un numéro de téléphone inconnu
- ✅ **LÉGAL**: Retrouver les comptes sociaux publics d'une personne

**ILLÉGAL:**
- ❌ **ILLÉGAL**: Utiliser les données pour du harcèlement
- ❌ **ILLÉGAL**: Utiliser les données pour du doxxing
- ❌ **ILLÉGAL**: Faire chanter ou menacer quelqu'un
- ❌ **ILLÉGAL**: Accéder à des données privées
- ❌ **ILLÉGAL**: Prétendre être quelqu'un d'autre

**Respect de la vie privée obligatoire.** Chaque commande rappelle cet avertissement.

---

## 🔒 SYSTÈME DE SÉCURITÉ

### Lien Court avec Notifikation
Lorsqu'un lien court est cliqué:
1. La page affiche tous les détails techniques de la visite
2. Le créateur du lien reçoit une notification DM complète
3. Les données incluent: IP, Appareil, Navigateur, Localisation, OS
4. Les visites sont enregistrées en base de données

---

## 📝 EXEMPLES D'UTILISATION

### Exemple 1: Vérifier si mon email a été compromis
```
+searchname John Doe
```
→ Retourne les emails trouvés et les fuites de données associées

### Exemple 2: Retrouver le compte GitHub d'un utilisateur Discord
```
+useroslint 123456789012345678
```
→ Affiche tous les comptes sociaux trouvés

### Exemple 3: Identifier un numéro de téléphone inconnu
```
+searchphone 0612345678
```
→ Fournit les sites de recherche inverse et les informations publiques

### Exemple 4: Vérifier l'emplacement d'une IP suspecte
```
+searchip 123.45.67.89
```
→ Affiche le pays, la ville, le FAI et les coordonnées GPS

---

**Dernière mise à jour:** novembre 2025
**Versión du bot:** 1.0.0
