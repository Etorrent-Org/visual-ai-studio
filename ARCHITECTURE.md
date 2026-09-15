# Architecture

## Baseline

Visual AI Studio **0.3.0** est une application web locale distribuée avec Docker.

- interface : React / Vite / Motion ;
- API : FastAPI ;
- logique métier : Python ;
- données : SQLite ;
- fichiers : volume Docker local ;
- agent créatif : Studio Visuel dans ChatGPT ;
- intégration externe : webhook n8n facultatif, contrat 1.0.

## Vue simple

```mermaid
flowchart LR
    U[Navigateur] --> R[React / Vite]
    R --> API[FastAPI]
    API --> APP[Services applicatifs Python]
    APP --> DOM[Logique métier]
    APP --> DB[(SQLite /data)]
    APP --> FS[Fichiers /data/projects]
    R --> P[Prompt de lancement]
    P -. copie manuelle .-> SV[Studio Visuel dans ChatGPT]
    SV -. livrables manuels .-> R
    APP -. contrat 1.0 .-> N8N[n8n Webhook]
```

Visual AI Studio ne réalise aucun appel direct à une API OpenAI. Le passage vers Studio Visuel et le retour des livrables restent manuels.

## Frontend

Le dossier `web` contient l'interface React :

- tableau de bord projets ;
- brief créatif ;
- préparation Studio Visuel ;
- import / validation et galerie ;
- export / webhook ;
- paramètres de stockage.

Le frontend ne duplique pas la logique métier : il appelle l'API FastAPI.

## Backend

`src/visual_ai_studio/web_app.py` expose les routes nécessaires au frontend et délègue à :

- `domain` pour les modèles et règles ;
- `services` pour les cas d'usage, les artefacts, l'export et la soumission ;
- `infrastructure` pour SQLite, les paramètres, le webhook et les journaux d'automatisation ;
- `application.py` pour construire le contexte applicatif partagé.

Le backend sert également le bundle frontend compilé en production.

## Stockage

Le conteneur utilise `/data` comme volume persistant :

```text
/data/
  visual-ai-studio.db
  settings.json
  projects/
```

Le dossier hôte est défini par `VISUAL_AI_HOST_DATA_DIR` dans Docker Compose.

La compatibilité de lecture des données existantes est conservée afin de ne pas perdre l'historique utilisateur.

## n8n

Le chemin réseau peut changer dans Docker, mais pas le contrat applicatif :

- `schema_version = 1.0` ;
- multipart `artifact_0...artifact_N` + `metadata` ;
- même `Idempotency-Key` ;
- même header d'authentification ;
- mêmes structures de métadonnées et de réponse.

Sur Docker Desktop, un n8n accessible sur la machine hôte peut être joint via `host.docker.internal`.

## Docker

Le `Dockerfile` est multi-stage :

1. Node 22 compile React/Vite ;
2. Python 3.12 installe le backend FastAPI ;
3. le bundle frontend est copié dans `/app/web-dist` ;
4. Uvicorn sert l'API et la SPA sur le port 8000.

`docker-compose.yml` expose par défaut le port hôte `3093` et monte le volume persistant dans `/data`.

## Organisation

- `web` : interface React ;
- `src/visual_ai_studio/web_app.py` : API web ;
- `src/visual_ai_studio/domain` : règles métier ;
- `src/visual_ai_studio/services` : cas d'usage ;
- `src/visual_ai_studio/infrastructure` : persistance et intégrations ;
- `src/visual_ai_studio/resources` : ressources partagées du backend ;
- `agent` : package Studio Visuel et Skill IA-Art ;
- `Dockerfile` / `docker-compose.yml` : distribution ;
- `.github/workflows/web-docker.yml` : CI web et Docker.

L'ancienne interface desktop PySide6 et la chaîne de build Windows ont été retirées du dépôt.

## Distribution

La distribution du projet est exclusivement web/Docker. Le dépôt ne produit plus d'installateur Windows.
