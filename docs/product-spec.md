# Visual AI Studio - Product Specification

## 1. Vision

Visual AI Studio est un studio de création visuelle local permettant à un utilisateur de transformer une idée en livrables visuels structurés avec l'aide d'un agent IA.

Le produit ne dépend d'aucun workflow personnel, compte social ou espace documentaire spécifique.

## 2. Workflow principal

Brief
→ Mode de sortie
→ Agent IA
→ Proposition
→ Validation utilisateur
→ Génération ou import du visuel
→ Contrôles
→ Validation finale
→ Export
→ Automatisation facultative

## 3. Modes de sortie

### Generic

Création visuelle sans dépendance à une plateforme.

L'utilisateur peut choisir un preset ou un format personnalisé.

### Pinterest

L'agent adapte le résultat à une publication Pinterest.

Sorties possibles :

- image ;
- titre ;
- description ;
- texte alternatif ;
- métadonnées.

### Instagram

L'agent adapte le résultat à une publication Instagram.

Sorties possibles :

- image ;
- légende ;
- texte alternatif ;
- hashtags ;
- métadonnées.

### Custom

L'utilisateur définit librement :

- dimensions ;
- ratio ;
- contraintes ;
- texte ;
- destination.

## 4. Contrat Agent -> Application

L'agent doit retourner une structure stable indépendante de la plateforme.

Structure logique cible :

{
  "schema_version": "1.0",
  "mode": "generic|pinterest|instagram|custom",
  "concept": {
    "title": "",
    "intent": "",
    "audience": ""
  },
  "visual": {
    "width": null,
    "height": null,
    "aspect_ratio": "",
    "prompt": "",
    "negative_prompt": "",
    "text_overlay": ""
  },
  "publication": {
    "title": "",
    "caption": "",
    "alt_text": "",
    "hashtags": []
  }
}

Les champs non applicables peuvent être vides.

## 5. Branding

Le branding utilisateur est optionnel.

Configuration possible :

- activation ;
- texte de signature ;
- logo ;
- position ;
- opacité.

Aucun branding n'est activé par défaut.

## 6. Automatisation

L'automatisation n'est jamais obligatoire.

Visual AI Studio fournit un connecteur webhook générique.

Configuration :

- activé / désactivé ;
- nom ;
- URL ;
- méthode d'authentification ;
- secret ;
- timeout ;
- test de connexion.

Les secrets sont stockés dans le coffre système.

## 7. n8n

n8n est une automatisation possible, pas une dépendance du produit.

Visual AI Studio transmet un payload générique.

Le workflow n8n décide ensuite de la destination :

- réseau social ;
- Notion ;
- stockage ;
- API ;
- autre service.

## 8. Hors périmètre V1

La V1 ne fournit pas directement :

- authentification Pinterest ;
- authentification Instagram ;
- authentification Notion ;
- publication directe vers les réseaux sociaux ;
- hébergement cloud ;
- multi-utilisateur ;
- abonnement SaaS ;
- marketplace.

## 9. Distribution cible

Application Windows autonome.

Objectif final :

Visual-AI-Studio-Setup.exe

L'utilisateur ne doit pas avoir besoin :

- de Python ;
- de Git ;
- de Docker ;
- de n8n.

## 10. Etapes de développement

1. neutralisation complète de l'application ;
2. modèle de données universel ;
3. modes Generic / Pinterest / Instagram / Custom ;
4. contrat JSON agent ;
5. agent Visual AI ;
6. génération IA ;
7. branding optionnel ;
8. webhook générique facultatif ;
9. tests ;
10. packaging Windows.