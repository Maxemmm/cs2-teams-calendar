#!/usr/bin/env python3
"""
🎮 CS2 Teams Calendar Generator
Génère automatiquement un fichier calendrier (.ics) pour suivre les matchs
de vos équipes Counter-Strike 2 préférées.

Auteur: CS2 Calendar Team
Version: 2.0.0
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta

from cs2api import CS2
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
    "base_url": "https://bo3.gg/matches/",
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

def detect_match_format(match):
    """Détecte le format du match (BO1, BO3, BO5, BO7)"""
    bo_type = match.get('bo_type', {})

    if bo_type == 7:
        return 'bo7'
    elif bo_type == 5:
        return 'bo5'
    elif bo_type == 3:
        return 'bo3'
    elif bo_type == 1:
        return 'bo1'
    else:
        # Par défaut, assume BO1 pour les matchs rapides
        return 'bo1'


async def generate_calendar():
    """Génère le calendrier des matchs CS2 pour les équipes configurées"""
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Impossible de charger la configuration: {e}")
        return False
    
    logger.info("🎮 Démarrage de la génération du calendrier CS2...")
    
    try:
        async with CS2() as cs2:
            all_matches = []
            failed_teams = []
            
            for team_name in config['teams']:
                logger.info(f"🔍 Recherche de l'équipe '{team_name}'...")
                
                try:
                    teams_data = await cs2.search_teams(team_name)
                    
                    if not teams_data or not teams_data.get('results'):
                        logger.warning(f"⚠️ Équipe '{team_name}' introuvable sur bo3.gg")
                        failed_teams.append(team_name)
                        continue
                    
                    team_info = teams_data['results'][0]
                    team_id = team_info['id']
                    logger.info(f"✅ Équipe trouvée : {team_info['name']} (ID: {team_id})")

                    # Récupération des matchs avec limite
                    matches_data = await cs2.get_team_upcoming_matches(team_id)
                    
                    if matches_data and matches_data.get('results'):
                        matches = matches_data['results'][:config.get('max_matches_per_team', 50)]
                        
                        # Ajouter des métadonnées au match
                        for match in matches:
                            match['team_name'] = team_name
                            match['source_team_id'] = team_id
                        
                        all_matches.extend(matches)
                        logger.info(f"📅 {len(matches)} match(s) trouvé(s) pour {team_name}")
                    else:
                        logger.info(f"📅 Aucun match à venir pour {team_name}")
                        
                except Exception as e:
                    logger.error(f"❌ Erreur lors de la récupération des données pour '{team_name}': {e}")
                    failed_teams.append(team_name)
                    continue

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
    """Crée un événement calendrier à partir des données d'un match"""
    try:
        event = Event()
        
        # Nom de l'événement
        team1_name = match.get('team1', {}).get('name', 'TBD')
        team2_name = match.get('team2', {}).get('name', 'TBD')
        event.name = f"CS2: {team1_name} vs {team2_name}"
        
        # Début de l'événement
        start_date_str = match.get('start_date')
        if not start_date_str:
            logger.warning("⚠️ Matches sans 'start_date', ignoré")
            return None
            
        try:
            event.begin = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
        except:
            logger.warning(f"⚠️ Impossible de parser la date: {start_date_str}")
            return None
        
        # Durée du match
        match_format = detect_match_format(match)
        duration_hours = config['match_durations'].get(match_format, 1.5)
        event.duration = timedelta(hours=duration_hours)
        
        # URL vers la page du match
        slug = match.get('slug')
        if slug:
            event.url = config['base_url'] + slug
        
        # Description enrichie
        tournament_name = match.get('tournament', {}).get('name', 'Tournament')
        team_name = match.get('team_name', 'Unknown')
        
        event.description = (
            f"🎮 Counter-Strike 2 Match\n"
            f"📋 Tournoi: {tournament_name}\n"
            f"⚔️ Format: {match_format.upper()}\n"
            f"⏱️ Durée estimée: {event.duration}\n"
            f"🔍 Équipe suivie: {team_name}\n"
        )
        
        if event.url:
            event.description += f"🔗 Lien: {event.url}"
        
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
    print("🎮 CS2 Teams Calendar Generator v2.0")
    print("=" * 50)
    
    try:
        success = asyncio.run(generate_calendar())
        
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