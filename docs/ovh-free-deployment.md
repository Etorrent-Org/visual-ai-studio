# IA Art Studio Free — déploiement OVH Perso

La version Free est entièrement statique. Aucun Python, Docker, SQLite ou n8n n’est nécessaire côté OVH.

## Domaine recommandé

`ia-art.7-sens.fr`

Le sous-domaine doit pointer vers le répertoire cible configuré dans l’hébergement OVH.

## Secrets GitHub

Dans le dépôt GitHub, créer :

- `OVH_FTP_SERVER`
- `OVH_FTP_USERNAME`
- `OVH_FTP_PASSWORD`
- `OVH_FTP_TARGET`

Exemple de cible : `/www/ia-art/` selon la structure configurée dans OVH.

## Déploiement

Le workflow `Deploy IA Art Studio Free to OVH` :
- se lance manuellement ;
- se lance automatiquement sur les changements de `free/**` après merge sur `main` ;
- valide la présence des trois fichiers statiques ;
- saute proprement le déploiement tant que les secrets ne sont pas configurés.

## Données

Le site Free n’envoie aucune donnée à Atelier 7S. Le brief reste dans la page courante et le prompt est construit en JavaScript dans le navigateur.
