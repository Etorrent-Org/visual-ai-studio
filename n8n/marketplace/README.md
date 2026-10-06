# Automation Pack — IA Art Studio Pro

Ce dossier contient les workflows n8n destinés à la distribution commerciale.

## 01 — Import Notion — Instagram

Fichier : `IA-Art-Studio-Pro-01-Import-Notion-Instagram.json`

### Avant activation

1. Importer le JSON dans n8n.
2. Sur le nœud **Webhook**, sélectionner ou créer une credential **Header Auth**.
3. Sur les trois appels HTTP Notion, sélectionner votre credential **Notion API**.
4. Ouvrir le nœud **Construire la fiche Instagram** et remplacer :
   `RESELECTIONNER_DATA_SOURCE_IMAGES`
   par l’identifiant de la source de données `Images` de votre copie du template.
5. Vérifier les noms de propriétés Notion utilisés par le workflow.
6. Tester avec un projet de démonstration.
7. Vérifier qu’un second envoi ne crée pas de doublon fonctionnel.
8. Activer le workflow uniquement après validation.

## Sécurité

La version distribuée :
- ne contient aucun credential n8n ;
- ne contient aucun identifiant de credential ;
- ne contient aucun ID de source Notion personnel ;
- est désactivée par défaut.

Toute nouvelle exportation doit repasser par le même contrôle avant publication.
