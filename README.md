# 🎮 CS2 Teams Calendar

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/your-username/cs2-teams-calendar/releases)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://docker.com)
[![GitHub Actions](https://img.shields.io/badge/actions-enabled-green.svg)](https://github.com/features/actions)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

> **🎯 Version 2.0.0** - Calendrier automatique professionnel pour suivre les matchs de vos équipes Counter-Strike 2 préférées !

[![CS2 Teams Calendar](https://img.shields.io/badge/CS2-Born%20to%20Win-red.svg)](https://counter-strike.net)

## ✨ Fonctionnalités

- **📅 Génération automatique** de calendrier iCalendar (.ics) pour CS2
- **⚙️ Support multi-équipes** - suivez plusieurs équipes simultanément  
- **⏱️ Durées intelligentes** basées sur le format des matchs (BO1, BO3, BO5, BO7)
- **🔄 Mise à jour automatique** 2x par jour (00h et 12h UTC) via GitHub Actions
- **🚀 Lancement manuel** possible à tout moment via l'interface GitHub
- **📱 Compatible** avec tous les calendriers (Outlook, Google Calendar, Apple Calendar, etc.)
- **🎮 Spécialisé Counter-Strike 2** avec l'API officielle PandaScore
- **🐳 Support Docker** pour déploiement en production
- **🛠️ Configuration avancée** avec validation des paramètres
- **📊 Logging professionnel** avec gestion d'erreurs robuste
- **⚡ Optimisé et sécurisé** avec timeout, cache et gestion de versions

## 🚀 Installation rapide

### Méthode 1: GitHub Actions (Recommandée) 🌐

1. **Fork** ce repository sur votre compte GitHub
2. Créez une clé API gratuite sur [pandascore.co](https://pandascore.co) (aucune carte bancaire requise)
3. Dans votre fork, allez dans `Settings > Secrets and variables > Actions` et ajoutez un secret nommé `PANDASCORE_TOKEN` avec votre clé
4. Modifiez `config.json` avec vos équipes préférées
5. Le calendrier se mettra à jour **automatiquement** 2x par jour !
6. Utilisez l'onglet "Actions" pour déclencher une mise à jour manuelle

### Méthode 2: Installation locale 🖥️

1. Clonez le repository :
```bash
git clone https://github.com/votre-username/cs2-teams-calendar.git
cd cs2-teams-calendar
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurez vos équipes :
```bash
# Copiez l'exemple et personnalisez
cp config.example.json config.json
```

4. Créez une clé API gratuite sur [pandascore.co](https://pandascore.co) et exportez-la :
```bash
export PANDASCORE_TOKEN="votre_token"
```

5. Lancez le script :
```bash
python generate_calendar.py
```

### Méthode 3: Docker 🐳

1. Configurez votre `config.json`
2. Déployez avec Docker Compose :
```bash
docker-compose up -d
```
3. Votre calendrier sera généré automatiquement et planifié !

## ⚙️ Configuration

### Configuration de base

Le fichier `config.json` est **obligatoire** ! Utilisez l'exemple fourni :

```json
{
  "teams": ["Vitality", "Gentle Mates", "3DMAX"],
  "match_durations": {
    "bo1": 1.5,
    "bo3": 4.0,
    "bo5": 6.5,
    "bo7": 9.0
  },
  "output_file": "matches.ics",
  "max_matches_per_team": 50,
  "timezone": "UTC",
  "calendar_name": "CS2 Teams Calendar",
  "include_tournament_info": true,
  "include_team_info": true
}
```

> ℹ️ La clé API PandaScore ne se met pas dans `config.json` : elle se fournit via la variable d'environnement `PANDASCORE_TOKEN` (secret GitHub Actions en production, export local en développement).

### 🔧 Options de configuration

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| **`teams`** | `array` | ✅ | Liste des équipes CS2 à suivre |
| **`match_durations`** | `object` | ⚪ | Durées estimées selon le format (heures) |
| **`output_file`** | `string` | ✅ | Nom du fichier .ics généré |
| **`max_matches_per_team`** | `number` | ⚪ | Limite de matchs par équipe (défaut: 50) |
| **`timezone`** | `string` | ⚪ | Force de l'environnement (défaut: UTC) |
| **`calendar_name`** | `string` | ⚪ | Nom affiché du calendrier |
| **`include_tournament_info`** | `boolean` | ⚪ | Inclure les infos du tournoi |
| **`include_team_info`** | `boolean` | ⚪ | Inclure les infos de l'équipe suivie |

⚪ = Optionnel (valeurs par défaut incluses)

## 🔄 Mise à jour automatique

### 📅 Planning automatique

Le projet utilise GitHub Actions pour se mettre à jour automatiquement :
- **⏰ Planifié** : **2x par jour** à 00h00 et 12h00 UTC
- **🚀 Manuel** : Via l'onglet "Actions" de GitHub
- **💾 Auto-commit** : Le fichier .ics est commité automatiquement si pas de changements
- **✅ Validation** : Configuration vérifiée avant chaque génération

### 🎛️ Déclencheurs GitHub Actions

- **Schedule** : `0 0 * * *` et `0 12 * * *` (cron)
- **Manual** : `workflow_dispatch` depuis l'interface GitHub
- **Push** : Déclenché sur push vers `main`
- **PR** : Validation sur les Pull Requests

### 📊 Monitoring

Chaque exécution génère un rapport détaillé :
- ✅ Équipes traitées avec succès
- ⚠️ Équipes non trouvées ou en erreur  
- 📅 Nombre d'événements créés
- 💾 Changements détectés ou non

## 📱 S'abonner au calendrier (Apple / Android)

Le fichier `.ics` étant régénéré et commité automatiquement 2x par jour, tu peux t'y **abonner** une seule fois : ton calendrier ira relire le fichier périodiquement au lieu d'avoir à le réimporter à chaque fois.

Lien à utiliser (adapte `matches.ics` si tu as changé `output_file` dans `config.json`) :

```
https://raw.githubusercontent.com/Maxemmm/cs2-teams-calendar/main/matches.ics
```

### 🍎 Apple (macOS / iOS)

1. App **Calendrier** → `Fichier > Nouvel abonnement...` (macOS) ou `Réglages > Calendrier > Comptes > Ajouter un compte > Autre > Calendrier en abonnement` (iOS)
2. Colle l'URL ci-dessus (le préfixe `webcal://` fonctionne aussi et ouvre directement l'app si tu cliques le lien depuis Safari) :
   ```
   webcal://raw.githubusercontent.com/Maxemmm/cs2-teams-calendar/main/matches.ics
   ```
3. Choisis la fréquence d'actualisation (le plus fréquent disponible, ex. "toutes les heures")

### 🤖 Android

Android n'a pas d'abonnement natif : passe par **Google Calendar**, qui se synchronise ensuite automatiquement sur ton téléphone.

1. Sur [calendar.google.com](https://calendar.google.com) (navigateur, pas l'app mobile) → `Autres agendas > + > À partir de l'URL`
2. Colle l'URL `https://...` ci-dessus → `Ajouter l'agenda`
3. Le calendrier apparaît ensuite automatiquement dans l'app Google Calendar sur Android

> ⚠️ Ce sont les apps calendrier (Apple / Google) qui décident de la fréquence de rafraîchissement (souvent toutes les quelques heures), pas le rythme du cron GitHub Actions — l'affichage peut donc avoir un léger décalage après chaque mise à jour.

## 📁 Structure du projet

```
cs2-teams-calendar/
├── .github/workflows/
│   └── update-calendar.yml              # GitHub Actions optimisé
├── generate_calendar.py                 # Script principal v2.0
├── config.json                          # Configuration utilisateur
├── config.example.json                  # Configuration d'exemple
├── requirements.txt                     # Dépendances avec versions
├── Dockerfile                          # Conteneur Docker
├── docker-compose.yml                  # Orchestration Docker
├── CHANGELOG.md                        # Historique des versions
├── matches.ics                         # Calendrier généré (toutes équipes)
├── .gitignore                          # Fichiers ignorés par Git
└── README.md                           # Documentation complète
```

### 🐳 Utilisation avec Docker

Le projet inclut un conteneur Docker professionnel :

```bash
# Construction de l'image
docker build -t cs2-calendar .

# Exécution ponctuelle
docker run -v ./config.json:/app/config.json \
           -v ./output:/app/output \
           cs2-calendar

# Ou avec docker-compose (recommandé)
docker-compose up -d
```

**Avantages Docker :**
- 🔒 Environnement isolé et sécurisé
- 🚀 Déploiement simplifié
- 📅 Planification automatique avec cron
- 🔄 Mises à jour automatiques
- 📊 Logs centralisés

## 🎯 Formats de matchs supportés

- **BO1** : 1h30 (match rapide)
- **BO3** : 4h (meilleur de 3)
- **BO5** : 6h30 (meilleur de 5)
- **BO7** : 9h (meilleur de 7)

## 🔍 Équipes CS2 populaires

### 🏆 Top Teams Mondiales

| Nom de l'équipe | Pays/Région | Statut |
|-----------------|-------------|--------|
| **Vitality** | 🇫🇷 France | Actuel #1 mondial |
| **NAVI** | 🇺🇦 Ukraine | Top Tier mondial |
| **FaZe** | 🌍 International | Top Tier mondial |
| **G2** | 🇪🇺 Europe | Top European |
| **MOUZ** | 🇩🇪 Allemagne | Team rising |

### 🌟 Autres équipes populaires

- **Astralis** 🇩🇰 (Ancienne domination)
- **Cloud9** 🇺🇸 (Équipe américaine)
- **Team Liquid** 🇺🇸 (Équipe internationale)
- **NIP** 🇸🇪 (Ninjas in Pyjamas)
- **Spirit** 🇷🇺 (Top CIS)
- **Gentle Mates** 🇫🇷 (Équipe française)

### 💡 Conseils pour la configuration

- ✅ **Recherche intelligente** : Le script trouve automatiquement l'équipe même avec des variations de nom
- 🎯 **Noms exacts recommandés** : Utilisez les noms tels qu'ils apparaissent sur [PandaScore](https://pandascore.co)
- 📝 **Case-sensitive** : Respectez la casse pour une correspondance optimale
- 🔍 **Test local** : Testez votre configuration avant le déploiement production

## 🔗 API utilisée

Ce projet utilise l'API officielle **[PandaScore](https://pandascore.co)** (tier gratuit, sans carte bancaire) qui fournit :
- 📊 Les données des équipes CS2
- 🎮 Les matchs et tournois à venir
- 📅 Les horaires et formats de matchs (BO1/BO3/BO5/BO7)
- 📺 Les liens de stream quand ils sont disponibles

> Le projet utilisait auparavant du scraping non-officiel de bo3.gg, mais ce site a mis en place une protection anti-bot qui bloque désormais les requêtes automatisées (403 Forbidden) — d'où la migration vers une API officielle et documentée, gratuite pour ce usage.

## 📈 Performance et fiabilité

### ⚡ Optimisations v2.0
- **⏱️ Timeout** : Évite les hangs avec limite de 10 minutes
- **🔄 Cache pip** : Builds GitHub Actions plus rapides  
- **📊 Monitoring** : Rapports détaillés à chaque exécution
- **🛡️ Gestion d'erreurs** : Fallback gracieux pour équipes non trouvées
- **💾 Commits intelligents** : Pas de commit si aucun changement

### 🚨 Gestion des erreurs
- ✅ **Équipes introuvables** : Liste claire des échecs sans crash
- 📝 **Logs détaillés** : Debugging facilité avec niveaux de log
- 🔄 **Retry automatique** : Les équipes valides ne bloquent pas les autres
- 💡 **Messages clairs** : Instructions précises en cas d'erreur

## 🤝 Contribution

Les contributions sont les bienvenues ! Voir le [CHANGELOG.md](./CHANGELOG.md) pour les nouveautés.

### 🚀 Comment contribuer
1. 🍴 Fork le repository
2. 🌱 Créez votre branche feature (`git checkout -b feature/amazing-feature`)
3. 💾 Commit vos changements (`git commit -m 'Add amazing feature'`)
4. 🚀 Push vers la branche (`git push origin feature/amazing-feature`)
5. 🔗 Ouvrez une Pull Request

### 💬 Suggestions
- 🐛 Signaler des bugs
- ✨ Proposer des nouvelles fonctionnalités
- 📚 Améliorer la documentation
- 🎨 Optimiser le code ou les workflows

## 📄 Licence

MIT License - Libre d'utilisation pour projets personnels et commerciaux.

---

<div align="center">
<strong>🎮 Ne ratez plus jamais un match CS2 !</strong><br>
⭐⭐⭐⭐⭐ Si ce projet vous aide, pensez à mettre une étoile !
</div>