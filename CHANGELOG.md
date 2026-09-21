# 🎮 Changelog - CS2 Teams Calendar

## [Version 3.2.0] - 2026-09-21

### ⏰ Fréquence de mise à jour
- **Passage à une exécution horaire** (au lieu de 2x/jour) pour mieux suivre les décalages fréquents d'horaires de matchs
- Largement sous les limites de l'API PandaScore (1000 requêtes/heure) et gratuit sur GitHub Actions pour un repo public
- Cron mis à jour dans le workflow GitHub Actions et dans le service cron du `docker-compose.yml`

## [Version 3.1.0] - 2026-09-21

### 🧹 Nettoyage du script
- Suppression de tous les emojis du script (logs, docstrings, description des événements générés) pour un style plus sobre et professionnel
- Ajout d'une `requests.Session()` partagée pour réutiliser les connexions HTTP entre les appels à l'API PandaScore
- `main()` utilise désormais le logger au lieu de `print()`, cohérent avec le reste du script

## [Version 3.0.0] - 2026-09-21

### 🔄 Migration de source de données
- **Remplacement de bo3.gg par l'API officielle PandaScore** : bo3.gg a mis en place une protection anti-bot qui renvoie désormais des erreurs 403 Forbidden sur les requêtes automatisées, rendant le scraping non-officiel (`cs2api`) inutilisable
- **Nouvelle dépendance** : appels HTTP directs via `requests` vers `api.pandascore.co` (authentification par token, tier gratuit)
- **Suppression de `cs2api`** et de la dépendance `python-dateutil` (non utilisée)
- **Script simplifié** : suppression de l'usage d'`asyncio`, devenu inutile avec des appels HTTP synchrones
- **Détection du format de match fiabilisée** : basée directement sur le champ `number_of_games` de PandaScore
- **Déduplication des matchs** : un même match entre deux équipes suivies n'apparaît plus qu'une seule fois
- **Lien de stream** dans les événements calendrier quand PandaScore en fournit un (remplace le lien bo3.gg)

### 📋 Changements Breaking
- Nécessite désormais une clé API PandaScore gratuite, fournie via la variable d'environnement `PANDASCORE_TOKEN` (secret GitHub Actions en CI)
- Suppression du champ `base_url` dans `config.json` (n'est plus utilisé)

## [Version 2.0.0] - 2024-01-XX

### ✨ Nouvelles Fonctionnalités
- **Mises à jour automatiques 2x par jour** (00h et 12h UTC)
- **Validation avancée de configuration** avec messages d'erreur explicites
- **Gestion robuste des erreurs** avec fallback gracieux
- **Limitation du nombre de matchs** par équipe (configurable)
- **Logging professionnel** avec emojis et niveaux adaptés
- **Métadonnées enrichies** dans les événements calendrier
- **Support de configuration avancée** avec valeurs par défaut

### 🔧 Améliorations Techniques
- **Workflow GitHub Actions optimisé** avec validation avant exécution
- **Script Python refactorisé** avec gestion d'erreurs avancée
- **Dépendances fixes** avec versions minimum garanties
- **Cache pip** dans les workflows pour des builds plus rapides
- **Timeout configuré** pour éviter les hangs
- **Commits plus sensés** avec emojis et timestamps

### 🐛 Corrections
- **Suppression du workflow dupliqué** generate.yml
- **Validation de configuration** avant traitement
- **Gestion des équipes introuvables** sans faire échouer le processus
- **Dates malformées** gérées proprement
- **Messages d'erreur** en français pour cohérence

### 📋 Changements Breaking
- Nouvelle structure de `config.json` avec options additionnelles
- Migration automatique des configurations existantes
- Changement des horaires par défaut des mises à jour (00h et 12h au lieu de 05h)

## [Version 1.x.x] - Historique précédent
Initial import des fonctionnalités de base.
