# Contribuer à Visual AI Studio

Merci de votre intérêt pour Visual AI Studio.

## Avant de créer un ticket

- vérifiez qu'un ticket similaire n'existe pas déjà ;
- utilisez le formulaire **Bug** pour un problème reproductible ;
- utilisez le formulaire **Feature** pour une amélioration suffisamment cadrée ;
- utilisez **Discussions** pour une question générale, un retour d'usage ou une idée encore exploratoire ;
- ne publiez jamais de clé, mot de passe, jeton, donnée client ou autre information sensible.

## Signaler un bug

Merci d'indiquer au minimum :

- la version de Visual AI Studio ;
- la version de Windows ;
- les étapes permettant de reproduire le problème ;
- le résultat attendu ;
- le résultat obtenu ;
- le message d'erreur ou le log utile, après suppression des informations sensibles.

## Proposer une amélioration

Décrivez d'abord le besoin utilisateur et la valeur attendue. Une solution technique peut être proposée ensuite, mais le besoin métier reste prioritaire.

## Pull requests

Pour une contribution de code :

1. créez une branche dédiée ;
2. limitez la modification au sujet traité ;
3. exécutez les contrôles du projet ;
4. décrivez clairement le changement et son impact dans la pull request.

Contrôles de référence :

```powershell
.\.venv\Scripts\python.exe -m ruff check src tests
.\.venv\Scripts\python.exe -m mypy src
.\.venv\Scripts\python.exe -m pytest -q
```

## Licence

En contribuant au dépôt, vous acceptez que votre contribution soit distribuée sous la licence MIT du projet.
