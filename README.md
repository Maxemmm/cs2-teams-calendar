# CS2 Teams Calendar

[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://docker.com)

Génère un calendrier iCalendar (`.ics`) listant les matchs à venir de tes équipes Counter-Strike 2 préférées, à partir de l'API [PandaScore](https://pandascore.co). Mis à jour automatiquement toutes les heures via GitHub Actions.

## Fonctionnalités

- Suivi multi-équipes avec dédoublonnage automatique des matchs communs
- Durées d'événement adaptées au format du match (BO1/BO3/BO5/BO7)
- Compatible avec tous les calendriers (Google, Apple, Outlook...) via abonnement `.ics`
- Mise à jour automatique (GitHub Actions) ou manuelle (local, Docker)
- Gestion d'erreurs par équipe : une équipe introuvable ou en échec ne bloque pas les autres

## Installation

### GitHub Actions (recommandé)

1. Fork ce repository
2. Crée une clé API gratuite sur [pandascore.co](https://pandascore.co) (sans carte bancaire)
3. Dans le fork : `Settings > Secrets and variables > Actions` → ajoute un secret `PANDASCORE_TOKEN`
4. Édite `config.json` avec tes équipes
5. Le calendrier se met à jour automatiquement ; déclenchement manuel possible depuis l'onglet **Actions**

### Local

```bash
git clone https://github.com/Maxemmm/cs2-teams-calendar.git
cd cs2-teams-calendar
pip install -r requirements.txt
cp config.example.json config.json   # puis personnalise-le
export PANDASCORE_TOKEN="votre_token"
python generate_calendar.py
```

### Docker

```bash
docker-compose up -d
```

Configure `config.json` et la variable d'environnement `PANDASCORE_TOKEN` (fichier `.env`) avant de lancer. Le service `cs2-calendar-cron` régénère le calendrier toutes les heures à l'intérieur du conteneur.

## Configuration

`config.json` (voir `config.example.json`) :

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
  "max_matches_per_team": 50
}
```

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `teams` | `array` | ✅ | Noms des équipes CS2 à suivre (tels qu'ils apparaissent sur PandaScore) |
| `match_durations` | `object` | | Durées estimées par format, en heures |
| `output_file` | `string` | ✅ | Nom du fichier `.ics` généré |
| `max_matches_per_team` | `number` | | Limite de matchs récupérés par équipe (défaut : 50) |

> La clé API ne va pas dans `config.json` : elle se fournit via la variable d'environnement `PANDASCORE_TOKEN` (secret GitHub Actions en CI, export local en dev).

Si une seule équipe est configurée et qu'aucun match à venir n'est trouvé pour elle, le calendrier est vidé automatiquement pour éviter d'y laisser des matchs périmés.

## Mise à jour automatique

Le workflow `.github/workflows/update-calendar.yml` s'exécute :

- **Toutes les heures, de 6h à 23h UTC** (`0 6-23 * * *`)
- Manuellement, depuis l'onglet **Actions** (`workflow_dispatch`)
- À chaque push sur `main`

Le fichier `.ics` n'est re-commité que s'il a changé.

## S'abonner au calendrier (Apple / Android)

Le fichier `.ics` étant régénéré et commité automatiquement, tu peux t'y **abonner** une seule fois : l'app calendrier le relira périodiquement au lieu d'avoir à le réimporter.

```
https://raw.githubusercontent.com/Maxemmm/cs2-teams-calendar/main/matches.ics
```

**Apple (macOS / iOS)** — app Calendrier → `Fichier > Nouvel abonnement...` (macOS) ou `Réglages > Calendrier > Comptes > Ajouter un compte > Autre > Calendrier en abonnement` (iOS). Colle l'URL ci-dessus (ou son équivalent `webcal://`), puis choisis la fréquence d'actualisation la plus courte disponible.

**Android** — pas d'abonnement natif : passe par [calendar.google.com](https://calendar.google.com) (navigateur) → `Autres agendas > + > À partir de l'URL`, colle l'URL, puis retrouve l'agenda dans l'app Google Calendar.

> Ce sont les apps calendrier qui décident de leur fréquence de rafraîchissement (souvent toutes les quelques heures), indépendamment du cron GitHub Actions — un léger décalage d'affichage est normal.

## Structure du projet

```
cs2-teams-calendar/
├── .github/workflows/update-calendar.yml   # Automatisation GitHub Actions
├── generate_calendar.py                    # Script principal
├── config.json                             # Configuration utilisateur
├── config.example.json                     # Configuration d'exemple
├── requirements.txt                        # Dépendances Python
├── Dockerfile
├── docker-compose.yml
├── CHANGELOG.md
├── matches.ics                             # Calendrier généré
└── .gitignore
```

## Formats de matchs

| Format | Durée estimée |
|--------|----------------|
| BO1 | 1h30 |
| BO3 | 4h |
| BO5 | 6h30 |
| BO7 | 9h |

## API utilisée

Ce projet utilise l'API officielle **[PandaScore](https://pandascore.co)** (tier gratuit) pour les données d'équipes, de matchs, d'horaires et de streams. Historique des versions et détails techniques : [CHANGELOG.md](./CHANGELOG.md).

## Contribution

1. Fork le repository
2. Crée une branche (`git checkout -b feature/ma-feature`)
3. Commit (`git commit -m 'Add ma-feature'`)
4. Push (`git push origin feature/ma-feature`)
5. Ouvre une Pull Request
