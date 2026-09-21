# Import Notion IA-Art — version web Instagram

Le workflow d'entrée de la version web actuelle est :

`n8n/IA-Art-01-Import-Notion-Instagram.json`

Il reçoit le paquet produit par IA-Art 5.0.2 :

- un à dix fichiers `instagram*.jpg` ou `instagram*.jpeg` ;
- un fichier `synthese.png` ;
- un fichier `notion.md` ;
- `metadata.json` et le manifeste restent techniques.

Le workflow téléverse les fichiers éditoriaux dans Notion, crée une fiche dans la source de données `Images`, puis renvoie :

```json
{
  "status": "success",
  "execution_id": "…",
  "notion_page_url": "https://www.notion.so/…"
}
```

## URL à configurer

Dans Visual AI Studio, ouvrir **Administration → Connexion n8n → URL du webhook** et utiliser l’URL de production :

`http://IP-DE-LA-VM:5678/webhook/ia-art-import-notion-hub`

Le workflow doit être actif. `webhook-test` et `127.0.0.1` ne conviennent pas lorsque l’application web et n8n sont dans des environnements distincts.

## Authentification

Le nom de l’en-tête et le secret se configurent dans **Administration**. Le nom doit être identique à celui du credential **Header Auth** du nœud Webhook. Le secret n’est pas affiché et ne doit pas être écrit dans le dépôt.

Les workflows qui publient ou traitent ensuite les fiches partent de Notion et ne sont pas modifiés par cet import.
