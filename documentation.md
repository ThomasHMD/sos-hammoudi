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
| `engine` | string | `ai`, `drawio` |
| `colors` | string | `neon`, `pastel`, `corporate`, `mono`, `sunset` |
| `style` | string | `corporate`, `modern`, `elegant`, `fun`, `random` |

## Workflow n8n attendu — "SOS Schema Maker"

### Nodes

1. **Webhook** (trigger) — `POST /webhook/schema-maker`
   - Reçoit FormData (multipart si upload)
   - Doit retourner les headers CORS pour GitHub Pages

2. **Normalize Email** — normalise l'email avant vérification
   - Output `body.email` = email original en minuscules
   - Output `body.normalizedEmail` = email canonical (sans dots pour Gmail/Googlemail)
   - Exemple : `T.homas.Hammoudi@gmail.com` → email=`t.homas.hammoudi@gmail.com`, normalizedEmail=`thomashammoudi@gmail.com`

3. **Check Auth (Data Table "users")** — récupère toutes les lignes de la table Autorisations (sans filtre)

4. **Smart Auth Check** — compare `normalizedEmail` avec chaque email de la table (normalisé aussi)
   - Tolère toutes les variantes Gmail : dots, case, googlemail.com
   - Si correspondance trouvée → passe la ligne auth (avec ConsoQuotidienne)
   - Si aucune correspondance → objet vide → `Is Authorized?` renvoie 403

3. **Lookup Data Table "usage"** — compter les usages du jour
   - Filtrer par email + date du jour
   - Si count >= limite → répondre 429 `{ "message": "Quota dépassé" }`

4. **Switch** sur `engine` :
   - **ai** : Prompt LLM → génère code Mermaid → Prepare Mermaid Render → Consolidate AI (image via mermaid.ink)
   - **drawio** : Appel MCP Draw.io → crée diagramme

5. **Consolidate** (un node par moteur) — normalise `{ email, engine, style, colors, mermaidCode, result, deliverableHtml }`
   - **Consolidate AI** : utilise l'URL mermaid.ink comme `<img src>`, produit `deliverableHtml` avec image inline
   - **Consolidate Draw.io** : extrait le lien diagrams.net/draw.io, produit `deliverableHtml` avec lien cliquable

6. **Prepare Mermaid Link** — construit l'URL `mermaid.ink` à partir du code Mermaid (base64)

7. **Gmail** — envoie un email HTML structuré en 2 sections :
   - **Ton livrable** : contenu de `deliverableHtml` (image AI, lien Draw.io ou lien Canva)
   - **Au cas où, le Mermaid** : lien mermaid.ink + code source Mermaid dans `<pre>`
   - Pas de pièce jointe

8. **Log Usage** — insère une ligne dans la data table "usage" (références explicites via `$('Prepare Mermaid Link')`)

9. **Respond to Webhook** — `{ "success": true }`

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
- **v1.2** — Simplification email : suppression du téléchargement JPG via mermaid.ink (pas de pièce jointe), inclusion du code Mermaid source dans le corps du mail. Réordonnancement `Send Gmail` → `Log Usage`. `Log Usage` référence `Prepare Mermaid Link` explicitement pour éviter la perte de données.
- **v1.3** — Corrections post-tests : Agent Image fixé (LLM → gemini-3-flash + HTTP Request Tool pour Imagen API), prompts Draw.io/Canva renforcés (interdiction mermaid.ink), email restructuré (livrable en haut + Mermaid séparé), normalisation email (case insensitive + dots Gmail).
- **v1.4** — Fix normalisation email : le filtre exact de `Check Auth` ne supportait pas la comparaison normalisée (dots Gmail). Ajout nœud `Smart Auth Check` qui récupère toutes les lignes et compare avec normalisation des deux côtés. `Normalize Email` exporte désormais `email` (original) + `normalizedEmail` (canonical). Fix Imagen API Tool : endpoint corrigé (`:predict` au lieu de `:generateImages`), format body corrigé (`instances[].prompt` + `parameters.sampleCount`).
- **v1.5** — Refactoring branche IA : remplacement Agent Image + Imagen API Tool (toolHttpRequest cassé par le credential googlePalmApi) par `Build Imagen Prompt` (Code) + `Call Imagen API` (HTTP Request classique). Fix Check Quota (référençait Check Auth au lieu de Smart Auth Check). Fix Draw.io : prompt amélioré (accepte XML brut), Consolidate Draw.io gère URL + XML + fallback, maxOutputTokens: 8192 sur le LLM.
- **v1.6** — Remplacement Imagen → Gemini native image generation : l'API Imagen nécessitait un compte GCP facturé. Remplacé par Gemini `generateContent` avec `responseModalities: ["TEXT", "IMAGE"]` (free tier, même clé API). Nœuds renommés : `Build Image Prompt`, `Call Gemini Image`. `Consolidate AI` adapté au format Gemini (`candidates[0].content.parts[].inlineData`).
- **v1.7** — Refonte branche IA : remplacement de la génération d'images par IA (Gemini) par un rendu code pur via mermaid.ink. L'IA (Agent Architecte) génère toujours le code Mermaid, mais le rendu visuel est désormais déterministe. Nœuds modifiés : `Build Image Prompt` → `Prepare Mermaid Render` (applique un thème Mermaid `%%{init:...}%%` selon la palette de couleurs choisie, construit l'URL mermaid.ink), `Consolidate AI` adapté pour utiliser l'URL mermaid.ink comme `<img src>`. Plus de dépendance à l'API Gemini pour la génération d'images. Les 5 palettes (neon, pastel, corporate, mono, sunset) sont appliquées via les `themeVariables` natifs de Mermaid.
- **v1.8** — MVP : suppression du moteur Canva (connexion impossible). Front-end : renommage "IA" → "MERMAID (IA + Mermaid)", suppression du bouton Canva. Workflow n8n : suppression des nœuds `Agent Canva` et `Consolidate Canva`, mise à jour du Switch Engine (2 sorties au lieu de 3 : ai + drawio). Nettoyage du nœud orphelin `Rube`. 2 moteurs restants : Mermaid (IA) et Draw.io.
