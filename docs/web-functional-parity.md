# Visual AI Studio Web — matrice de parité fonctionnelle

Cette matrice est la règle de migration de la version desktop 0.2.1 vers la version web Docker 0.3.0.

**Principe : aucune fonction métier n'est ajoutée et aucune fonction métier n'est supprimée.** Seule l'interface et l'architecture d'exécution changent.

## 1. Projets

| Fonction 0.2.1 | Web Docker 0.3.0 |
| --- | --- |
| Liste des projets | Conservée |
| Projets archivés visibles dans l'historique | Conservé |
| KPI Projets / Brief / Validé / Archivé | Conservés |
| Recherche par nom, collection ou style | Conservée |
| Filtre par statut | Conservé |
| Nouveau projet | Conservé |
| Ouvrir | Conservé |
| Dupliquer | Conservé |
| Archiver avec confirmation | Conservé |
| Statuts visibles Brief / Validé / Archivé | Conservés |

## 2. Brief créatif

| Fonction 0.2.1 | Web Docker 0.3.0 |
| --- | --- |
| Instagram par défaut | Conservé |
| Autre / personnalisé | Conservé |
| Instagram 1080 × 1350, ratio 4:5 | Conservé |
| Nombre de visuels 1 à 10 | Conservé |
| Boutons − / + | Conservés |
| Nom du projet | Conservé |
| Collection / campagne | Conservée |
| Détection des collections proches avant création | Conservée |
| Style | Conservé |
| Idée / demande | Conservée |
| Audience | Conservée |
| Texte dans l'image | Conservé |
| Notes | Conservées |
| Largeur / hauteur / ratio personnalisés | Conservés |
| Objectif | Conservé |
| Sujet principal | Conservé |
| Décor | Conservé |
| Ambiance | Conservée |
| Palette | Conservée |
| Lumière | Conservée |
| Matières | Conservées |
| Composition | Conservée |
| Niveau de détail | Conservé |
| Éléments obligatoires | Conservés |
| Éléments interdits | Conservés |
| Note de référence | Conservée |
| Image de référence | Conservée via upload navigateur |
| Autosauvegarde | Conservée, délai 800 ms |
| Enregistrer le brouillon | Conservé |
| Invalidation du prompt si le brief change | Conservée |
| Préparer pour Studio Visuel | Conservé |

## 3. Studio Visuel

| Fonction 0.2.1 | Web Docker 0.3.0 |
| --- | --- |
| Prompt généré par le code Python existant | Inchangé |
| Version du prompt | Conservée |
| SHA-256 du prompt | Conservé |
| Aperçu intégral du prompt | Conservé |
| Copier le prompt | Conservé |
| Ouvrir Studio Visuel si URL configurée | Conservé |
| Mode d'emploi en 5 étapes | Conservé |
| Résultat prêt — importer les fichiers | Conservé |

Le fichier `prompt-template.txt`, `prompt_builder.py`, Studio Visuel et le Skill IA-Art restent la source de vérité existante.

## 4. Import et validation

| Fonction 0.2.1 | Web Docker 0.3.0 |
| --- | --- |
| Drag & drop | Conservé |
| Choisir plusieurs fichiers | Conservé |
| Choisir un dossier | Conservé via sélecteur de dossier navigateur |
| PNG / JPG / JPEG / WebP | Conservés |
| Markdown / TXT / JSON | Conservés |
| Limite de taille par fichier | Conservée |
| Copie dans `projects/<id>/v<version>/artifacts` | Conservée |
| Validation de lisibilité image | Conservée |
| Validation largeur / hauteur | Conservée |
| Validation texte UTF-8 non vide | Conservée |
| Validation JSON objet | Conservée |
| SHA-256 des fichiers | Conservé |
| Image obligatoire | Conservée |
| Manifest facultatif avec avertissement | Conservé |
| Liste des contrôles | Conservée |
| Galerie des images | Conservée |
| `Je valide ce résultat` | Conservé |
| Passage au statut Validé | Conservé |

## 5. Export

| Fonction 0.2.1 | Web Docker 0.3.0 |
| --- | --- |
| Export disponible uniquement après validation | Conservé |
| Copie de tous les livrables | Conservée |
| Ajout de `project.json` | Conservé |
| Dossier `<slug>-v<version>` | Conservé dans l'archive téléchargée |

L'application desktop ouvrait un sélecteur de dossier Windows. Une application web ne peut pas écrire arbitrairement dans un dossier du poste client : le navigateur télécharge donc une archive ZIP contenant **exactement le même dossier et les mêmes fichiers**.

## 6. n8n / webhook — invariant impératif

Le flux n8n ne change pas.

Le client web appelle **le même `WebhookClient` Python et le même `SubmissionService`** que la version desktop.

Invariants :

- `schema_version` reste `1.0` ;
- `source` reste `visual-ai-studio` ;
- même bloc `project` ;
- même bloc `output` ;
- même liste `artifacts` ;
- même bloc `validation` ;
- multipart identique : `artifact_0`, `artifact_1`, … + `metadata` ;
- `Idempotency-Key` identique : SHA-256 de `<project_id>:<version>` ;
- nom du header d'authentification conservé ;
- secret conservé côté serveur / variable d'environnement ;
- mêmes réponses acceptées : `success` et `duplicate` ;
- `execution_id`, `remote_url`, `message`, `retryable`, `duplicate_avoided` conservés ;
- journalisation `automation_runs` conservée.

Docker Desktop peut atteindre un n8n exposé sur le poste via `host.docker.internal`. Cela ne modifie pas le contrat n8n, uniquement l'adresse réseau utilisée depuis le conteneur.

## 7. Paramètres

| Fonction 0.2.1 | Web Docker 0.3.0 |
| --- | --- |
| Dossier des projets visible | Conservé |
| Choisir le dossier | Conservé dans le volume Docker monté |
| Enregistrer | Conservé |
| Paramètres techniques n8n non exposés dans l'UI | Conservé |

Les paramètres techniques existants restent fournis par `settings.json` ou par variables d'environnement Docker.

## 8. Données et historique

- SQLite reste utilisé ;
- les tables et repositories Python existants restent utilisés ;
- la structure des projets reste la même ;
- les anciens types de livrables Pinterest / Instagram / synthèse / Notion restent lisibles pour l'historique ;
- le dossier hôte contenant `visual-ai-studio.db` peut être monté directement dans `/data` pour réutiliser l'historique existant ;
- aucun SaaS, authentification, multi-utilisateur, publication Instagram directe ou fonction supplémentaire n'est introduit.
