# SOS HAMMOUDI — Documentation technique

## Vue d'ensemble

Toolbox web à usage restreint. Premier outil : **Schema Maker** — génération de schémas à partir d'une description ou d'une image uploadée, avec envoi du résultat par email.

## Architecture

```
Front-end (GitHub Pages)  ──POST──▶  n8n Webhook
                                      │
                                      ├─ Auth (data table users)
                                      ├─ Quota (data table usage)
                                      ├─ Génération (IA / Canva / draw.io)
                                      ├─ Envoi Gmail
                                      └─ Réponse JSON
```

## Stack technique

| Couche | Techno |
|--------|--------|
| Front | HTML / CSS / JS vanilla — pas de framework |
| Hébergement front | GitHub Pages |
| Backend / orchestration | n8n (https://n8n.thomashammoudi.com) |
| Auth | Data table n8n "users" (whitelist email) |
| Quota | Data table n8n "usage" (compteur quotidien par email) |
| Envoi email | Gmail via n8n (OAuth) |
| Design | 8-bit neo-retro — Press Start 2P + Silkscreen |

## Fichiers du projet

| Fichier | Rôle |
|---------|------|
| `index.html` | Page unique SPA — formulaire complet |
| `styles.css` | Design 8-bit neo-retro (scanlines, pixel borders, néon) |
| `app.js` | Logique front : tabs, upload, validation, appel webhook |
| `assets/` | Images et ressources statiques |
| `documentation.md` | Ce fichier |
| `CLAUDE.md` | Instructions projet pour Claude Code |

## Formulaire — champs envoyés au webhook

| Champ | Type | Valeurs possibles |
|-------|------|-------------------|
| `email` | string | Email de l'utilisateur |
| `mode` | string | `describe` ou `upload` |
| `description` | string | Texte décrivant le schéma (si mode=describe) |
| `file` | File | Image uploadée (si mode=upload) |
| `engine` | string | `ai`, `canva`, `drawio` |
| `colors` | string | `neon`, `pastel`, `corporate`, `mono`, `sunset` |
| `style` | string | `corporate`, `modern`, `elegant`, `fun`, `random` |

## Workflow n8n attendu — "SOS Schema Maker"

### Nodes

1. **Webhook** (trigger) — `POST /webhook/schema-maker`
   - Reçoit FormData (multipart si upload)
   - Doit retourner les headers CORS pour GitHub Pages

2. **Lookup Data Table "users"** — vérifier si l'email est autorisé
   - Si non trouvé → répondre 403 `{ "message": "Email non autorisé" }`

3. **Lookup Data Table "usage"** — compter les usages du jour
   - Filtrer par email + date du jour
   - Si count >= limite → répondre 429 `{ "message": "Quota dépassé" }`

4. **Switch** sur `engine` :
   - **ai** : Prompt LLM → génère code Mermaid → conversion en image (SVG/PNG)
   - **canva** : Appel MCP Canva → crée design → export image
   - **drawio** : Génère XML draw.io → export PNG ou envoi .drawio

5. **Incrémenter usage** — ajouter une entrée dans la data table "usage"

6. **Gmail** — envoyer le résultat en pièce jointe

7. **Respond to Webhook** — `{ "success": true }`

### Data tables

**users** :
| Colonne | Type |
|---------|------|
| email | string |
| name | string |
| daily_limit | number |

**usage** :
| Colonne | Type |
|---------|------|
| email | string |
| date | string (YYYY-MM-DD) |
| engine | string |

### CORS

Le webhook doit retourner ces headers :
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

Option : répondre directement au preflight OPTIONS.

### Reset quotidien

Deux options :
1. **Pas de reset** : le workflow filtre par date du jour dans la table usage (recommandé, plus simple)
2. **Workflow schedulé** : purge la table usage chaque nuit (optionnel, pour garder la table propre)

## Prérequis

- Instance n8n accessible (https://n8n.thomashammoudi.com)
- Credentials Gmail configurées dans n8n (OAuth2)
- Data tables créées dans n8n
- Repo GitHub avec GitHub Pages activé

## Palettes de couleurs

| Palette | Couleurs |
|---------|----------|
| Néon | `#ff2d75` `#00e5ff` `#ffe600` `#39ff14` |
| Pastel | `#ffb3c6` `#b8e0ff` `#fff3b0` `#c3ffc1` |
| Corporate | `#1a3a5c` `#2980b9` `#e74c3c` `#ecf0f1` |
| Mono | `#1a1a2e` `#4a4a6a` `#9a9aba` `#eaeaff` |
| Sunset | `#ff6b2b` `#ff2d75` `#b026ff` `#1a0a3e` |

## Styles visuels

Les styles influencent la forme, la mise en page et le ton du schéma (indépendamment des couleurs).

| Style | Description | Directives pour le prompt IA |
|-------|-------------|------------------------------|
| Corporate | Pro & structuré | Lignes droites, angles nets, hiérarchie claire, polices sans-serif, spacing généreux, pas de fioritures |
| Moderne | Clean & épuré | Coins arrondis, ombres douces, minimaliste, icônes flat, beaucoup de blanc/espace |
| Élégant | Raffiné & sobre | Typographie fine, traits fins, palette restreinte, compositions équilibrées, serif possible |
| Fun | Coloré & vivant | Formes organiques, icônes illustrées, textures, contrastes forts, éléments décoratifs |
| Aléatoire | Surprise | Le moteur choisit aléatoirement parmi les 4 styles ci-dessus |

## Historique des changements

- **v1.0** — Setup initial : front-end complet (formulaire, design 8-bit), structure projet, documentation
- **v1.1** — Séparation couleurs/style : ajout champ "style" (corporate/moderne/élégant/fun/aléatoire), renommage ancien "style" en "couleurs". Workflow n8n créé (ID: G0ZozfIfxMGY33kE). Amélioration contrastes CSS.
