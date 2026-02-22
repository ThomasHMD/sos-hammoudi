# Pipeline Mermaid → Flowchart PNG

## Résumé

Le processus convertit un diagramme Mermaid en image PNG haute résolution sans aucun moteur de rendu d'images IA ni outil tiers de type Mermaid CLI. Tout repose sur un script Python utilisant la bibliothèque **Pillow** (PIL) pour dessiner chaque élément du flowchart pixel par pixel sur un canvas.

L'avantage : contrôle total sur le rendu, le style, les couleurs, les polices, le positionnement. Le résultat est net, professionnel, et exportable en haute résolution (print-ready).

---

## Architecture du pipeline

```
Entrée Mermaid (texte)
        │
        ▼
  Parsing du Mermaid
  (extraction des nœuds, liens, styles)
        │
        ▼
  Moteur de layout
  (calcul des positions x/y de chaque élément)
        │
        ▼
  Rendu Pillow
  (dessin sur canvas PIL : boîtes, losanges, connecteurs, textes)
        │
        ▼
  Export PNG
```

---

## Étape 1 : Parsing du Mermaid

Le code Mermaid est du texte structuré. Il faut en extraire :

| Élément | Exemple Mermaid | Ce qu'on en tire |
|---------|----------------|------------------|
| Nœuds rectangulaires | `A["Réception fichier"]` | id=A, label="Réception fichier", type=box |
| Nœuds losange (décision) | `C{"Conforme ?"}` | id=C, label="Conforme ?", type=diamond |
| Nœuds cylindre (BDD) | `BDD[("Base de données")]` | id=BDD, label="Base de données", type=cylinder |
| Liens simples | `A --> B` | from=A, to=B, type=solid |
| Liens avec label | `H -- Oui --> I` | from=H, to=I, label="Oui", type=solid |
| Liens pointillés | `E -.-> BDD` | from=E, to=BDD, type=dotted |
| Liens pointillés + label | `E -.->│"Suivi"│ BDD` | from=E, to=BDD, label="Suivi", type=dotted |
| Styles | `style A fill:#4A90D9,color:#fff` | id=A, fill=#4A90D9, text_color=#fff |

**Ce qui est variabilisable ici :** tout le parsing. Un LLM peut très bien recevoir le Mermaid brut et produire un JSON structuré contenant la liste des nœuds et des liens. C'est d'ailleurs la meilleure approche pour n8n : faire parser le Mermaid par l'IA en amont du script Python.

### Format JSON intermédiaire suggéré

```json
{
  "title": "Processus de production de cartes PVC",
  "subtitle": "Flux détaillé avec contrôles qualité",
  "nodes": [
    {
      "id": "A",
      "label": "Réception du fichier client",
      "detail": null,
      "type": "box",
      "style": "start",
      "num": "1"
    },
    {
      "id": "C",
      "label": "Données conformes ?",
      "type": "diamond",
      "style": "default"
    },
    {
      "id": "BDD",
      "label": "Base de données interne",
      "detail": "lots terminés / en cours / en retard",
      "type": "cylinder",
      "style": "database"
    }
  ],
  "edges": [
    { "from": "A", "to": "B", "type": "solid", "label": null },
    { "from": "C", "to": "D", "type": "solid", "label": "Non" },
    { "from": "F1", "to": "BDD", "type": "dotted", "label": "Suivi temps réel" }
  ],
  "theme": {
    "accent": "#134D72",
    "success": "#2ECC71",
    "error": "#D34232",
    "warning": "#E99212",
    "background": "#F6F8FB",
    "text_dark": "#1E2837",
    "text_muted": "#647387",
    "border": "#D2DCE8",
    "font_title": "InstrumentSans-Bold",
    "font_label": "InstrumentSans-Bold",
    "font_body": "InstrumentSans-Regular",
    "font_mono": "GeistMono-Regular",
    "scale": 2
  }
}
```

---

## Étape 2 : Moteur de layout

C'est la partie la plus critique. Le layout détermine où chaque élément se place sur le canvas. Dans mon implémentation, le layout est **linéaire vertical** (adapté aux flowcharts top-down) avec des branches latérales.

### Logique de placement

Le flux principal occupe une colonne centrale (`MCX`). Les éléments secondaires se placent sur des colonnes latérales :

| Colonne | Contenu | Position X typique |
|---------|---------|-------------------|
| Gauche | Flux d'erreur / non-conformité | ~15% de la largeur |
| Centre | Flux principal | ~40% de la largeur |
| Droite (proche) | Branches conditionnelles (ex : embossage) | Centre + 200px |
| Droite (loin) | BDD / éléments de suivi | ~85% de la largeur |

