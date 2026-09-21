> **Distribution actuelle : web/Docker 0.3.0 depuis les sources.** Les releases Windows 0.2.1 et antérieures sont historiques. La release nommée `v1.0.0` contient l’ancien installateur 0.1.1 et ne correspond pas à la version web.

<p align="center">
  <img src="docs/images/visual-ai-studio-icon.png" width="120" alt="Visual AI Studio">
</p>

<h1 align="center">Visual AI Studio</h1>

<p align="center">
  Studio web Docker pour structurer un brief, travailler avec Studio Visuel,
  contrôler les créations et exporter les livrables.
</p>

---

## À quoi sert Visual AI Studio ?

Visual AI Studio accompagne un projet visuel du brief jusqu'à l'export final, avec Instagram comme canal de publication principal.

Le workflow reste volontairement simple :

1. préparer le brief dans Visual AI Studio ;
2. choisir de 1 à 10 visuels principaux pour la publication ;
3. générer le prompt de lancement ;
4. copier ce prompt dans Studio Visuel ;
5. laisser Studio Visuel préparer puis générer exactement le nombre de visuels demandé ;
6. laisser le Skill IA-Art signer les images et préparer les livrables ;
7. importer les fichiers générés ;
8. contrôler et valider le résultat ;
9. exporter localement ou transmettre le paquet au webhook n8n existant.

Visual AI Studio ne réalise **aucun appel direct à une API OpenAI** et ne nécessite aucune clé API OpenAI.

---

## Stack web Docker

- **Frontend** : React, Vite, Motion ;
- **Backend** : FastAPI / Python ;
- **Données** : SQLite et fichiers locaux ;
- **Déploiement** : Docker / Docker Compose ;
- **Stockage persistant** : volume `/data` ;
- **Port hôte par défaut** : `3093`.

Le dépôt ne contient plus l'ancienne application desktop PySide6 ni sa chaîne Windows.

---

## Fonctionnalités

### Projets

- liste des projets ;
- KPI **Projets / Brief / Validé / Archivé** ;
- recherche par nom, collection ou style ;
- filtre de statut ;
- création, ouverture, duplication et archivage ;
- historique des projets archivés.

### Brief créatif

Le seul mode de sortie est **Instagram Feed**, en 1080 × 1350 avec un ratio 4:5.

Pour Instagram, un post peut contenir **1 à 10 visuels principaux cohérents**.

Le brief prend en charge le projet, la collection, le style, l'idée, l'audience, le texte, les notes, la direction créative avancée et l'image de référence. Le format est fixe pour éviter les sorties incompatibles avec IA-Art.

L'autosauvegarde, la détection de collections proches, l'invalidation du prompt après modification du brief et le versionnement sont intégrés.

### Studio Visuel et IA-Art

Visual AI Studio prépare le prompt de lancement destiné à Studio Visuel. Studio Visuel et le Skill IA-Art restent séparés de l'application.

Le package est disponible dans :

`agent/studio-visuel-agent.zip`

Il contient l'agent Studio Visuel et le Skill IA-Art **5.0.2** alignés sur le contrat Instagram.

Pour Instagram, IA-Art livre les visuels finaux en **JPEG/JPG 1080 × 1350**, avec une synthèse PNG, un Markdown Notion et l'archive complète.

### Import et validation

Formats pris en charge : PNG, JPG/JPEG, WebP, Markdown, TXT et JSON.

Pour l'import Notion de la version web Instagram, le workflow n8n dédié est disponible dans [`n8n/IA-Art-01-Import-Notion-Instagram.json`](n8n/IA-Art-01-Import-Notion-Instagram.json). Les flux aval démarrent depuis Notion ; ils ne sont pas appelés directement par Visual AI Studio.

Les contrôles couvrent la lisibilité, les dimensions, l'UTF-8, le JSON, le SHA-256, la présence d'au moins une image et le manifeste facultatif. Les images sont présentées dans une galerie et la validation finale reste humaine : **Je valide ce résultat**.

### Export

Un projet validé peut :

- être téléchargé sous forme d'une archive contenant le dossier `<slug>-v<version>`, tous les livrables et `project.json` ;
- être transmis au webhook n8n existant.

---

## Compatibilité n8n

Le contrat n8n reste **strictement inchangé** :

- `schema_version: 1.0` ;
- `source: visual-ai-studio` ;
- même structure `project`, `output`, `artifacts`, `validation` ;
- même multipart `artifact_0`, `artifact_1`, … + `metadata` ;
- même `Idempotency-Key` ;
- même header d'authentification ;
- mêmes réponses `success` et `duplicate` ;
- mêmes champs `execution_id`, `remote_url`, `message`, `retryable` et `duplicate_avoided`.

Si n8n tourne sur le poste hôte et Visual AI Studio dans Docker Desktop, l'URL du webhook peut utiliser `host.docker.internal` à la place de `127.0.0.1` / `localhost`. Seule l'adresse réseau change ; le flux n8n ne change pas.

---

## Installation Docker

Créer un fichier `.env` à partir de `.env.example`, puis :

```powershell
docker compose up -d --build
```

Ouvrir ensuite :

```text
http://localhost:3093
```

Le dossier hôte défini par `VISUAL_AI_HOST_DATA_DIR` est monté dans `/data` et contient la base SQLite ainsi que les projets.

Pour reprendre un historique existant, ce dossier peut pointer vers un répertoire contenant `visual-ai-studio.db` et le dossier `projects`.

---

## Variables Docker

Les principaux réglages sont disponibles dans `.env.example` :

- `VISUAL_AI_PORT` ;
- `VISUAL_AI_HOST_DATA_DIR` ;
- `VISUAL_AI_WEBHOOK_URL` ;
- `VISUAL_AI_WEBHOOK_SECRET` ;
- `VISUAL_AI_AUTH_HEADER` ;
- `VISUAL_AI_TIMEOUT_SECONDS` ;
- `VISUAL_AI_MAX_FILE_SIZE_MB` ;
- `VISUAL_AI_AGENT_URL`.

La configuration n8n se fait depuis l’écran **Administration** de l’application : URL du webhook, nom du header, secret, délai et test de connexion. Les valeurs sont conservées dans le volume Docker ; le fichier `.env` n’est pas nécessaire pour les modifier.

Les variables n8n du `.env` restent disponibles comme valeurs de démarrage pour une installation automatisée, mais une configuration enregistrée depuis l’interface est prioritaire.

---

## Développement

### Backend

```bash
python -m venv .venv
.venv/bin/python -m pip install -e ".[web,web-dev]"
VISUAL_AI_DATA_DIR=./data .venv/bin/python -m pytest -q tests/unit tests/integration
VISUAL_AI_DATA_DIR=./data .venv/bin/uvicorn visual_ai_studio.web_app:app --reload
```

Sous PowerShell, définir d'abord `$env:VISUAL_AI_DATA_DIR = ".\data"`.

### Frontend

```bash
cd web
npm install
npm run dev
```

Le serveur Vite redirige `/api` vers le backend local sur le port 8000.

---

## Sécurité et confidentialité

Les données restent dans le volume Docker local, sauf envoi volontaire vers le webhook configuré. Visual AI Studio ne nécessite aucune clé API OpenAI.

Consultez [`SECURITY.md`](SECURITY.md) pour les règles de sécurité.

---

## Licence

Visual AI Studio est distribué sous **licence MIT**. Consultez [`LICENSE`](LICENSE).

---

## Version

Version web : **0.3.0**.
