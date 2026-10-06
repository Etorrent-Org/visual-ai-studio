# IA Art Studio Free

Version web statique et gratuite d’IA Art Studio.

## Périmètre

- brief créatif ;
- génération locale du prompt ;
- copie presse-papiers ;
- téléchargement du prompt en TXT ;
- aucun compte ;
- aucun backend ;
- aucune API ;
- aucune donnée envoyée ou sauvegardée sur le serveur.

Le dossier `free/` peut être déployé tel quel sur un hébergement web statique, notamment OVH Perso.

## Test local

Ouvrir `index.html` directement ou servir le dossier avec un serveur HTTP statique.

## Déploiement OVH

Le workflow GitHub Actions `.github/workflows/deploy-free-ovh.yml` déploie ce dossier par FTP lorsque les secrets OVH sont configurés dans GitHub.
