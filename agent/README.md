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

Le fichier `studio-visuel-agent.zip` contient :

- `studio-visuel-agent.md` : instructions générales de l'agent ;
- `skill.zip` : Skill `visual-content-studio`.

Le Skill est la source de vérité fonctionnelle de Studio Visuel.

## Modes pris en charge par Visual AI Studio

- Instagram — mode par défaut, 1080 × 1350, ratio 4:5 ;
- Autre / personnalisé.

Instagram prend en charge une publication composée de **1 à 10 visuels principaux cohérents**. La fiche synthèse et le Markdown restent des livrables annexes séparés.

## Important

Studio Visuel et Visual AI Studio sont deux composants distincts :

- **Visual AI Studio** structure le brief, prépare le prompt, contrôle les résultats et gère l'export ;
- **Studio Visuel** réalise le workflow conversationnel de création visuelle.

Le package agent/Skill sera aligné séparément sur ce nouveau fonctionnement. Aucune clé API OpenAI n'est nécessaire dans Visual AI Studio.

## Licence

Studio Visuel et le Skill `visual-content-studio` fournis dans ce package sont distribués sous **licence MIT**.
