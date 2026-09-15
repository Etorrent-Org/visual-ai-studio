# Studio Visuel

Visual AI Studio fonctionne avec un agent conversationnel séparé nommé **Studio Visuel**.

L'application web Docker ne réalise aucun appel direct à une API OpenAI.

## Principe

Le workflow est volontairement simple :

1. créer un brief dans Visual AI Studio ;
2. sélectionner Instagram ou un format personnalisé ;
3. choisir de 1 à 10 visuels principaux pour la publication ;
4. générer le prompt destiné à Studio Visuel ;
5. copier ce prompt ;
6. ouvrir Studio Visuel dans ChatGPT ;
7. coller le prompt et suivre le workflow conversationnel de l'agent ;
8. après `image_gen`, considérer les PNG affichés comme des sources intermédiaires et répondre simplement **`continue`** ;
9. laisser IA-Art produire les JPEG signés, la synthèse PNG, le Markdown Notion et l'archive complète ;
10. récupérer les fichiers finaux ;
11. les importer dans Visual AI Studio ;
12. contrôler et valider le résultat ;
13. exporter les fichiers.

## Package

Les ZIP générés ne sont plus versionnés directement afin d'éviter toute corruption d'un binaire lors d'une mise à jour distante.

La source packagée du Skill IA-Art 5.0.2 est stockée sous forme de segments Base64 dans :

`agent/package/skill.zip.b64.part*`

Le script `agent/package_agent.py` :

1. reconstitue `skill.zip` ;
2. vérifie son SHA-256 attendu ;
3. vérifie que le ZIP IA-Art est lisible ;
4. génère `studio-visuel-agent.zip` ;
5. vérifie la structure du package final.

Pour reconstruire localement les packages :

```powershell
python agent/package_agent.py
```

Les fichiers sont créés dans `agent/dist/` :

- `skill.zip` : Skill **IA-Art** prêt à être installé dans ChatGPT ;
- `studio-visuel-agent.zip` : package complet Studio Visuel.

Le package Studio Visuel contient exactement :

- `studio-visuel-agent.md` : instructions Instagram multi-images de l'agent ;
- `skill.zip` : Skill **IA-Art** aligné sur Instagram ;
- `LICENSE` : licence MIT.

Le Skill IA-Art est la source de vérité pour la signature, la synthèse, le Markdown Notion et le packaging final.

Pour Instagram, les visuels éditoriaux finaux sont toujours livrés en **JPEG/JPG 1080 × 1350**. Les PNG produits par `image_gen` sont uniquement intermédiaires. Une livraison IA-Art complète contient obligatoirement les N JPEG/JPG signés, une fiche de synthèse PNG, un Markdown Notion unique et l'archive éditoriale correspondante.

### Reprise après génération

`image_gen` termine son tour sur les images générées. Studio Visuel doit donc annoncer avant la génération que l'utilisateur devra répondre **`continue`** lorsque les PNG seront visibles.

Au message `continue` — ou un équivalent bref comme `ok`, `oui`, `vas-y` ou `go` — IA-Art reprend directement après la génération, sans refaire le brief ni les prompts, puis effectue dans le même tour :

1. découverte des N PNG sources ;
2. signature et conversion en JPEG/JPG réel ;
3. création de la synthèse PNG ;
4. création du Markdown Notion ;
5. création et vérification de l'archive complète.

Les PNG sources ne doivent jamais être présentés comme la livraison finale.

## Modes pris en charge par Visual AI Studio

- Instagram — mode par défaut, 1080 × 1350, ratio 4:5 ;
- Autre / personnalisé.

Le workflow IA-Art de publication utilise uniquement Instagram.

Instagram prend en charge une publication composée de **1 à 10 visuels principaux cohérents**. Studio Visuel doit produire exactement le nombre demandé. La fiche synthèse et le Markdown restent des livrables annexes séparés et ne sont jamais comptés parmi les visuels du post.

## Répartition des responsabilités

- **Visual AI Studio** structure le brief et transmet le nombre de visuels demandé ;
- **Studio Visuel** prépare la direction artistique, le storyboard et exactement N prompts/images ;
- **IA-Art** reprend après `image_gen`, signe et convertit les N images en JPEG/JPG, puis fabrique un paquet unique avec une synthèse PNG et un Markdown Notion.

Aucune clé API OpenAI n'est nécessaire dans Visual AI Studio.

## Licence

Studio Visuel et le Skill IA-Art fournis dans ce package sont distribués sous **licence MIT**.
