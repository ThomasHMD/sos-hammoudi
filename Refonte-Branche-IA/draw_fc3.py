#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont

S = 2
W = 1100 * S
H = 2200 * S

ACCENT = (19, 77, 114)
WHITE = (255, 255, 255)
BG = (246, 248, 251)
TEXT_DARK = (30, 40, 55)
TEXT_MUT = (100, 115, 135)
BORDER = (210, 220, 232)
GREEN = (46, 204, 113)
RED = (211, 66, 50)
ORANGE = (233, 146, 18)
CONN = (19, 77, 114, 80)
CONN_L = (19, 77, 114, 45)
RED_CONN = (211, 66, 50, 80)
DOT_C = (233, 146, 18, 120)

FD = "/mnt/skills/examples/canvas-design/canvas-fonts"
f_bold = ImageFont.truetype(f"{FD}/InstrumentSans-Bold.ttf", 14*S)
f_reg = ImageFont.truetype(f"{FD}/InstrumentSans-Regular.ttf", 13*S)
f_mono = ImageFont.truetype(f"{FD}/GeistMono-Regular.ttf", 10*S)
f_title = ImageFont.truetype(f"{FD}/InstrumentSans-Bold.ttf", 22*S)
f_sub = ImageFont.truetype(f"{FD}/GeistMono-Regular.ttf", 10*S)
f_num = ImageFont.truetype(f"{FD}/GeistMono-Bold.ttf", 9*S)
f_tag = ImageFont.truetype(f"{FD}/GeistMono-Bold.ttf", 9*S)
f_dia = ImageFont.truetype(f"{FD}/InstrumentSans-Bold.ttf", 13*S)
f_dia_sm = ImageFont.truetype(f"{FD}/InstrumentSans-Regular.ttf", 12*S)
f_bdd = ImageFont.truetype(f"{FD}/InstrumentSans-Bold.ttf", 12*S)
f_bdd_sm = ImageFont.truetype(f"{FD}/GeistMono-Regular.ttf", 9*S)
f_legend = ImageFont.truetype(f"{FD}/InstrumentSans-Regular.ttf", 11*S)

img = Image.new('RGBA', (W, H), BG)
d = ImageDraw.Draw(img, 'RGBA')

# Tighter layout: less wasted space on right
MCX = 440 * S
ERR_X = 80 * S
# BDD will be drawn as a column on right, connected properly

