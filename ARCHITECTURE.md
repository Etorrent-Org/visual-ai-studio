# Architecture

## Baseline

Visual AI Studio **0.3.0** est une application web locale distribuée avec Docker.

- Interface : React / Vite / Motion ;
- API : FastAPI ;
- logique métier : Python existant ;
- données : SQLite ;
- fichiers : volume Docker local ;
- agent créatif : Studio Visuel dans ChatGPT ;
- intégration externe : webhook n8n facultatif et compatible avec le contrat 1.0 existant.

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
    APP -. contrat 1.0 inchangé .-> N8N[n8n Webhook]
```

Visual AI Studio ne réalise aucun appel direct à une API OpenAI. Le passage vers Studio Visuel et le retour des livrables restent manuels.

## Principe de migration

La version web conserve les modèles, repositories, services et validateurs Python existants. L'interface PySide6 n'est plus le frontend principal mais reste dans le dépôt pour préserver l'historique et permettre un build desktop legacy manuel.

La parité fonctionnelle est figée dans [`docs/web-functional-parity.md`](docs/web-functional-parity.md).

## Frontend

Le dossier `web` contient l'interface React :

- tableau de bord projets ;
- brief créatif ;
- préparation Studio Visuel ;
- import / validation et galerie ;
- export / webhook ;
- paramètres de stockage.

Le frontend ne contient pas de logique métier parallèle : il appelle l'API FastAPI, qui réutilise les services Python existants.

## Backend

`src/visual_ai_studio/web_app.py` expose les routes nécessaires au frontend et délègue à :

- `domain` pour les modèles et règles ;
- `services` pour le prompt, les artefacts, l'export et la soumission ;
- `infrastructure` pour SQLite, les paramètres, le webhook et les journaux d'automatisation.

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

## n8n

Le chemin réseau peut changer dans Docker, mais pas le contrat applicatif.

Le backend appelle le même `WebhookClient` et le même `SubmissionService` que le desktop :

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
- `src/visual_ai_studio/ui` : frontend desktop legacy ;
- `src/visual_ai_studio/resources` : ressources partagées ;
- `agent` : package Studio Visuel ;
- `Dockerfile` / `docker-compose.yml` : distribution principale ;
- `.github/workflows/web-docker.yml` : CI web ;
- `.github/workflows/release-windows.yml` : build Windows legacy manuel.

## Distribution

La distribution principale est l'image Docker construite depuis le dépôt. La version Windows 0.2.1 reste disponible comme version historique, mais n'est plus publiée automatiquement.
