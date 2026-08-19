# Visual AI Studio

Visual AI Studio est une application Windows locale de création visuelle assistée par intelligence artificielle.

## Objectif

Fournir un workflow simple permettant de :

1. créer un brief visuel ;
2. choisir une destination ou un format ;
3. générer une proposition avec un agent IA ;
4. générer ou importer le visuel ;
5. contrôler et valider le résultat ;
6. exporter les livrables ;
7. transmettre facultativement le résultat vers une automatisation externe.

## Modes prévus

- Generic
- Pinterest
- Instagram
- Custom

Les modes définissent les contraintes de sortie mais ne sont pas des intégrations obligatoires avec les plateformes.

## Principes

Visual AI Studio doit rester :

- local-first ;
- mono-utilisateur dans sa première version ;
- indépendant de tout compte Pinterest, Instagram ou Notion ;
- dépourvu de branding utilisateur embarqué ;
- utilisable sans n8n ;
- utilisable sans automatisation externe ;
- configurable par l'utilisateur.

## Branding

Le branding est facultatif.

Un utilisateur pourra éventuellement configurer :

- un nom ;
- un logo ;
- une signature ;
- une position ;
- des règles d'application.

Aucun branding personnel n'est fourni par défaut.

## Agent IA

La cible prévoit un agent générique de création visuelle.

L'agent devra adapter ses sorties au mode sélectionné :

- Generic ;
- Pinterest ;
- Instagram ;
- Custom.

L'intégration OpenAI sera réalisée après stabilisation du contrat de données entre l'application et l'agent.

## Automatisation

L'automatisation est facultative.

La première intégration envisagée est un webhook générique compatible avec n8n.

Visual AI Studio ne doit pas connaître la destination finale du workflow.

Un webhook pourra par exemple transmettre les résultats vers :

- Pinterest ;
- Instagram ;
- Notion ;
- un stockage ;
- une API ;
- tout autre workflow n8n.

## Architecture

Application Windows :

- Python 3.11+
- PySide6
- Pydantic
- SQLite / SQLAlchemy
- keyring
- PyInstaller

## Etat

Projet en cours de généralisation à partir d'une application locale existante.

Le dépôt reste privé pendant cette phase.