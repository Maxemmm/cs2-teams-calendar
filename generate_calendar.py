#!/usr/bin/env python3
"""
🎮 CS2 Teams Calendar Generator
Génère automatiquement un fichier calendrier (.ics) pour suivre les matchs
de vos équipes Counter-Strike 2 préférées.

Source de données : API officielle PandaScore (https://pandascore.co)

Auteur: CS2 Calendar Team
Version: 3.0.0
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta

import requests
from ics import Calendar, Event

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# API PandaScore - toutes les routes CS2 utilisent le préfixe /csgo (historique)
PANDASCORE_BASE_URL = "https://api.pandascore.co/csgo"
PANDASCORE_TOKEN_ENV_VAR = "PANDASCORE_TOKEN"

# Configuration par défaut
DEFAULT_CONFIG = {
    "teams": [],
    "match_durations": {
        "bo1": 1.5,
        "bo3": 4.0,
        "bo5": 6.5,
        "bo7": 9.0
    },
    "output_file": "matches.ics",
    "max_matches_per_team": 50,
    "timezone": "UTC"
}

def load_config():
    """Charge et valide la configuration depuis config.json"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            user_config = json.load(f)

        # Fusion avec les valeurs par défaut
        config = DEFAULT_CONFIG.copy()
        config.update(user_config)

        # Validation des champs obligatoires
        validate_config(config)

        logger.info(f"Configuration chargée pour {len(config['teams'])} équipe(s)")
        return config

    except FileNotFoundError:
        logger.error("❌ Fichier config.json non trouvé !")
        logger.info("💡 Créez un fichier config.json avec vos équipes préférées.")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"❌ Erreur de syntaxe dans config.json : {e}")
        raise
    except ValueError as e:
        logger.error(f"❌ Erreur de validation dans config.json : {e}")
        raise

def validate_config(config):
    """Valide la configuration"""
    if not isinstance(config.get('teams'), list) or len(config['teams']) == 0:
        raise ValueError("Le champ 'teams' doit être une liste non vide")

    if not isinstance(config.get('match_durations'), dict):
        raise ValueError("Le champ 'match_durations' doit être un objet")

    if not isinstance(config.get('output_file'), str) or not config['output_file'].endswith('.ics'):
        raise ValueError("Le champ 'output_file' doit être un nom de fichier .ics valide")

    logger.info("✅ Configuration valide")

def get_pandascore_token():
    """Récupère le token PandaScore depuis l'environnement"""
    token = os.environ.get(PANDASCORE_TOKEN_ENV_VAR)
    if not token:
        raise RuntimeError(
            f"Variable d'environnement '{PANDASCORE_TOKEN_ENV_VAR}' manquante. "
            "Créez une clé API gratuite sur https://pandascore.co puis exportez-la "
            "(ou ajoutez-la comme secret GitHub Actions)."
        )
    return token

def pandascore_get(path, token, params=None):
    """Effectue un appel GET authentifié vers l'API PandaScore"""
    query = dict(params or {})
    query["token"] = token
    response = requests.get(f"{PANDASCORE_BASE_URL}{path}", params=query, timeout=15)
    response.raise_for_status()
    return response.json()

def search_team(team_name, token):
    """Recherche une équipe CS2 par son nom.

    L'API ne trie pas les résultats par pertinence (une recherche pour "3DMAX"
    peut renvoyer "3DMAX Academy" avant "3DMAX"), donc on préfère une
    correspondance exacte du nom ou de l'acronyme si elle existe.
    """
    results = pandascore_get("/teams", token, {"search[name]": team_name, "per_page": 10})
    if not results:
        return None

    needle = team_name.strip().casefold()
    for team in results:
        if team.get('name', '').strip().casefold() == needle:
            return team
    for team in results:
        if team.get('acronym', '').strip().casefold() == needle:
            return team
    return results[0]

def get_team_upcoming_matches(team_id, token, max_matches):
    """Récupère les matchs à venir d'une équipe"""
    return pandascore_get(
        "/matches/upcoming",
        token,
        {
            "filter[opponent_id]": team_id,
            "sort": "begin_at",
            "per_page": min(max_matches, 100),
        },
    )

def detect_match_format(match):
    """Détecte le format du match (BO1, BO3, BO5, BO7) à partir de number_of_games"""
    number_of_games = match.get('number_of_games')
    if number_of_games in (1, 3, 5, 7):
        return f"bo{number_of_games}"
    # Par défaut, assume BO1 pour les formats inconnus
    return 'bo1'

def extract_opponent_names(match):
    """Extrait les noms des deux équipes d'un match (TBD si non confirmées)"""
    names = []
    for entry in match.get('opponents') or []:
        opponent = (entry or {}).get('opponent') or {}
        names.append(opponent.get('name', 'TBD'))
    while len(names) < 2:
        names.append('TBD')
    return names[0], names[1]

def match_stream_url(match):
    """Retourne le premier lien de stream disponible pour le match, si existant"""
    for stream in match.get('streams_list') or []:
        if stream.get('raw_url'):
            return stream['raw_url']
    return None


