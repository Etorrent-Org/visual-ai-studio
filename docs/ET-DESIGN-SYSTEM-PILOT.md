# Pilote ET Design System v0.1.0 — Visual AI Studio

## Origine
Source graphique : Life Desk (Next.js/React, tokens couleur OKLCH),
plus cartouche japonais rouge **エルワン**. Le paquet autonome
`@et/design-system@0.1.0` est publié dans le dépôt privé `Etorrent-Org/et-design-system`, sur `main`, commit `376111faab17410203fd743316ef8b9a82f7f8e3`.

## Périmètre de cette branche
- CSS tokens copiés et figés dans `web/src/design-system/et-tokens.css`.
- Adaptateur CSS **propre à Visual AI Studio**, importé en dernier.
- SVG vectoriel servi localement depuis `web/public/brand/erwann-seal.svg`.
- Shell `.et-root` activé dans `App.tsx`, signature dans la navigation.
- **Aucun** changement des routes API, écriture disque, stockage, webhook,
  logique des formulaires, contrôles, dépendances ou structure Docker.

## Contrôles attendus
```bash
cd web
npm ci
npm run build
npm run check:et-theme
```
Tester manuellement les vues Projets / Créer / Administration,
les modales, les uploads, les actions clavier et les formats
1440px, 768px, 390px. Ne jamais tester les envois n8n réels avec
des données de production durant la revue graphique.

## Limites et suite
- À migrer vers une dépendance privée figée après mise en place d'un accès de build sûr au dépôt
  `Etorrent-Org/et-design-system` pour supprimer la duplication des tokens. Ne jamais stocker de token GitHub dans un Dockerfile ; la copie actuelle est volontairement versionnée et embarquée localement.
- Les nouvelles couleurs doivent être validées visuellement et avec
  contrôles d'accessibilité avant fusion.
- **PR de revue uniquement**. Ne pas fusionner ni déployer
  sur TatouneServer avant validation explicite.
- Rollback : abandon de cette branche / PR, ou revert du commit
  en cas de fusion ultérieure.
