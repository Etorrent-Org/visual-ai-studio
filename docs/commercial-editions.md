# IA Art Studio — éditions commerciales

## Positionnement

IA Art Studio est décliné en deux expériences distinctes afin d’éviter un faux système de licence posé sur du code historiquement publié sous MIT.

### Free — service web public

Hébergé sur `ia-art.7-sens.fr`.

Fonctions :
- brief créatif ;
- formats Instagram et personnalisé ;
- génération déterministe du prompt ;
- copie / export TXT ;
- aucun compte ;
- aucun stockage serveur ;
- aucune intégration Notion ou n8n.

Architecture : HTML/CSS/JavaScript statiques, compatible OVH Perso.

### Pro — produit self-hosted

Distribution Docker destinée à l’acheteur.

Fonctions :
- projets persistants ;
- SQLite ;
- historique ;
- briefs et prompts versionnés ;
- fichiers de référence ;
- import des livrables ;
- validation ;
- export ZIP ;
- configuration n8n ;
- import Notion via workflow n8n ;
- sauvegarde du volume applicatif à documenter et automatiser.

Architecture : React + FastAPI + SQLite + Docker.

## Modèle commercial

La version Free sert de démonstrateur et d’acquisition.

La version Pro est vendue comme package self-hosted : application, image/compose, template Notion, workflows n8n nettoyés, documentation d’installation et mises à jour selon les conditions commerciales de l’offre.

Aucune promesse de SaaS multi-utilisateur n’est faite à ce stade.

## Limite juridique / licence

Le code déjà publié sous MIT reste réutilisable selon la licence MIT. La valeur commerciale doit donc venir du produit packagé, des nouvelles briques propriétaires éventuelles, des workflows, du template Notion, de la documentation, des mises à jour et du support, pas d’un simple masquage de boutons dans le code public existant.

## Roadmap

1. publier la Free statique ;
2. rebrander l’application Docker en IA Art Studio Pro ;
3. nettoyer le workflow n8n livré ;
4. préparer le template Notion commercial ;
5. ajouter une stratégie de sauvegarde du volume `/data` ;
6. produire le package d’installation Pro ;
7. recette sur environnement vierge ;
8. créer page produit et checkout.