def fetch_all_matches(config, token):
    """Récupère et fusionne les matchs à venir pour toutes les équipes suivies"""
    all_matches = []
    failed_teams = []
    seen_match_ids = set()

    for team_name in config['teams']:
        logger.info(f"🔍 Recherche de l'équipe '{team_name}'...")

        try:
            team = search_team(team_name, token)

            if not team:
                logger.warning(f"⚠️ Équipe '{team_name}' introuvable sur PandaScore")
                failed_teams.append(team_name)
                continue

            team_id = team['id']
            logger.info(f"✅ Équipe trouvée : {team['name']} (ID: {team_id})")

            matches = get_team_upcoming_matches(team_id, token, config.get('max_matches_per_team', 50))

            new_matches = 0
            for match in matches:
                if match['id'] in seen_match_ids:
                    continue
                seen_match_ids.add(match['id'])
                match['team_name'] = team_name
                all_matches.append(match)
                new_matches += 1

            logger.info(f"📅 {new_matches} match(s) trouvé(s) pour {team_name}")

        except requests.HTTPError as e:
            logger.error(f"❌ Erreur API PandaScore pour '{team_name}': {e}")
            failed_teams.append(team_name)
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des données pour '{team_name}': {e}")
            failed_teams.append(team_name)

    return all_matches, failed_teams


def generate_calendar():
    """Génère le calendrier des matchs CS2 pour les équipes configurées"""
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Impossible de charger la configuration: {e}")
        return False

    try:
        token = get_pandascore_token()
    except RuntimeError as e:
        logger.error(f"❌ {e}")
        return False

    logger.info("🎮 Démarrage de la génération du calendrier CS2...")

    try:
        all_matches, failed_teams = fetch_all_matches(config, token)

        # Si aucune équipe n'a pu être traitée
        if failed_teams and len(failed_teams) == len(config['teams']):
            logger.error("❌ Aucune équipe n'a pu être traitée. Vérifiez les noms d'équipes dans config.json")
            return False

        # Génération du calendrier
        if not all_matches:
            logger.info("📅 Aucun match à venir trouvé pour toutes les équipes.")
            return True

        cal = Calendar()
        cal.name = f"CS2 Teams Calendar ({len(config['teams'])} équipes)"
        cal.description = f"Calendrier automatique des matchs CS2 pour: {', '.join(config['teams'])}"

        events_created = 0
        for match in all_matches:
            try:
                event = create_calendar_event(match, config)
                if event:
                    cal.events.add(event)
                    events_created += 1
            except Exception as e:
                logger.warning(f"⚠️ Impossible de créer l'événement pour le match: {e}")
                continue

        # Sauvegarde du fichier
        output_file = config['output_file']
        with open(output_file, "w", encoding="utf-8") as f:
            f.writelines(cal)

        logger.info(f"✅ Calendrier généré: {output_file}")
        logger.info(f"📊 {events_created} événement(s) créé(s) pour {len(config['teams'])} équipe(s)")

        if failed_teams:
            logger.info(f"⚠️ Équipes échouées: {', '.join(failed_teams)}")

        return True

    except Exception as e:
        logger.error(f"❌ Erreur fatale lors de la génération: {e}")
        return False

def create_calendar_event(match, config):
    """Crée un événement calendrier à partir des données d'un match PandaScore"""
    try:
        event = Event()

        # Nom de l'événement
        team1_name, team2_name = extract_opponent_names(match)
        event.name = f"CS2: {team1_name} vs {team2_name}"

        # Début de l'événement
        start_date_str = match.get('scheduled_at') or match.get('begin_at')
        if not start_date_str:
            logger.warning("⚠️ Match sans date planifiée, ignoré")
            return None

        try:
            event.begin = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
        except ValueError:
            logger.warning(f"⚠️ Impossible de parser la date: {start_date_str}")
            return None

        # Durée du match
        match_format = detect_match_format(match)
        duration_hours = config['match_durations'].get(match_format, 1.5)
        event.duration = timedelta(hours=duration_hours)

        # Lien de stream si disponible
        stream_url = match_stream_url(match)
        if stream_url:
            event.url = stream_url

        # Description enrichie
        tournament_name = (match.get('tournament') or {}).get('name') \
            or (match.get('league') or {}).get('name') \
            or 'Tournament'
        team_name = match.get('team_name', 'Unknown')

        event.description = (
            f"🎮 Counter-Strike 2 Match\n"
            f"📋 Tournoi: {tournament_name}\n"
            f"⚔️ Format: {match_format.upper()}\n"
            f"⏱️ Durée estimée: {event.duration}\n"
            f"🔍 Équipe suivie: {team_name}\n"
        )

        if stream_url:
            event.description += f"📺 Stream: {stream_url}"

        # Catégorie et tags
        event.categories.add("CS2")
        event.categories.add("Esports")
        event.categories.add(match_format.upper())

        return event

    except Exception as e:
        logger.warning(f"❌ Impossible de créer l'événement: {e}")
        return None

def main():
    """Point d'entrée principal du programme"""
    print("🎮 CS2 Teams Calendar Generator v3.0")
    print("=" * 50)

    try:
        success = generate_calendar()

        if success:
            print("\n✅ Génération terminée avec succès !")
            sys.exit(0)
        else:
            print("\n❌ Erreur lors de la génération.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️ Génération interrompue par l'utilisateur.")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
