# Studio Visuel

Visual AI Studio fonctionne avec un agent conversationnel séparé nommé **Studio Visuel**.

L'application Windows ne réalise aucun appel direct à une API OpenAI.

## Principe

Le workflow est volontairement simple :

1. créer un brief dans Visual AI Studio ;
2. sélectionner Instagram ou un format personnalisé ;
3. choisir de 1 à 10 visuels principaux pour la publication ;
4. générer le prompt destiné à Studio Visuel ;
5. copier ce prompt ;
6. ouvrir Studio Visuel dans ChatGPT ;
7. coller le prompt et suivre le workflow conversationnel de l'agent ;
8. récupérer les fichiers produits ;
9. les importer dans Visual AI Studio ;
10. contrôler et valider le résultat ;
11. exporter les fichiers.

## Package

Le fichier `studio-visuel-agent.zip` contient exactement :

- `studio-visuel-agent.md` : instructions Instagram multi-images de l'agent ;
- `skill.zip` : Skill **IA-Art** aligné sur Instagram ;
- `LICENSE` : licence MIT.

Le Skill IA-Art est la source de vérité pour la signature, la synthèse, le Markdown Notion et le packaging final.

## Modes pris en charge par Visual AI Studio

- Instagram — mode par défaut, 1080 × 1350, ratio 4:5 ;
- Autre / personnalisé.

Le workflow IA-Art de publication utilise uniquement Instagram.

Instagram prend en charge une publication composée de **1 à 10 visuels principaux cohérents**. Studio Visuel doit produire exactement le nombre demandé. La fiche synthèse et le Markdown restent des livrables annexes séparés et ne sont jamais comptés parmi les visuels du post.

## Répartition des responsabilités

- **Visual AI Studio** structure le brief et transmet le nombre de visuels demandé ;
- **Studio Visuel** prépare la direction artistique, le storyboard et exactement N prompts/images ;
- **IA-Art** signe les N images et fabrique un paquet unique avec une synthèse et un Markdown Notion.

Aucune clé API OpenAI n'est nécessaire dans Visual AI Studio.

## Licence

Studio Visuel et le Skill IA-Art fournis dans ce package sont distribués sous **licence MIT**.