Le placement vertical est séquentiel : chaque élément est dessiné, on récupère sa position basse (`bottom_y`), on ajoute un espacement (`connector_height`), et on dessine l'élément suivant.

**Variables de layout :**

```python
# Positions horizontales
MAIN_CENTER_X = 440  # colonne principale
ERROR_CENTER_X = 80  # colonne erreur
BRANCH_OFFSET = 200  # décalage pour branches conditionnelles

# Dimensions des éléments
BOX_WIDTH = 290
BOX_HEIGHT_MIN = 40
DIAMOND_SIZE = 46
CONNECTOR_HEIGHT = 22       # espacement standard
CONNECTOR_HEIGHT_SMALL = 15 # espacement compact (sous-étapes)

# Canvas
SCALE = 2        # facteur retina (2 = haute résolution)
CANVAS_WIDTH = 1100
CANVAS_HEIGHT = 2200  # sera croppé automatiquement
```

**Ce qui est variabilisable :** toutes ces valeurs. L'IA peut les ajuster selon la complexité du diagramme (nombre de nœuds, profondeur des branches). Un diagramme simple aura un canvas plus petit et des espacements plus grands ; un diagramme complexe compressera davantage.

---

## Étape 3 : Rendu Pillow

Pillow dessine chaque composant sur un canvas RGBA. Voici les primitives utilisées.

### 3.1 Boîtes (nœuds rectangulaires)

```python
from PIL import Image, ImageDraw, ImageFont

# Ombre portée légère
draw.rounded_rectangle(
    (x1+2, y1+2, x2+2, y2+2),
    radius=8, fill=(0, 0, 0, 10)
)

# Rectangle principal
draw.rounded_rectangle(
    (x1, y1, x2, y2),
    radius=8, fill=fill_color, outline=outline_color, width=1
)

# Badge numéro (cercle en haut à gauche)
draw.ellipse((bx, by, bx+20, by+20), fill=badge_color)

# Texte centré dans la boîte
draw.text((center_x - text_width//2, text_y), label, font=font, fill=text_color)
```

**Variabilisable :** `radius` (arrondi des coins), opacité de l'ombre, taille du badge, toutes les couleurs.

### 3.2 Losanges (décisions)

```python
# 4 points formant un losange
points = [
    (cx, top),           # sommet
    (cx + size, center), # droite
    (cx, bottom),        # bas
    (cx - size, center)  # gauche
]
draw.polygon(points, fill=WHITE, outline=ACCENT)
```

**Variabilisable :** `size` du losange, couleur de bordure, épaisseur du trait.

### 3.3 Connecteurs (flèches)

```python
# Ligne verticale
draw.line([(x, y1), (x, y2)], fill=color, width=1.5)

# Pointe de flèche (triangle)
arrow_size = 4
draw.polygon([
    (x, y2),
    (x - arrow_size, y2 - arrow_size * 1.3),
    (x + arrow_size, y2 - arrow_size * 1.3)
], fill=color)
```

Pour les lignes pointillées :

```python
x = start_x
while x < end_x:
    segment_end = min(x + 5, end_x)
    draw.line([(x, y), (segment_end, y)], fill=color, width=1.5)
    x += 9  # 5px trait + 4px espace
```

**Variabilisable :** épaisseur des traits, taille des flèches, espacement des pointillés, couleur par type de lien.

### 3.4 Tags de branche (OUI / NON)

```python
# Petit pill arrondi avec fond semi-transparent
draw.rounded_rectangle(
    (cx - tw//2 - 7, y, cx + tw//2 + 7, y + th + 4),
    radius=8, fill=(*color, 25)  # 25/255 d'opacité
)
draw.text((cx - tw//2, y + 2), "OUI", font=tag_font, fill=color)
```

### 3.5 Polices

Les polices sont des fichiers `.ttf` chargés via `ImageFont.truetype()`. Dans mon cas :

| Usage | Police | Taille (base) |
|-------|--------|--------------|
| Titre du diagramme | InstrumentSans Bold | 22px |
| Labels des boîtes | InstrumentSans Bold | 14px |
| Texte secondaire | InstrumentSans Regular | 13px |
| Détails techniques | GeistMono Regular | 10px |
| Numéros de badge | GeistMono Bold | 9px |
| Tags OUI/NON | GeistMono Bold | 9px |

**Variabilisable :** choix de police, tailles. Toute police Google Fonts au format TTF fonctionne. Il suffit de la télécharger dans le conteneur.

---

## Étape 4 : Export

```python
# Crop automatique pour supprimer l'espace vide en bas
cropped = img.crop((0, 0, width, final_y))

# Conversion RGBA -> RGB (PNG ne nécessite pas forcément l'alpha)
output = Image.new('RGB', cropped.size, background_color)
output.paste(cropped, mask=cropped.split()[3])

# Export
output.save("flowchart.png", "PNG", quality=95)
```

