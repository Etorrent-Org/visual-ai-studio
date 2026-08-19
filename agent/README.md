# Studio Visuel

Visual AI Studio fonctionne avec un agent conversationnel séparé nommé **Studio Visuel**.

L'application Windows ne réalise aucun appel direct à une API OpenAI.

## Principe

Le workflow est volontairement simple :

1. créer un brief dans Visual AI Studio ;
2. sélectionner Pinterest, Instagram ou un format personnalisé ;
3. générer le prompt destiné à Studio Visuel ;
4. copier ce prompt ;
5. ouvrir Studio Visuel dans ChatGPT ;
6. coller le prompt et suivre le workflow conversationnel de l'agent ;
7. récupérer les fichiers produits ;
8. les importer dans Visual AI Studio ;
9. contrôler et valider le résultat ;
10. exporter les fichiers.

## Package

Le fichier :

`studio-visuel-agent.zip`

contient :

- `studio-visuel-agent.md` : instructions générales de l'agent ;
- `skill.zip` : Skill `visual-content-studio`.

Le Skill est la source de vérité fonctionnelle de Studio Visuel.

## Modes pris en charge

- Pinterest
- Instagram
- Autre / personnalisé

## Important

Studio Visuel et Visual AI Studio sont deux composants distincts :

- **Visual AI Studio** structure le brief, prépare le prompt, contrôle les résultats et gère l'export ;
- **Studio Visuel** réalise le workflow conversationnel de création visuelle.

Aucune clé API OpenAI n'est nécessaire dans Visual AI Studio.
## Licence

Studio Visuel et le Skill `visual-content-studio` fournis dans ce package
sont distribués sous **licence MIT**.

Le fichier `LICENSE` est inclus dans le package distribué.
