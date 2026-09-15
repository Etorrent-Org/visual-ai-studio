# Visual AI Studio - Spécification produit v0.3.0

## 1. Vision

Visual AI Studio est une application web locale distribuée avec Docker permettant de structurer un projet de création visuelle depuis le brief jusqu'à la validation et l'export des livrables.

La génération est réalisée avec un composant conversationnel séparé nommé **Studio Visuel**. Visual AI Studio n'effectue aucun appel direct à une API OpenAI et conserve une approche **local-first**.

## 2. Composants

### Visual AI Studio Web

L'application prend en charge la création et le suivi des projets, le brief, la préparation du prompt, l'import des résultats, le contrôle des fichiers, la galerie, la validation humaine, l'export local et l'envoi facultatif vers le webhook.

### Studio Visuel

Studio Visuel est l'agent conversationnel utilisé dans ChatGPT pour préparer la direction artistique, le storyboard et les visuels demandés.

### IA-Art

Le Skill IA-Art est responsable de la signature et du packaging des visuels Instagram. Pour Instagram, les livrables finaux sont des JPEG/JPG 1080 × 1350 accompagnés d'une synthèse PNG, d'un Markdown Notion et de l'archive éditoriale complète.

## 3. Workflow principal

1. créer ou ouvrir un projet ;
2. saisir le brief créatif ;
3. sélectionner le mode de sortie ;
4. définir de 1 à 10 visuels principaux ;
5. préparer le prompt destiné à Studio Visuel ;
6. copier le prompt dans Studio Visuel ;
7. suivre le workflow conversationnel ;
8. récupérer puis importer les fichiers produits ;
9. contrôler les résultats ;
10. valider humainement le résultat ;
11. exporter les livrables ou utiliser le webhook existant.

Le passage entre Visual AI Studio et Studio Visuel reste volontairement manuel.

## 4. Projets et historique

Trois statuts métier sont visibles : **Brief**, **Validé** et **Archivé**.

La page Projets propose :

- les quatre KPI ;
- la recherche par nom, collection ou style ;
- le filtre de statut ;
- la création ;
- l'ouverture ;
- la duplication ;
- l'archivage avec confirmation ;
- la présence des projets archivés dans l'historique.

## 5. Modes de sortie

### Instagram

Instagram est le mode par défaut : **1080 × 1350 px**, ratio **4:5**.

Une publication peut comporter **1 à 10 visuels principaux**, réglés avec les boutons `−` et `+`. Plusieurs visuels représentent une série cohérente destinée à un seul post.

### Autre / personnalisé

L'utilisateur peut définir les dimensions, le ratio, le style, les contraintes, le texte dans l'image et la destination prévue.

## 6. Brief créatif

Le brief comprend : nom, collection, style, idée, audience, nombre de visuels, texte, notes, dimensions, ratio, objectif, sujet, décor, ambiance, palette, lumière, matières, composition, détail, éléments obligatoires, éléments interdits, image et note de référence.

Sont également pris en charge :

- l'autosauvegarde ;
- la normalisation des collections ;
- la détection des valeurs proches ;
- la création explicite d'une nouvelle collection ;
- l'invalidation du prompt et l'incrément de version lorsqu'un brief déjà préparé est modifié.

## 7. Préparation Studio Visuel

Visual AI Studio utilise `prompt_builder.py` et `prompt-template.txt` pour produire le prompt de lancement.

La page fournit :

- le prompt intégral ;
- sa version ;
- son SHA-256 ;
- la copie dans le presse-papiers ;
- l'ouverture de Studio Visuel si une URL est configurée ;
- le mode d'emploi en cinq étapes ;
- le passage explicite vers l'import des résultats.

## 8. Import et validation

Formats pris en charge : PNG, JPG, JPEG, WebP, Markdown, TXT et JSON.

Les règles de validation couvrent :

- limite de taille par fichier ;
- image lisible ;
- largeur et hauteur attendues ;
- texte UTF-8 lisible et non vide ;
- JSON valide et de type objet ;
- SHA-256 ;
- au moins une image obligatoire ;
- manifeste facultatif ;
- fichier inconnu signalé sans blocage.

Les images sont présentées dans une galerie. La validation finale reste explicite et humaine : **Je valide ce résultat**.

## 9. Export local

Le service d'export crée le dossier `<slug>-v<version>` contenant tous les artefacts et `project.json`.

L'interface web transmet ce dossier sous forme d'archive ZIP, car un navigateur ne peut pas écrire arbitrairement dans le système de fichiers du poste client.

## 10. n8n / webhook

La compatibilité n8n est un invariant :

- `schema_version: 1.0` ;
- `source: visual-ai-studio` ;
- bloc `project` inchangé ;
- bloc `output` inchangé ;
- liste `artifacts` inchangée ;
- bloc `validation` inchangé ;
- multipart `artifact_0`, `artifact_1`, … + `metadata` ;
- `Idempotency-Key` identique ;
- header d'authentification identique ;
- réponses `success` et `duplicate` ;
- champs `execution_id`, `remote_url`, `message`, `retryable`, `duplicate_avoided` ;
- journalisation dans `automation_runs`.

Une URL utilisant `host.docker.internal` peut être nécessaire pour atteindre un n8n exposé sur le poste hôte. Cette différence est uniquement réseau.

## 11. Paramètres

L'interface expose uniquement le dossier des projets.

Le dossier sélectionnable reste volontairement à l'intérieur du volume Docker monté sous `/data`. Les paramètres techniques restent hors de l'UI et peuvent être fournis par variables d'environnement Docker.

## 12. Données et historique

SQLite est utilisé pour les projets et l'historique.

La compatibilité de lecture des données et types de livrables existants est conservée afin de ne pas perdre l'historique utilisateur.

Un dossier hôte contenant `visual-ai-studio.db` et `projects` peut être monté dans `/data` pour reprendre les données existantes.

## 13. Architecture technique

- Python 3.12 ;
- FastAPI / Uvicorn ;
- React 19 ;
- Vite ;
- Motion ;
- Pydantic ;
- SQLAlchemy ;
- SQLite ;
- Pillow ;
- Docker / Docker Compose.

Le frontend React ne duplique pas la logique métier Python.

## 14. Distribution

La distribution est exclusivement web/Docker. Le `Dockerfile` construit le frontend puis le backend dans une image unique. Docker Compose expose par défaut l'interface sur le port hôte 3093 et monte `/data` en volume persistant.

Le dépôt ne contient plus d'interface PySide6 ni de chaîne de build Windows.

## 15. Hors périmètre v0.3.0

La version 0.3.0 n'ajoute pas :

- d'authentification utilisateur ;
- de fonctionnement multi-utilisateur ;
- de SaaS ;
- de publication Instagram directe ;
- d'appel API OpenAI ;
- de marketplace ;
- de nouveau mode de création ;
- de nouvelle intégration métier.

## 16. Licence et état

Visual AI Studio, sa documentation et le package Studio Visuel sont distribués sous licence MIT.

Version web : **0.3.0**.
