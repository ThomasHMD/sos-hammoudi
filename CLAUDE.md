# SOS HAMMOUDI — Contexte projet pour Claude Code

## Langue
Toujours répondre en **français**. Identifiants de code en anglais.

## Description
Toolbox web à usage restreint (whitelist email). Premier outil : Schema Maker.

## Stack
- **Front** : HTML / CSS / JS vanilla (pas de framework, pas de build)
- **Backend** : n8n (https://n8n.thomashammoudi.com) — webhooks + data tables
- **Hébergement** : GitHub Pages
- **Email** : Gmail via n8n

## Structure
```
sos-hammoudi/
├── index.html          # Page unique — formulaire Schema Maker
├── styles.css          # Design 8-bit neo-retro
├── app.js              # Logique front (tabs, upload, webhook call)
├── assets/             # Ressources statiques
├── documentation.md    # Doc technique complète (charger en contexte si besoin)
└── CLAUDE.md           # Ce fichier
```

## Design
- Thème "8-bit neo-retro" : fond sombre, couleurs néon (magenta, cyan, jaune, lime)
- Fonts : Press Start 2P (titres) + Silkscreen (corps)
- Effet scanlines CSS, bordures pixelisées, animations glow

## Webhook n8n
- URL : `https://n8n.thomashammoudi.com/webhook/schema-maker`
- Méthode : POST (FormData)
- Champs : email, mode, description/file, engine, colors, style
- `colors` = palette de couleurs (neon, pastel, corporate, mono, sunset)
- `style` = style visuel (corporate, modern, elegant, fun, random)
- Réponses : 200 (succès), 403 (email non autorisé), 429 (quota dépassé)

## Conventions
- Pas de framework JS, tout en vanilla
- Pas de build tool (pas de npm/webpack/vite)
- Éditer les fichiers existants plutôt qu'en créer de nouveaux
- Mettre à jour `documentation.md` quand on ajoute/modifie une fonctionnalité
- Ne pas commiter sans demande explicite