Le facteur `SCALE = 2` produit une image à résolution double (retina). Pour un canvas de 1100x2200, l'image finale fait 2200x4400px, soit du print-ready à 300 DPI sur environ 19x37 cm.

---

## Implémentation dans n8n

### Workflow suggéré

```
[Formulaire web]
  Champ : code Mermaid (textarea)
  Champ : couleur accent (color picker)
  Champ : style (select : minimal / corporate / coloré)
        │
        ▼
[Node Code / HTTP Request → API Claude]
  Prompt : "Parse ce Mermaid en JSON structuré selon ce schéma : {...}"
  L'IA renvoie le JSON intermédiaire (nœuds, liens, thème)
        │
        ▼
[Node Code (Python)]
  Reçoit le JSON
  Exécute le script Pillow
  Produit le PNG en base64 ou fichier temporaire
        │
        ▼
[Réponse / stockage]
  Renvoie le PNG au formulaire ou le stocke (S3, Drive, etc.)
```

### Prérequis techniques

| Composant | Détail |
|-----------|--------|
| Python 3.10+ | Environnement d'exécution |
| Pillow | `pip install Pillow` |
| Polices TTF | Télécharger les Google Fonts souhaitées |
| Mémoire | ~50 Mo pour un canvas 2200x4400 en RGBA |
| Temps d'exécution | < 2 secondes pour un flowchart de 20 nœuds |

### Ce que l'IA gère vs ce que le script gère

| Responsabilité | Géré par |
|---------------|----------|
| Parsing du Mermaid → JSON | IA (Claude / GPT) |
| Choix des couleurs selon le style demandé | IA |
| Choix des polices selon le ton | IA |
| Calcul du layout (positions x/y) | Script Python |
| Dessin des primitives graphiques | Script Python (Pillow) |
| Export PNG | Script Python |

### Variables que l'IA peut contrôler

```json
{
  "theme": {
    "accent": "#134D72",
    "success": "#2ECC71",
    "error": "#D34232",
    "warning": "#E99212",
    "background": "#F6F8FB",
    "card_background": "#FFFFFF",
    "text_dark": "#1E2837",
    "text_muted": "#647387",
    "border": "#D2DCE8",
    "shadow_opacity": 10,
    "corner_radius": 8,
    "connector_opacity": 80,
    "arrow_size": 4,
    "dotted_segment": 5,
    "dotted_gap": 4
  },
  "fonts": {
    "title": { "family": "InstrumentSans-Bold.ttf", "size": 22 },
    "label": { "family": "InstrumentSans-Bold.ttf", "size": 14 },
    "body": { "family": "InstrumentSans-Regular.ttf", "size": 13 },
    "mono": { "family": "GeistMono-Regular.ttf", "size": 10 },
    "badge": { "family": "GeistMono-Bold.ttf", "size": 9 },
    "tag": { "family": "GeistMono-Bold.ttf", "size": 9 }
  },
  "layout": {
    "scale": 2,
    "canvas_width": 1100,
    "main_column_x_percent": 0.40,
    "error_column_x_percent": 0.12,
    "branch_offset": 200,
    "connector_height": 22,
    "connector_height_small": 15,
    "box_width": 290,
    "box_min_height": 40,
    "diamond_size": 46
  }
}
```

---

## Limites et points d'attention

**Ce qui marche bien :** les flowcharts top-down linéaires avec branches (le cas d'usage le plus courant pour des processus métier).

**Ce qui nécessite du travail supplémentaire :** les diagrammes très ramifiés avec de nombreuses branches parallèles, les graphes cycliques complexes, les diagrammes de séquence ou de Gantt. Le layout linéaire ne couvre pas tous les types Mermaid.

**Alternative pour le parsing :** plutôt que de parser le Mermaid avec l'IA, on peut aussi utiliser la librairie JavaScript `mermaid` côté serveur pour extraire le graphe (nœuds + arêtes) via son API interne, puis passer ces données structurées au script Python. Ça évite les erreurs de parsing par l'IA sur des syntaxes Mermaid inhabituelles.

**Gestion de la hauteur :** le canvas est initialisé avec une hauteur généreuse puis croppé automatiquement. Pour des diagrammes très longs, prévoir un calcul préalable du nombre de nœuds pour dimensionner correctement.

---

## Fichiers de référence

Les deux scripts Python complets qui ont produit les flowcharts de cette session sont disponibles. Le second (`draw_fc3.py`) est le plus abouti et couvre : flux principal linéaire, branches conditionnelles, colonnes d'erreur, BDD avec pointillés, légende, badges numérotés, ombres portées, et export haute résolution.
