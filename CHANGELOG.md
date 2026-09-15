# Changelog

## Non publié

### Nettoyage

- suppression complète de l'interface desktop PySide6 et de ses tests UI ;
- suppression du point d'entrée desktop, des ressources QSS/ICO et des scripts de lancement associés ;
- suppression de l'installateur Inno Setup, du workflow Windows et des scripts PyInstaller/release legacy ;
- suppression des anciennes captures de l'interface desktop et de la documentation de parité desktop/web ;
- retrait des dépendances de développement PySide6, pytest-qt et PyInstaller ;
- documentation recentrée sur l'application web Docker ;
- conservation du backend Python/FastAPI et de la compatibilité des données historiques.

## 0.3.0 - 2026-09-15

Migration de Visual AI Studio vers une application web Docker à parité fonctionnelle avec la version desktop 0.2.1.

### Interface

- remplacement du frontend principal PySide6 par une interface React / Vite très graphique ;
- conservation des pages Projets, Brief, Studio Visuel, Validation, Export et Paramètres ;
- conservation des KPI, recherches, filtres, actions projet, galerie et validation humaine ;
- interface responsive avec direction visuelle sombre, verre, violet et cyan ;
- conservation du réglage de 1 à 10 visuels Instagram.

### Backend

- ajout d'une API FastAPI ;
- réutilisation des modèles, repositories, services, prompt builder, validateurs et SQLite existants ;
- conservation de l'autosauvegarde, des collections, du versionnement et des contrôles de livrables ;
- export web sous forme de ZIP contenant le même dossier `<slug>-v<version>`, les mêmes livrables et `project.json`.

### Docker

- ajout d'un Dockerfile multi-stage Node / Python ;
- ajout de Docker Compose ;
- volume persistant `/data` ;
- port hôte par défaut `3093` ;
- prise en charge de `host.docker.internal` pour joindre un service n8n exposé sur le poste hôte ;
- paramètres techniques disponibles par variables d'environnement sans les exposer dans l'UI.

### n8n

- aucune modification du contrat webhook ;
- `schema_version` reste `1.0` ;
- même `WebhookClient` et même `SubmissionService` ;
- même multipart `artifact_N` + `metadata` ;
- même `Idempotency-Key`, même authentification et mêmes structures de réponse.

### QA

- matrice de parité desktop / web dans `docs/web-functional-parity.md` ;
- tests API du parcours brief → prompt → import → validation → export ;
- tests du sélecteur de stockage Docker ;
- CI séparée backend, frontend et image Docker ;
- chaîne Windows automatique remplacée par un workflow legacy manuel.

## 0.2.1 - 2026-09-14

Version corrective de migration depuis IA-Art Studio.

### Corrections

- migration automatique de l'ancienne base `ia-art-studio.db` lorsque Visual AI Studio ne contient encore aucun projet ;
- sauvegarde de la base Visual AI Studio existante avant migration ;
- affichage des projets archivés dans le tableau et les indicateurs d'historique ;
- compatibilité de lecture des anciens types de livrables Pinterest, Instagram, synthèse et Notion ;
- ajout de boutons explicites `−` et `+` pour régler de 1 à 10 visuels dans un post ;
- suppression de l'ancien raccourci Bureau `IA-Art Studio` lors de l'installation, sans suppression des données historiques.

## 0.2.0 - 2026-09-14

### Fonctionnalités

- Instagram devient le canal de publication par défaut ;
- une publication Instagram peut demander de 1 à 10 visuels principaux cohérents ;
- le prompt Studio Visuel décrit explicitement les visuels comme une série destinée à un seul post ;
- Studio Visuel lit le nombre demandé et prépare exactement N prompts et N images ;
- le Skill IA-Art embarqué signe les N images et produit une synthèse unique, un Markdown Notion unique et une archive unique ;
- la fiche synthèse et le Markdown restent des livrables annexes séparés.

### Changements

- retrait du mode de publication historique remplacé par Instagram ;
- nettoyage de l'interface, des presets, des tests et de la documentation associés à l'ancien canal ;
- mise à jour du package Studio Visuel et du Skill IA-Art ;
- documentation produit alignée sur Instagram et le multi-images.

### Maintenance

- la chaîne de release lit désormais la version depuis `pyproject.toml` ;
- un tag Git différent de `v<version>` bloque la publication ;
- le packaging vérifie que la version et le nom de l'installateur Inno Setup restent alignés ;
- le workflow publie l'installateur avec un motif de fichier indépendant d'un numéro de version codé en dur ;
- les tests hérités ont été alignés sur la suppression de Pinterest.

## 0.1.1 - 2026-08-20

Version publique Windows stabilisée.

### Changements

- finalisation du packaging Windows avec PyInstaller et Inno Setup ;
- ajout de la chaîne CI / release GitHub avec artefacts et checksums ;
- distribution de `Visual-AI-Studio-Setup-0.1.1.exe` ;
- distribution du package `studio-visuel-agent.zip` ;
- ajout de l'infographie Visual AI Studio dans le README ;
- alignement de la documentation publique sur la version 0.1.1.

## 0.1.0 - 2026-08-19

Première version publique de Visual AI Studio.

### Inclus

- application Windows locale en Python / PySide6 ;
- création et suivi de projets visuels ;
- briefs pour réseaux sociaux et formats personnalisés ;
- préparation du prompt destiné à Studio Visuel ;
- import et contrôle des livrables ;
- galerie et validation humaine ;
- export local des fichiers ;
- stockage local SQLite ;
- package Studio Visuel séparé ;
- licence MIT.
