# IA Art Studio Pro — installation self-hosted

## Prérequis

- Docker Engine / Docker Desktop récent ;
- Docker Compose ;
- un dossier persistant pour les données ;
- n8n et Notion uniquement si l’automatisation est utilisée.

## Installation

```sh
cp .env.pro.example .env.pro
docker compose --env-file .env.pro -f docker-compose.pro.yml up -d --build
```

Ouvrir ensuite `http://localhost:3093` ou le port choisi.

## Données

Toutes les données applicatives persistantes sont dans le dossier défini par :

`IA_ART_PRO_DATA_DIR`

Il contient notamment SQLite et les fichiers projets.

## Sauvegarde manuelle

```sh
docker compose --env-file .env.pro -f docker-compose.pro.yml --profile backup run --rm backup
```

Les archives sont écrites dans `IA_ART_PRO_BACKUP_DIR` et conservées 14 jours par défaut.

## n8n / Notion

1. Importer le workflow depuis `n8n/marketplace/`.
2. Reconnecter Header Auth et Notion.
3. Remplacer le placeholder de source Notion.
4. Activer le workflow.
5. Dans IA Art Studio Pro, ouvrir Administration et enregistrer l’URL du webhook et son secret.
6. Tester la connexion depuis l’application.

## Sécurité

- ne jamais committer le fichier `.env.pro` ;
- utiliser un secret de webhook unique et long ;
- ne pas exposer directement le port de l’application à Internet sans reverse proxy HTTPS si l’instance contient des données personnelles ;
- conserver les sauvegardes hors du dossier de données principal.

## Limite actuelle

IA Art Studio Pro reste une application **mono-utilisateur / mono-instance**. Cette édition n’est pas un SaaS multi-tenant.