def tc(cx, cy, txt, fnt, col):
    bb = d.textbbox((0,0), txt, font=fnt)
    d.text((cx-(bb[2]-bb[0])//2, cy-(bb[3]-bb[1])//2), txt, fill=col, font=fnt)

def tc_top(cx, y, txt, fnt, col):
    bb = d.textbbox((0,0), txt, font=fnt)
    d.text((cx-(bb[2]-bb[0])//2, y), txt, fill=col, font=fnt)

def bx(cx, y, lines, style="n", w=290*S, num=None):
    th = 0
    heights = []
    for txt, fnt in lines:
        bb = d.textbbox((0,0), txt, font=fnt)
        h = bb[3]-bb[1]
        heights.append(h)
        th += h
    th += (len(lines)-1)*4*S
    bh = max(40*S, th+18*S)
    x1,y1,x2,y2 = cx-w//2, y, cx+w//2, y+bh

    colors = {"n":(WHITE,BORDER,TEXT_DARK), "s":(ACCENT,ACCENT,(255,255,255)),
              "e":(GREEN,GREEN,(255,255,255)), "r":(RED,RED,(255,255,255)),
              "o":(ORANGE,ORANGE,(255,255,255))}
    fc,oc,txc = colors.get(style, colors["n"])

    d.rounded_rectangle((x1+2*S,y1+2*S,x2+2*S,y2+2*S), radius=8*S, fill=(0,0,0,10))
    d.rounded_rectangle((x1,y1,x2,y2), radius=8*S, fill=fc, outline=oc, width=S)

    if num:
        bs=20*S; bx_=x1-4*S; by_=y1-4*S
        bcol = {"s":(WHITE,ACCENT),"e":(WHITE,GREEN),"r":(WHITE,RED)}.get(style,(ACCENT,WHITE))
        d.ellipse((bx_,by_,bx_+bs,by_+bs), fill=bcol[0])
        tc(bx_+bs//2, by_+bs//2, num, f_num, bcol[1])

    ty = y1 + (bh-th)//2
    for i,(txt,fnt) in enumerate(lines):
        c = txc if style != "n" else (TEXT_MUT if fnt==f_mono else TEXT_DARK)
        tc_top(cx, ty, txt, fnt, c)
        ty += heights[i]+4*S
    return y2

def dia(cx, y, l1, l2=None, sz=46*S):
    cy = y+sz
    pts = [(cx,y),(cx+sz,cy),(cx,cy+sz),(cx-sz,cy)]
    d.polygon([(p[0]+2*S,p[1]+2*S) for p in pts], fill=(0,0,0,8))
    d.polygon(pts, fill=WHITE, outline=ACCENT)
    for i in range(4):
        d.line([pts[i], pts[(i+1)%4]], fill=ACCENT, width=int(1.5*S))
    if l2:
        tc(cx, cy-8*S, l1, f_dia, ACCENT)
        tc(cx, cy+8*S, l2, f_dia_sm, ACCENT)
    else:
        tc(cx, cy, l1, f_dia, ACCENT)
    return cy, y+sz*2

def arr_d(x, y1, y2, c=CONN):
    d.line([(x,y1),(x,y2)], fill=c, width=int(1.5*S))
    a=4*S
    d.polygon([(x,y2),(x-a,y2-int(a*1.3)),(x+a,y2-int(a*1.3))], fill=c)

def ln_d(x, y1, y2, c=CONN):
    d.line([(x,y1),(x,y2)], fill=c, width=int(1.5*S))

def ln_h(x1, x2, y, c=CONN):
    d.line([(x1,y),(x2,y)], fill=c, width=int(1.5*S))

def arr_l(x1, x2, y, c=CONN):
    d.line([(x1,y),(x2,y)], fill=c, width=int(1.5*S))
    a=4*S
    d.polygon([(x2,y),(x2+int(a*1.3),y-a),(x2+int(a*1.3),y+a)], fill=c)

def dot_h(x1, x2, y, c=DOT_C):
    x=x1
    while x<x2:
        e=min(x+5*S,x2)
        d.line([(x,y),(e,y)], fill=c, width=int(1.5*S))
        x+=9*S

def tag(cx, y, txt, col):
    bb = d.textbbox((0,0), txt, font=f_tag)
    tw,th = bb[2]-bb[0], bb[3]-bb[1]
    px,py = 7*S, 2*S
    d.rounded_rectangle((cx-tw//2-px, y, cx+tw//2+px, y+th+py*2), radius=8*S, fill=(*col[:3], 25))
    d.text((cx-tw//2, y+py), txt, fill=col, font=f_tag)
    return y+th+py*2

# ========== TITLE ==========
y = 24*S
tc_top(MCX, y, "Processus de production de cartes PVC", f_title, ACCENT)
y += 30*S
tc_top(MCX, y, "FLUX DÉTAILLÉ AVEC CONTRÔLES QUALITÉ", f_sub, TEXT_MUT)
y += 18*S
lw=50*S
d.line([(MCX-lw,y),(MCX+lw,y)], fill=(*ACCENT,40), width=S)
y += 18*S

CH = 22*S
CHS = 15*S

bdd_pts = []
err_pts = []

# 1 Réception
b = bx(MCX, y, [("Réception du fichier client", f_bold)], "s", num="1")
arr_d(MCX, b, b+CH); y=b+CH

# 2 Contrôle intégrité
b = bx(MCX, y, [("Contrôle d'intégrité des données", f_bold)], num="2")
ctrl_top = y
arr_d(MCX, b, b+CH); y=b+CH

# Données conformes ?
dc_cy, dc_bot = dia(MCX, y, "Données", "conformes ?")

# NON -> signalement
sig_cx = ERR_X + 60*S
ln_h(MCX-46*S, sig_cx+115*S, dc_cy, CONN)
tag(sig_cx+130*S, dc_cy-14*S, "NON", RED)
sig_b = bx(sig_cx, dc_cy-22*S, [("Signalement anomalie", f_bold), ("+ correction", f_mono)], w=220*S)
# Loop back up
loop_y = ctrl_top - 14*S
d.line([(sig_cx, dc_cy-22*S), (sig_cx, loop_y)], fill=CONN_L, width=int(1.5*S))
d.line([(sig_cx, loop_y), (MCX, loop_y)], fill=CONN_L, width=int(1.5*S))
a=4*S
d.polygon([(MCX,loop_y),(MCX-a,loop_y-int(a*1.3)),(MCX+a,loop_y-int(a*1.3))], fill=CONN_L)

# OUI
tag(MCX+30*S, dc_bot+2*S, "OUI", ACCENT)
y=dc_bot+24*S; arr_d(MCX, dc_bot, y)

# 3 Création du lot
b = bx(MCX, y, [("Création du lot + fiche de production", f_bold)], num="3")
bdd_pts.append((MCX+145*S, (y+b)//2))
arr_d(MCX, b, b+CH); y=b+CH

# 4 Impression
b = bx(MCX, y, [("Impression cartes PVC", f_bold)], num="4")
arr_d(MCX, b, b+CHS); y=b+CHS

# Bipage 1
b = bx(MCX, y, [("Bipage opérateur", f_reg)], w=230*S)
bdd_pts.append((MCX+115*S, (y+b)//2))
arr_d(MCX, b, b+CHS); y=b+CHS

# Échantillonnage 1
b = bx(MCX, y, [("Échantillonnage : colorimétrie,", f_mono), ("netteté, centrage, défauts", f_mono)], w=280*S)
arr_d(MCX, b, b+CHS); y=b+CHS

# Conforme 1
c1cy, c1bot = dia(MCX, y, "Conforme ?")
err_pts.append(c1cy)
tag(MCX+30*S, c1bot+2*S, "OUI", ACCENT)
y=c1bot+24*S; arr_d(MCX, c1bot, y)

# 5 Mise sous presse
b = bx(MCX, y, [("Mise sous presse", f_bold), ("96 °C / 85 bar / 11 min", f_mono)], num="5")
arr_d(MCX, b, b+CHS); y=b+CHS

# Bipage 2
b = bx(MCX, y, [("Bipage opérateur", f_reg)], w=230*S)
bdd_pts.append((MCX+115*S, (y+b)//2))
arr_d(MCX, b, b+CHS); y=b+CHS

# Échantillonnage 2
b = bx(MCX, y, [("Échantillonnage : adhérence couches,", f_mono), ("découpe, déformation", f_mono)], w=290*S)
arr_d(MCX, b, b+CHS); y=b+CHS

# Conforme 2
c2cy, c2bot = dia(MCX, y, "Conforme ?")
err_pts.append(c2cy)
tag(MCX+30*S, c2bot+2*S, "OUI", ACCENT)
y=c2bot+24*S; arr_d(MCX, c2bot, y)

# Embossage requis ?
emb_cy, emb_bot = dia(MCX, y, "Embossage", "requis ?")
tag(MCX-62*S, emb_bot+2*S, "NON", TEXT_MUT)

# OUI -> embossage sub-flow to the right
emb_sub_cx = MCX + 200*S
ln_h(MCX+46*S, emb_sub_cx-100*S, emb_cy, CONN)
tag(MCX+75*S, emb_cy-14*S, "OUI", ACCENT)

ey = emb_cy-20*S
eb = bx(emb_sub_cx, ey, [("Embossage", f_bold)], num="6", w=210*S)
arr_d(emb_sub_cx, eb, eb+CHS); ey2=eb+CHS

eb2 = bx(emb_sub_cx, ey2, [("Bipage opérateur", f_reg)], w=210*S)
bdd_pts.append((emb_sub_cx+105*S, (ey2+eb2)//2))
arr_d(emb_sub_cx, eb2, eb2+CHS); ey3=eb2+CHS

eb3 = bx(emb_sub_cx, ey3, [("Contrôle : lisibilité,", f_mono), ("positionnement", f_mono)], w=210*S)
arr_d(emb_sub_cx, eb3, eb3+CHS); ey4=eb3+CHS

c3cy, c3bot = dia(emb_sub_cx, ey4, "Conforme ?")
err_pts.append(c3cy)
tag(emb_sub_cx+30*S, c3bot+2*S, "OUI", ACCENT)

# Merge
merge_y = max(emb_bot+45*S, c3bot+24*S)
arr_d(MCX, emb_bot, merge_y)
ln_d(emb_sub_cx, c3bot, merge_y, CONN)
ln_h(emb_sub_cx, MCX, merge_y, CONN)
dot_r=4*S
d.ellipse((MCX-dot_r,merge_y-dot_r,MCX+dot_r,merge_y+dot_r), fill=(*ACCENT,60))
y=merge_y; arr_d(MCX, y, y+CH); y+=CH

# 7 Encartage
b = bx(MCX, y, [("Encartage + mise sous pli", f_bold)], num="7")
arr_d(MCX, b, b+CHS); y=b+CHS

# Bipage 4
b = bx(MCX, y, [("Bipage opérateur", f_reg)], w=230*S)
bdd_pts.append((MCX+115*S, (y+b)//2))
arr_d(MCX, b, b+CHS); y=b+CHS

# Contrôle pli
b = bx(MCX, y, [("Contrôle pli complet : rapprochement", f_mono), ("carte/courrier, collage, pliage, enveloppe", f_mono)], w=320*S)
arr_d(MCX, b, b+CHS); y=b+CHS

# Conforme 4
c4cy, c4bot = dia(MCX, y, "Conforme ?")
err_pts.append(c4cy)
tag(MCX+30*S, c4bot+2*S, "OUI", ACCENT)
y=c4bot+24*S; arr_d(MCX, c4bot, y)

# 8 Affranchissement
b = bx(MCX, y, [("Affranchissement", f_bold)], num="8")
arr_d(MCX, b, b+CHS); y=b+CHS

# Contrôle tarif
b = bx(MCX, y, [("Contrôle : tarif, format, intégrité", f_mono)], w=280*S)
arr_d(MCX, b, b+CH); y=b+CH

# 9 Remise postale
b = bx(MCX, y, [("Remise postale", f_bold)], "e", num="9")
main_bot = b

# ========== ERROR TRACK ==========
err_line_x = ERR_X + 70*S
err_top = min(err_pts)-5*S
err_bottom_line = max(err_pts)+5*S
d.line([(err_line_x, err_top),(err_line_x, err_bottom_line)], fill=(*RED,35), width=int(1.5*S))

for ecy in err_pts:
    dia_left = MCX - 46*S
    if ecy == c3cy:
        dia_left = emb_sub_cx - 46*S
        arr_l(dia_left, err_line_x, ecy, RED_CONN)
        tag(emb_sub_cx-85*S, ecy-14*S, "NON", RED)
    else:
        arr_l(dia_left, err_line_x, ecy, RED_CONN)
        tag(dia_left-32*S, ecy-14*S, "NON", RED)

ey = err_bottom_line+10*S
arr_d(err_line_x, err_bottom_line, ey, RED_CONN)

err_w = 230*S
eb = bx(err_line_x, ey, [("Isolement du lot", f_bold), ("+ analyse de cause", f_mono)], "r", w=err_w, num="E1")
arr_d(err_line_x, eb, eb+CHS, RED_CONN); ey=eb+CHS
eb = bx(err_line_x, ey, [("Identification opérateur", f_bold), ("(traçabilité fiche de production)", f_mono)], "r", w=err_w, num="E2")
arr_d(err_line_x, eb, eb+CHS, RED_CONN); ey=eb+CHS
eb = bx(err_line_x, ey, [("Diagnostic : matière / machine /", f_mono), ("humain / données", f_mono)], "r", w=err_w, num="E3")
arr_d(err_line_x, eb, eb+CHS, RED_CONN); ey=eb+CHS
eb = bx(err_line_x, ey, [("Action corrective : consignes /", f_mono), ("recalibrage / reformation", f_mono)], "r", w=err_w, num="E4")
arr_d(err_line_x, eb, eb+CHS, RED_CONN); ey=eb+CHS
eb = bx(err_line_x, ey, [("Reprise du lot", f_bold)], "r", w=190*S, num="E5")
err_final_bot = eb

# ========== BDD PANEL ==========
# Position BDD so that the dotted lines actually reach it
# BDD x = rightmost bipage connection + some padding
bdd_right_edge = W - 30*S
bdd_w = 200*S
BDD_CX = bdd_right_edge - bdd_w//2
bdd_x1 = BDD_CX - bdd_w//2

# Center BDD vertically among its connection points
bdd_avg_y = sum(py for _,py in bdd_pts) // len(bdd_pts)
bdd_h = 90*S
bdd_y1 = bdd_avg_y - bdd_h//2

# Draw BDD box
d.rounded_rectangle((bdd_x1+2*S, bdd_y1+2*S, bdd_x1+bdd_w+2*S, bdd_y1+bdd_h+2*S), radius=8*S, fill=(0,0,0,10))
d.rounded_rectangle((bdd_x1, bdd_y1, bdd_x1+bdd_w, bdd_y1+bdd_h), radius=8*S, fill=ORANGE, outline=ORANGE, width=S)
cyl_eh=12*S
d.ellipse((bdd_x1, bdd_y1-cyl_eh//2, bdd_x1+bdd_w, bdd_y1+cyl_eh), fill=(253,176,48), outline=ORANGE)

tc(BDD_CX, bdd_avg_y-14*S, "Base de données interne", f_bdd, WHITE)
tc(BDD_CX, bdd_avg_y+4*S, "lots terminés / en cours", f_bdd_sm, (255,255,255,210))
tc(BDD_CX, bdd_avg_y+18*S, "/ en retard", f_bdd_sm, (255,255,255,210))

tc_top(BDD_CX, bdd_y1-20*S, "Suivi temps réel", f_sub, ORANGE)

# Draw dotted lines from bipage connection points TO the BDD left edge
for px, py in bdd_pts:
    dot_h(px, bdd_x1, py, DOT_C)

# ========== LEGEND ==========
ly = max(main_bot, err_final_bot) + 28*S
lx = 40*S
tc_top(lx+80*S, ly, "LÉGENDE", f_sub, TEXT_MUT)
ly += 20*S

legend_items = [
    (ACCENT, "Début"),
    (GREEN, "Fin"),
    (RED, "Non-conformité"),
    (ORANGE, "Base de données"),
    (WHITE, "Étape standard"),
]
for i, (col, lbl) in enumerate(legend_items):
    ix = lx + i*155*S
    iy = ly
    ol = BORDER if col==WHITE else col
    d.rounded_rectangle((ix,iy,ix+14*S,iy+14*S), radius=3*S, fill=col, outline=ol, width=S)
    d.text((ix+20*S, iy), lbl, fill=TEXT_DARK, font=f_legend)

final_y = ly + 44*S

# Crop & save
cropped = img.crop((0, 0, W, min(final_y, H)))
out = Image.new('RGB', cropped.size, BG)
out.paste(cropped, mask=cropped.split()[3])
out.save("/home/claude/flowchart2.png", "PNG", quality=95)
print(f"Done: {out.size}")
