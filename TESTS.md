# Tests E2E — SOS Schema Maker (v1.5)

**Workflow n8n ID** : `G0ZozfIfxMGY33kE`
**URL front** : https://thomashmd.github.io/sos-hammoudi/
**URL webhook** : https://n8n.thomashammoudi.com/webhook/schema-maker
**Date** : 2026-02-21

---

## Corrections appliquées pendant les tests

- **Check Auth** : `alwaysOutputData: true` (sinon 0 items → pipeline morte)
- **Is Authorized?** : condition `Object.keys($json).length > 0` (remplace `$input.all().length`)
- **Check Usage** : filtre sur `email` seul (colonnes `date`/`engine` n'existent pas)
- **Check Quota** : `ConsoQuotidienne` (≠ `daily_limit`), 0/Null = illimité
- **Log Usage** : colonnes `email` + `NbConso` (≠ `date`/`engine`)
- **Gemini** : `models/gemini-3-flash-preview` (≠ `gemini-2.5-flash-preview-05-20` expiré)

### Corrections v1.3

- **Agent Image** : LLM remis à `gemini-3-flash-preview` (≠ `imagen-4.0-fast-generate-001` qui est un modèle image, pas chat). Ajout nœud `Imagen API Tool` (HTTP Request Tool) connecté en `ai_tool` pour appeler l'API Imagen via l'agent.
- **Agent Draw.io** : prompt system renforcé — DOIT utiliser l'outil MCP Draw.IO, INTERDIT de renvoyer un lien mermaid.ink
- **Agent Canva** : prompt system renforcé — DOIT utiliser l'outil MCP Canva, INTERDIT de renvoyer un lien mermaid.ink
- **Consolidate AI / Draw.io / Canva** : ajout champ `deliverableHtml` — contient le livrable principal (image base64, lien Draw.io, lien Canva)
- **Send Gmail** : email restructuré — livrable en haut, section Mermaid séparée ("Au cas où, le Mermaid")
- **Normalize Email** : nouveau nœud Code entre Webhook et Check Auth — normalise l'email (lowercase + suppression dots pour Gmail/Googlemail)

### Corrections v1.4

- **Normalize Email** : output désormais `body.email` (original lowercased) + `body.normalizedEmail` (canonical, sans dots Gmail). Avant, seul l'email normalisé était passé, ce qui cassait le lookup exact en base.
- **Check Auth** : filtre email supprimé — récupère désormais **toutes** les lignes de la table Autorisations (le filtre exact ne supportait pas la comparaison normalisée).
- **Smart Auth Check** : nouveau nœud Code inséré entre `Check Auth` et `Is Authorized?` — compare l'email normalisé de l'input avec chaque email normalisé de la base. Tolère toutes les variantes Gmail (dots, case).
- **Chaîne d'auth** : `Webhook → Normalize Email → Check Auth → Smart Auth Check → Is Authorized?`
- **Imagen API Tool** : endpoint corrigé `:predict` (au lieu de `:generateImages`), body format corrigé (`instances[].prompt` + `parameters.sampleCount` au lieu de `prompt` + `config.numberOfImages`).

### Corrections v1.5

- **Branche IA refactorée** : suppression du pattern Agent Image + `toolHttpRequest` (Imagen API Tool). Le credential `googlePalmApi` réécrivait l'URL dans le contexte `toolHttpRequest` → "Invalid URL". Remplacé par 2 nœuds déterministes :
  - `Build Imagen Prompt` (Code) : construit un prompt descriptif en anglais à partir du Mermaid + style + couleurs
  - `Call Imagen API` (HTTP Request) : POST direct vers l'API Imagen avec le credential `googlePalmApi` (qui fonctionne correctement sur `httpRequest` classique)
- **Consolidate AI** : adapté au format de réponse HTTP directe (plus de `$json.output` d'agent)
- **Check Quota** : corrigé pour référencer `$('Smart Auth Check')` au lieu de `$('Check Auth')` (bug v1.4 — récupérait le quota du premier utilisateur de la table au lieu de l'utilisateur authentifié)
- **Agent Draw.io** : prompt système mis à jour — préfère les liens d'édition, accepte le XML brut comme sortie valide
- **Consolidate Draw.io** : refactoré — gère 3 cas (URL Draw.io, XML brut avec instructions copier/coller, fallback texte). Nettoyage des balises markdown dans la réponse LLM.
- **Google Gemini Chat Model2** : ajout `maxOutputTokens: 8192` pour éviter la troncature des URLs/XML Draw.io

### Corrections v1.6

- **Remplacement Imagen → Gemini native image generation** : l'API Imagen (`imagen-4.0-fast-generate-001:predict`) nécessitait un compte Google Cloud facturé ("Imagen API is only accessible to billed users"). Remplacé par Gemini `generateContent` avec `responseModalities: ["TEXT", "IMAGE"]` — inclus dans le free tier (500 req/jour), même clé API (`googlePalmApi`).
  - `Build Imagen Prompt` → `Build Image Prompt` : body restructuré pour `generateContent` (format `contents[].parts[].text` + `generationConfig.responseModalities`)
  - `Call Imagen API` → `Call Gemini Image` : URL changée vers `gemini-2.0-flash-exp:generateContent`
  - `Consolidate AI` : parser le format Gemini (`candidates[0].content.parts[].inlineData.data`) au lieu d'Imagen (`predictions[0].bytesBase64Encoded`)

---

## Phase 0 — Prérequis

- [x] Workflow n8n **activé**
- [x] Email `thomas.hammoudi@gmail.com` dans la data table **Autorisations**
- [x] Data table **Consommation** accessible
- [x] Page GitHub Pages accessible

---

## Phase 1 — Validations front-end (vérification par code)

| # | Test | Statut | Notes |
|---|------|--------|-------|
| 1.1 | Formulaire vide → soumission | ✅ | `<input type="email" required>` — validation HTML5 native |
| 1.2 | Mode describe, description vide, email valide | ✅ | `app.js:93-96` — showError correct |
| 1.3 | Mode upload, sans fichier, email valide | ✅ | `app.js:97-99` — showError correct |
| 1.4 | Switcher describe → upload → describe | ✅ | `app.js:26-38` — toggle classes correct |

> Note : tests vérifiés par analyse de code (MCP Chrome ne permettait pas les clicks)

---

## Phase 2 — Gestion des erreurs backend

| # | Test | Statut | Notes |
|---|------|--------|-------|
| 2.1 | Email non autorisé (`inconnu@test.com`) | ✅ | 403 + `{"success":false,"message":"Email non autorisé"}` |
| 2.2 | Quota dépassé (simulation) | ⏭️ | Skippé — ConsoQuotidienne = Null (illimité) pour l'utilisateur test |

---

## Phase 3 — Chemin nominal : moteur IA

| # | Test | Statut | Notes |
|---|------|--------|-------|
| 3.1 | Email autorisé, describe, organigramme CEO/CTO/CFO, AI, neon, corporate | ✅ | 200 + email envoyé |
| 3.2 | Vérification email reçu (3.1) | ⬜ | À vérifier manuellement dans la boîte mail |
| 3.3 | Même test, style **random** | ✅ | 200 + email envoyé |

---

## Phase 4 — Chemin nominal : moteur Canva

| # | Test | Statut | Notes |
|---|------|--------|-------|
| 4.1 | Email autorisé, describe, moteur Canva, pastel, modern | ❌ | MCP Canva : "Authentication failed" — credentials OAuth2 à ré-authentifier dans n8n |
| 4.2 | Vérification email reçu (4.1) | ⏭️ | Bloqué par 4.1 |

> **Action requise** : ré-authentifier les credentials MCP Canva dans n8n Settings > Credentials > "MCP account"

---

## Phase 5 — Chemin nominal : moteur Draw.io

| # | Test | Statut | Notes |
|---|------|--------|-------|
| 5.1 | Email autorisé, describe, moteur Draw.io, mono, elegant | ✅ | 200 + email envoyé |
| 5.2 | Vérification email reçu (5.1) | ⬜ | À vérifier manuellement dans la boîte mail |

---

## Phase 6 — Vérification quota

| # | Test | Statut | Notes |
|---|------|--------|-------|
| 6.1 | Data table Consommation après phases 3-5 | ⬜ | À vérifier — lignes insérées pour tests 3.1, 3.3, 5.1 |

---

## Résumé final

- **Tests passés** : 9 / 14
- **Tests échoués** : 1 (Canva auth)
- **Tests skippés** : 2 (quota illimité, email Canva)
- **Tests en attente de vérification manuelle** : 3 (emails reçus 3.2, 5.2 + data table 6.1)
- **Emails envoyés** : AI ✅, Canva ❌, Draw.io ✅

### Actions requises
1. **Vérifier les 3 emails** reçus sur thomas.hammoudi@gmail.com (tests 3.1, 3.3, 5.1)
2. **Ré-authentifier MCP Canva** dans n8n pour débloquer le test 4.1
3. **Vérifier la data table Consommation** pour les lignes insérées

---

## Phase 7 — Tests post-corrections v1.3

| # | Test | Statut | Notes |
|---|------|--------|-------|
| 7.1 | Moteur AI — image générée via Imagen API | ⬜ | Vérifier que l'email contient une image (pas juste le Mermaid) |
| 7.2 | Moteur AI — email séparé livrable / Mermaid | ⬜ | Section "Ton livrable" en haut, "Au cas où, le Mermaid" en bas |
| 7.3 | Moteur Draw.io — lien Draw.io dans email | ⬜ | Vérifier que le lien pointe vers diagrams.net, PAS mermaid.ink |
| 7.4 | Moteur Draw.io — email séparé livrable / Mermaid | ⬜ | Même structure que 7.2 |
| 7.5 | Email case insensitive — `Thomas.HAMMOUDI@gmail.com` | ⬜ | Doit être accepté (normalisé en lowercase) |
| 7.6 | Email dot insensitive Gmail — `t.homas.hammoudi@gmail.com` | ⬜ | Doit être accepté (dots supprimés pour Gmail) |
| 7.7 | Canva — après ré-auth credentials | ⬜ | En attente ré-auth MCP Canva |

---

## Phase 8 — Tests normalisation email v1.4

La v1.3 avait un bug : le nœud `Normalize Email` supprimait les dots Gmail **avant** le lookup exact en base. Comme la data table contient `thomas.hammoudi@gmail.com` (avec dots), le filtre exact ne trouvait rien → 403.

**Fix** : `Check Auth` récupère toutes les lignes, `Smart Auth Check` fait la comparaison normalisée des deux côtés.

| # | Test | Email envoyé | Résultat attendu | Statut | Notes |
|---|------|-------------|------------------|--------|-------|
| 8.1 | Email original avec dots | `thomas.hammoudi@gmail.com` | 200 | ⬜ | Cas nominal — email identique à la base |
| 8.2 | Email uppercase + dots | `Thomas.HAMMOUDI@gmail.com` | 200 | ⬜ | Lowercase + dots tolérés |
| 8.3 | Email sans dots | `thomashammoudi@gmail.com` | 200 | ⬜ | Sans dots = même mailbox Gmail |
| 8.4 | Email dots aléatoires | `t.homas.hammoudi@gmail.com` | 200 | ⬜ | Dots à n'importe quel endroit |
| 8.5 | Email non autorisé | `inconnu@test.com` | 403 | ⬜ | Doit toujours être refusé |
