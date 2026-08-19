# Visual AI Studio - Spécification produit v0.1.0

## 1. Vision

Visual AI Studio est une application Windows locale permettant de structurer
un projet de création visuelle depuis le brief jusqu'à la validation et
l'export des livrables.

La génération est réalisée avec un composant conversationnel séparé nommé
**Studio Visuel**.

Visual AI Studio n'effectue aucun appel direct à une API OpenAI.

Le produit suit une approche **local-first** et reste utilisable sans service
cloud, sans Docker et sans automatisation externe.

## 2. Composants

### Visual AI Studio

L'application Windows prend en charge :

- la création des projets ;
- la saisie du brief ;
- la préparation du prompt de lancement ;
- l'import des résultats ;
- le contrôle des fichiers ;
- la galerie d'images ;
- la validation humaine ;
- l'export local ;
- l'envoi facultatif vers un webhook.

### Studio Visuel

Studio Visuel est l'agent conversationnel utilisé dans ChatGPT.

Il prend en charge :

- la reformulation du brief ;
- la direction artistique ;
- la préparation du prompt image ;
- les contraintes négatives ;
- les contenus de publication ;
- la génération visuelle ;
- la livraison des résultats.

Le Skill `visual-content-studio` constitue la source de vérité fonctionnelle
de Studio Visuel.

## 3. Workflow principal

1. créer ou ouvrir un projet ;
2. saisir le brief créatif ;
3. sélectionner le mode de sortie ;
4. préparer le prompt destiné à Studio Visuel ;
5. copier le prompt ;
6. ouvrir Studio Visuel dans ChatGPT ;
7. suivre le workflow conversationnel ;
8. récupérer les fichiers produits ;
9. importer les fichiers dans Visual AI Studio ;
10. contrôler les résultats ;
11. valider humainement le résultat ;
12. exporter les livrables.

Le passage entre Visual AI Studio et Studio Visuel reste volontairement
manuel.

## 4. Modes de sortie

Trois modes sont disponibles.

### Pinterest

Le brief peut être orienté vers une création destinée à Pinterest.

Studio Visuel adapte alors sa proposition au contexte de publication.

### Instagram

Le brief peut être orienté vers une création destinée à Instagram.

Studio Visuel adapte alors sa proposition au contexte de publication.

### Autre / personnalisé

L'utilisateur peut définir librement :

- les dimensions ;
- le ratio ;
- le style ;
- les contraintes ;
- le texte dans l'image ;
- la destination ou l'usage prévu.

## 5. Statuts des projets

Visual AI Studio utilise trois statuts métier visibles :

- **Brief**
- **Validé**
- **Archivé**

Aucun statut technique n'est exposé à l'utilisateur.

## 6. Brief créatif

Le brief peut notamment contenir :

- le nom du projet ;
- la collection ou campagne ;
- l'idée ou la demande ;
- l'audience ;
- le style ;
- le texte souhaité dans l'image ;
- les dimensions ;
- le ratio ;
- des notes ;
- des éléments obligatoires ;
- des éléments interdits ;
- des indications de direction créative.

Le brief reste modifiable tant que le projet est en préparation.

## 7. Préparation Studio Visuel

Visual AI Studio génère un **prompt de lancement**.

Ce prompt :

- transmet le contexte du projet ;
- indique le mode de sortie ;
- reprend les informations utiles du brief ;
- demande à Studio Visuel d'utiliser son Skill ;
- demande de commencer par la reformulation du brief ;
- impose une validation utilisateur avant la poursuite du workflow.

Visual AI Studio ne duplique pas dans l'application la logique créative du
Skill Studio Visuel.

## 8. Import et validation

Les fichiers pris en charge comprennent notamment :

### Images

- PNG
- JPG
- JPEG
- WebP

### Fichiers complémentaires

- Markdown
- TXT
- JSON

Plusieurs images peuvent être importées pour un même projet.

Les images sont présentées dans une galerie de validation.

Les contrôles automatiques peuvent produire des avertissements ou des erreurs.

La validation finale est explicite et humaine :

**Je valide ce résultat**

## 9. Export

Un projet validé peut être exporté localement.

L'export crée un dossier dédié contenant les fichiers du projet et ses
informations utiles.

Un envoi vers un webhook peut également être utilisé lorsqu'une configuration
technique correspondante existe.

Le webhook n'est pas nécessaire au fonctionnement standard de l'application.

## 10. Stockage local

Les projets et fichiers de travail sont conservés localement.

L'utilisateur peut choisir le dossier de stockage depuis les paramètres de
Visual AI Studio.

Les paramètres visibles restent volontairement réduits afin de privilégier
l'usage métier.

## 11. Hors périmètre v0.1.0

La version 0.1.0 ne fournit pas directement :

- d'authentification Pinterest ;
- d'authentification Instagram ;
- de publication automatique vers un réseau social ;
- d'appel direct à une API OpenAI ;
- d'hébergement cloud ;
- de fonctionnement multi-utilisateur ;
- d'abonnement SaaS ;
- de marketplace.

## 12. Architecture technique

Visual AI Studio repose notamment sur :

- Python 3.11+
- PySide6
- Pydantic
- SQLAlchemy
- SQLite
- Pillow
- platformdirs
- keyring
- PyInstaller
- Inno Setup

## 13. Distribution Windows

Visual AI Studio est distribué sous forme d'application Windows autonome.

L'installateur de la version 0.1.0 est :

`Visual-AI-Studio-Setup-0.1.0.exe`

L'utilisateur final n'a pas besoin d'installer :

- Python ;
- Git ;
- Docker.

Le package Studio Visuel est distribué séparément dans la même GitHub Release.

## 14. Licence

Visual AI Studio, sa documentation et le package Studio Visuel sont distribués
sous licence MIT.

## 15. État

Version produit : **0.1.0**

La version 0.1.0 constitue la première distribution publique Windows de
Visual AI Studio.