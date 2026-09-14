# Visual AI Studio - Spécification produit v0.2.0

## 1. Vision

Visual AI Studio est une application Windows locale permettant de structurer un projet de création visuelle depuis le brief jusqu'à la validation et l'export des livrables.

La génération est réalisée avec un composant conversationnel séparé nommé **Studio Visuel**. Visual AI Studio n'effectue aucun appel direct à une API OpenAI et suit une approche **local-first**.

## 2. Composants

### Visual AI Studio

L'application prend en charge la création des projets, la saisie du brief, la préparation du prompt de lancement, l'import des résultats, le contrôle des fichiers, la galerie d'images, la validation humaine, l'export local et l'envoi facultatif vers un webhook.

### Studio Visuel

Studio Visuel est l'agent conversationnel utilisé dans ChatGPT. Il prend en charge la reformulation du brief, la direction artistique, la préparation du prompt image, les contraintes négatives, les contenus de publication, la génération visuelle et la livraison des résultats.

Le Skill `visual-content-studio` constitue la source de vérité fonctionnelle de Studio Visuel.

## 3. Workflow principal

1. créer ou ouvrir un projet ;
2. saisir le brief créatif ;
3. sélectionner le mode de sortie ;
4. définir de 1 à 10 visuels principaux pour la publication ;
5. préparer le prompt destiné à Studio Visuel ;
6. copier le prompt dans Studio Visuel ;
7. suivre le workflow conversationnel ;
8. récupérer puis importer les fichiers produits ;
9. contrôler les résultats ;
10. valider humainement le résultat ;
11. exporter les livrables.

Le passage entre Visual AI Studio et Studio Visuel reste volontairement manuel.

## 4. Modes de sortie

Deux modes sont disponibles.

### Instagram

Instagram est le mode de publication par défaut. Le format standard est **1080 × 1350 px**, ratio **4:5**.

Une publication peut comporter **1 à 10 visuels principaux**. Lorsque plusieurs visuels sont demandés, Studio Visuel doit les concevoir comme une série cohérente destinée à un seul post, et non comme des variantes indépendantes.

### Autre / personnalisé

L'utilisateur peut définir librement les dimensions, le ratio, le style, les contraintes, le texte dans l'image et la destination prévue.

## 5. Livrables

Les visuels principaux destinés au post sont distincts des livrables annexes.

La **fiche synthèse** et le **Markdown IA-Art** restent des livrables séparés et leur structure n'est pas modifiée par la fonctionnalité multi-images.

## 6. Statuts des projets

Visual AI Studio utilise trois statuts métier visibles : **Brief**, **Validé** et **Archivé**. Aucun statut technique n'est exposé à l'utilisateur.

## 7. Brief créatif

Le brief peut notamment contenir le nom du projet, la collection ou campagne, l'idée, l'audience, le style, le nombre de visuels principaux, le texte souhaité dans l'image, les dimensions, le ratio, des notes et les indications de direction créative.

Le brief reste modifiable tant que le projet est en préparation.

## 8. Préparation Studio Visuel

Visual AI Studio génère un **prompt de lancement** qui transmet le contexte du projet, le mode de sortie, le nombre de visuels principaux et les informations utiles du brief.

Pour une publication multi-images, le prompt demande explicitement une narration visuelle cohérente entre les images d'un même post.

Visual AI Studio ne duplique pas dans l'application la logique créative du Skill Studio Visuel.

## 9. Import et validation

Les fichiers pris en charge comprennent notamment PNG, JPG, JPEG, WebP, Markdown, TXT et JSON.

Plusieurs images peuvent être importées pour un même projet et sont présentées dans une galerie de validation. La validation finale est explicite et humaine : **Je valide ce résultat**.

## 10. Export et webhook

Un projet validé peut être exporté localement. Un envoi vers un webhook peut également être utilisé lorsqu'une configuration technique correspondante existe. Le webhook n'est pas nécessaire au fonctionnement standard de l'application.

## 11. Stockage local

Les projets et fichiers de travail sont conservés localement. L'utilisateur peut choisir le dossier de stockage depuis les paramètres de Visual AI Studio.

## 12. Hors périmètre v0.2.0

La version 0.2.0 ne fournit pas directement d'authentification Instagram, de publication automatique vers un réseau social, d'appel direct à une API OpenAI, d'hébergement cloud, de fonctionnement multi-utilisateur, d'abonnement SaaS ou de marketplace.

## 13. Architecture technique

Visual AI Studio repose notamment sur Python 3.11+, PySide6, Pydantic, SQLAlchemy, SQLite, Pillow, platformdirs, keyring, PyInstaller et Inno Setup.

## 14. Distribution Windows

Visual AI Studio est distribué sous forme d'application Windows autonome. L'utilisateur final n'a pas besoin d'installer Python, Git ou Docker. Le package Studio Visuel est distribué séparément dans la même GitHub Release.

## 15. Licence et état

Visual AI Studio, sa documentation et le package Studio Visuel sont distribués sous licence MIT.

Version produit publique actuelle : **0.2.0**.
