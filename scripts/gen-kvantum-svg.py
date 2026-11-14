#!/usr/bin/env python3
"""Generate kde/kvantum/__NAME__/__NAME__.svg.in: the Kvantum nine-slice sheet.

Geometry (corner radii, track and thumb sizes, check and knob size) comes from tokens.json; colors stay
{{token}} placeholders that build.py fills per theme. Qt SVG has no rgba(), so alpha tokens are written as
rgb({{x|rgb}}) plus {{x|alpha}}. Usage: gen-kvantum-svg.py [out-file]   (default: the .svg.in in the repo).
Kvantum scales every corner tile into the widget's frame size, so the tile size must equal the kvconfig frame.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "kde/kvantum/__NAME__/__NAME__.svg.in"
TOK = json.loads((ROOT / "tokens.json").read_text())["common"]


def px(name):
    return int(TOK[name].removesuffix("px"))


R_CTL = px("radius_control")        # button, tbutton, lineedit, tabbar, tabframe, group, common, dock, tooltip
R_ITEM = px("radius_menu_item")     # menu item, menu-bar item, item view
R_INNER = px("radius_inner")        # tab segment, scrollbar thumb pill
R_MENU = R_CTL                      # Kvantum scales the menu tile into the menu frame (= radius_control), not radius_popover
R_BAR = px("progress_height") // 2  # progress bar pill
R_TRACK = px("slider_track") // 2   # slider groove pill
THUMB = px("scrollbar_thumb_hover")
MARGIN = px("scrollbar_margin")
SB_TILE = THUMB // 2 + MARGIN       # scrollbar tile: thumb radius + margin
CHECK = px("check_size")
KNOB = px("slider_knob")
TAB_INSET = (px("control_height") - px("control_height_sm")) // 2  # segment inset inside the 24 px track
TAB_TILE = R_INNER + TAB_INSET
MENU_SHADOW = 12  # kvconfig menu_shadow_depth
TIP_SHADOW = 8    # kvconfig tooltip_shadow_depth
TIP_FRAME = px("spacing_xs")  # kvconfig [ToolTip] frame
W = 640
M = 4  # stretchable middle size of every nine-slice
items = []
cur = {"x": 8, "y": 8, "rowh": 0}


def num(x):
    return str(int(x)) if float(x) == int(x) else str(x)


def t(name):
    return "{{%s}}" % name


def rgbc(tok):
    return "rgb({{%s|rgb}})" % tok


def place(w, h, body):
    if cur["x"] + w > W:
        cur["x"], cur["y"], cur["rowh"] = 8, cur["y"] + cur["rowh"] + 8, 0
    items.append(body(cur["x"], cur["y"]))
    cur["x"] += w + 8
    cur["rowh"] = max(cur["rowh"], h)


def pieces(R, bw, i):
    """Pieces for corner tile R, border width bw, transparent pill inset i. part -> (w, h, fill path, border path)."""
    Ro, r = R - i, R - i - bw
    P = {}
    P["topleft"] = (R, R, f"M{i} {R}A{Ro} {Ro} 0 0 1 {R} {i}V{R}Z", f"M{i} {R}A{Ro} {Ro} 0 0 1 {R} {i}V{i+bw}A{r} {r} 0 0 0 {i+bw} {R}Z")
    P["topright"] = (R, R, f"M0 {i}A{Ro} {Ro} 0 0 1 {Ro} {R}H0Z", f"M0 {i}A{Ro} {Ro} 0 0 1 {Ro} {R}H{r}A{r} {r} 0 0 0 0 {i+bw}Z")
    P["bottomleft"] = (R, R, f"M{i} 0A{Ro} {Ro} 0 0 0 {R} {Ro}V0Z", f"M{i} 0A{Ro} {Ro} 0 0 0 {R} {Ro}V{r}A{r} {r} 0 0 1 {i+bw} 0Z")
    P["bottomright"] = (R, R, f"M{Ro} 0A{Ro} {Ro} 0 0 1 0 {Ro}V0Z", f"M{Ro} 0A{Ro} {Ro} 0 0 1 0 {Ro}V{r}A{r} {r} 0 0 0 {r} 0Z")
    P["top"] = (M, R, f"M0 {i}H{M}V{R}H0Z", f"M0 {i}H{M}V{i+bw}H0Z")
    P["bottom"] = (M, R, f"M0 0H{M}V{Ro}H0Z", f"M0 {Ro-bw}H{M}V{Ro}H0Z")
    P["left"] = (R, M, f"M{i} 0H{R}V{M}H{i}Z", f"M{i} 0H{i+bw}V{M}H{i}Z")
    P["right"] = (R, M, f"M0 0H{Ro}V{M}H0Z", f"M{Ro-bw} 0H{Ro}V{M}H{Ro-bw}Z")
    return P


def pos(R, part):
    return {"topleft": (0, 0), "top": (R, 0), "topright": (R + M, 0), "left": (0, R), "right": (R + M, R),
            "bottomleft": (0, R + M), "bottom": (R, R + M), "bottomright": (R + M, R + M)}[part]


def frame(elem, R, fill, border, bw=1, op=None, interior=True, inset=0, shade=False, marker=False):
    """One state of a nine-slice element: 8 pieces + interior, laid out assembled on the sheet.
    shade darkens the bottom border row (button shadow inside the tile). marker adds the empty
    `expand-<elem>` element Kvantum looks for when frame.expansion is used."""
    P = pieces(R, bw, inset)
    cw = 2 * R + M
    opa = f' opacity="{op}"' if op else ""
    fl = f'fill="{fill}"'
    bl = f'fill="{border}"'

    def body(x, y):
        out = []
        for part, (w, h, fp, bp) in P.items():
            px_, py_ = pos(R, part)
            g = f'<g id="{elem}-{part}" transform="translate({x+px_},{y+py_})"{opa}>'
            if inset:
                g += f'<rect width="{w}" height="{h}" opacity="0"/>'
            g += f'<path d="{fp}" {fl}/>'
            if border != "none":
                g += f'<path d="{bp}" {bl}/>'
            if shade and part == "bottom":
                g += f'<path d="M0 {R-bw}H{M}V{R}H0Z" fill="#000" fill-opacity="0.10"/>'
            out.append(g + "</g>")
        if interior:
            out.append(f'<rect id="{elem}" x="{x+R}" y="{y+R}" width="{M}" height="{M}" {fl}{opa}/>')
        if marker:
            out.append(f'<rect id="expand-{elem}" x="{x}" y="{y}" width="1" height="1" opacity="0"/>')
        return "\n".join(out)

    place(cw, cw, body)


def raw(w, h, text):
    place(w, h, lambda x, y: f'<g transform="translate({x},{y})">{text}</g>')


def glyph(eid, w, h, inner):
    raw(w, h, f'<g id="{eid}"><rect width="{w}" height="{h}" opacity="0"/>{inner}</g>')


def chev(d, col, sw=1.4):
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'


# ---------------- frames ----------------
# push button: the shadow lives inside the tile (darker bottom row)
for st, f, b in [("normal", "button_bg", "border_hex"), ("focused", "button_bg_hover", "border_hex"),
                 ("pressed", "button_bg_active", "border_hex"), ("toggled", "button_bg_active", "border_hex")]:
    frame(f"button-{st}", R_CTL, t(f), t(b), shade=True, marker=(st == "normal"))
# default button: accent_soft tint over the normal button (Kvantum cannot color default-button text)
frame("button-default", R_CTL, rgbc("accent") + f'" fill-opacity="{t("accent_soft|alpha")}', t("accent"), marker=True)

# flat toolbar button: 24 x 24 icon button = frame 4 + expansion 12 (corner tile R_CTL)
frame("tbutton-normal", R_CTL, "none", "none", marker=True)
frame("tbutton-focused", R_CTL, rgbc("flat_hover"), "none", op=t("flat_hover|alpha"))
frame("tbutton-pressed", R_CTL, rgbc("flat_active"), "none", op=t("flat_active|alpha"))
frame("tbutton-toggled", R_CTL, rgbc("flat_active"), "none", op=t("flat_active|alpha"))

# line edit
frame("lineedit-normal", R_CTL, t("entry_bg"), t("border_hex"), marker=True)
frame("lineedit-focused", R_CTL, t("entry_bg"), t("accent"), bw=2)

# segmented tabs: 24 px tile height, the 20 px segment (radius_inner) is inset 2 px; the track comes from tabbar
frame("tab-normal", TAB_TILE, "none", "none", marker=True, inset=TAB_INSET)
frame("tab-focused", TAB_TILE, t("button_bg_active"), "none", inset=TAB_INSET)
frame("tab-toggled", TAB_TILE, t("accent"), "none", inset=TAB_INSET)
frame("tab-pressed", TAB_TILE, t("accent_active"), "none", inset=TAB_INSET)
frame("tabbar-normal", R_CTL, t("switch_off"), t("switch_off"), marker=True)
frame("tabframe-normal", R_CTL, t("view_bg"), t("border_hex"))

# group box, generic frame, dock
frame("group-normal", R_CTL, t("sidebar_bg"), t("border_hex"))
frame("common-normal", R_CTL, "none", t("border_hex"))
frame("common-focused", R_CTL, "none", t("accent"), bw=2)
frame("dock-normal", R_CTL, t("window_bg"), t("border_hex"))

# menu, menu items, tooltip
frame("menu-normal", R_MENU, t("menu_bg"), t("border_hex"))
frame("menuitem-normal", R_ITEM, "none", "none", marker=True)
for st in ("focused", "pressed", "toggled"):
    frame(f"menuitem-{st}", R_ITEM, t("accent"), t("accent"))
    frame(f"menubaritem-{st}", R_ITEM, t("accent"), t("accent"))
frame("menubaritem-normal", R_ITEM, "none", "none", marker=True)
frame("tooltip-normal", R_CTL, t("tooltip_bg"), t("border_hex"), marker=True)

# item views
frame("itemview-normal", R_ITEM, "none", "none", marker=True)
frame("itemview-focused", R_ITEM, rgbc("flat_hover"), "none", op=t("flat_hover|alpha"))
frame("itemview-pressed", R_ITEM, t("accent"), t("accent"))
frame("itemview-toggled", R_ITEM, t("accent"), t("accent"))
frame("itemview-toggled-inactive", R_ITEM, t("selection_bg_backdrop"), t("selection_bg_backdrop"))

# progress bar and slider groove (pills)
frame("progress-normal", R_BAR, t("switch_off"), "none")
frame("progress-pattern-normal", R_BAR, t("accent"), "none")
frame("progress-pattern-disabled", R_BAR, t("fg_disabled"), "none")
frame("slider-normal", R_TRACK, t("switch_off"), "none")
frame("slider-toggled", R_TRACK, t("accent"), "none")

# scrollbars: tile = thumb radius + margin, pill inset by the margin
frame("scrollbargroove-normal", R_INNER, "none", "none")
for st, col, tok in (("normal", rgbc("scrollbar"), t("scrollbar|alpha")), ("focused", t("fg_backdrop"), None),
                     ("pressed", t("fg_secondary"), None), ("toggled", t("fg_secondary"), None)):
    frame(f"scrollbarslider-{st}", SB_TILE, col, "none", op=tok, inset=MARGIN)
    frame(f"ss-{st}", SB_TILE, col, "none", op=tok, interior=False, inset=MARGIN)



def shadow_frame(elem, f, d):
    """`<elem>-shadow-*` tiles for composited popups: tile = frame f + shadow depth d. The body border sits at
    offset d, soft shadow rings fall off outside it (1 px rings, quadratic fade, strength = accent_soft alpha as
    the per-mode shadow strength). Corners and edges are mirrored copies of one top-left corner and one top edge.
    The `-shadow-hint-*` elements tell Kvantum how thick the visible shadow is (d of the tile)."""
    P = f + d
    A = 0.5

    def rings(corner):
        sh, bd = [], ""
        for k in range(1, d + 1):
            a = round(A * (1 - (k - 1) / d) ** 2, 3)
            if corner:
                R = f + k
                p = f"M{d-k} {P}A{R} {R} 0 0 1 {P} {d-k}V{d-k+1}A{R-1} {R-1} 0 0 0 {d-k+1} {P}Z"
            else:
                p = f"M0 {d-k}H{M}V{d-k+1}H0Z"
            sh.append(f'<path d="{p}" fill="#000" fill-opacity="{a}"/>')
        if corner:
            bd = f'<path d="M{d} {P}A{f} {f} 0 0 1 {P} {d}V{d+1}A{f-1} {f-1} 0 0 0 {d+1} {P}Z" fill="{t("border_hex")}"/>'
        else:
            bd = f'<path d="M0 {d}H{M}V{d+1}H0Z" fill="{t("border_hex")}"/>'
        w, h = (P, P) if corner else (M, P)
        return f'<rect width="{w}" height="{h}" opacity="0"/><g opacity="{t("accent_soft|alpha")}">{"".join(sh)}</g>{bd}'

    corner, edge = rings(True), rings(False)
    # part -> (content, matrix a b c d e f placed at the cell origin), cell = 2P + M square
    S = 2 * P + M
    parts = {
        "topleft": (corner, (1, 0, 0, 1, 0, 0)), "topright": (corner, (-1, 0, 0, 1, S, 0)),
        "bottomleft": (corner, (1, 0, 0, -1, 0, S)), "bottomright": (corner, (-1, 0, 0, -1, S, S)),
        "top": (edge, (1, 0, 0, 1, P, 0)), "bottom": (edge, (1, 0, 0, -1, P, S)),
        "left": (edge, (0, 1, 1, 0, 0, P)), "right": (edge, (0, 1, -1, 0, S, P)),
    }

    def body(x, y):
        out = []
        for part, (content, (a, b, c, dd, e, ff)) in parts.items():
            out.append(f'<g id="{elem}-shadow-{part}" transform="matrix({a},{b},{c},{dd},{x+e},{y+ff})">{content}</g>')
        for side, (w, h) in {"left": (d, M), "right": (d, M), "top": (M, d), "bottom": (M, d)}.items():
            out.append(f'<rect id="{elem}-shadow-hint-{side}" x="{x}" y="{y}" width="{w}" height="{h}" opacity="0"/>')
        return "\n".join(out)

    place(S, S, body)


shadow_frame("menu", R_MENU, MENU_SHADOW)
shadow_frame("tooltip", TIP_FRAME, TIP_SHADOW)

# ---------------- interior-only and glyph elements ----------------
D = {"up": "M2 5.75L4.5 3.25L7 5.75", "down": "M2 3.25L4.5 5.75L7 3.25",
     "right": "M3.25 2L5.75 4.5L3.25 7", "left": "M5.75 2L3.25 4.5L5.75 7"}
for dn, d in D.items():
    for st, c in (("normal", "fg"), ("pressed", "fg"), ("disabled", "fg_disabled")):
        glyph(f"arrow-{dn}-{st}", 9, 9, chev(d, t(c)))
for dn in ("right", "left"):
    glyph(f"menuitem-{dn}-normal", 9, 9, chev(D[dn], t("fg")))
    glyph(f"menuitem-{dn}-focused", 9, 9, chev(D[dn], t("accent_fg")))
dbl = "M2 3.4L4.5 1.1L7 3.4M2 5.6L4.5 7.9L7 5.6"
for st, c in (("normal", "fg"), ("pressed", "fg"), ("disabled", "fg_disabled")):
    glyph(f"combo-arrow-down-{st}", 9, 9, chev(dbl, t(c), 1.3))
for st in ("normal", "pressed"):  # tree expander glyphs
    glyph(f"arrow-minus-{st}", 9, 9, chev("M2 4.5H7", t("fg")))
    glyph(f"arrow-plus-{st}", 9, 9, chev("M2 4.5H7M4.5 2V7", t("fg")))
raw(4, 1, f'<rect id="slider-tick-normal" width="4" height="1" fill="{t("fg_disabled")}"/>')

glyph("button-default-indicator", 4, 4, "")
glyph("toolbar-handle", 5, 8, "")
for gname in ("grip", "splitter-grip", "resize-grip"):  # empty, so Kvantum's default-theme grips never show
    for st in ("normal", "focused", "pressed"):
        glyph(f"{gname}-{st}", 8, 8, "")
raw(1, 16, f'<rect id="header-separator" width="1" height="16" fill="{t("separator_hex")}"/>')
for st, f, o in (("normal", "none", None), ("focused", rgbc("flat_hover"), t("flat_hover|alpha")),
                 ("pressed", rgbc("flat_active"), t("flat_active|alpha")), ("toggled", rgbc("flat_active"), t("flat_active|alpha"))):
    oa = f' opacity="{o}"' if o else ""
    raw(16, 16, f'<rect id="header-{st}" width="16" height="16" fill="{f}"{oa}/>')
raw(16, 16, f'<rect id="toolbar-normal" width="16" height="16" fill="{t("headerbar_bg")}"/>')
raw(16, 16, f'<rect id="menubar-normal" width="16" height="16" fill="{t("headerbar_bg")}"/>')
raw(16, 16, f'<rect id="titlebar-normal" width="16" height="16" fill="{t("headerbar_bg_backdrop")}"/>')
raw(16, 16, f'<rect id="titlebar-focused" width="16" height="16" fill="{t("headerbar_bg")}"/>')

# checkbox / radio at check_size (check and dash glyph paths are drawn for 16)
rc = t("radius_check|px")
c2 = num(CHECK / 2)
for st, ring, fillc in (("normal", "border_hex", "entry_bg"), ("focused", "accent", "entry_bg")):
    sw = 1 if st == "normal" else 1.5
    o = sw / 2
    d = CHECK - sw
    raw(CHECK, CHECK, f'<g id="checkbox-{st}"><rect width="{CHECK}" height="{CHECK}" opacity="0"/><rect x="{num(o)}" y="{num(o)}" width="{num(d)}" height="{num(d)}" rx="{rc}" fill="{t(fillc)}" stroke="{t(ring)}" stroke-width="{num(sw)}"/></g>')
    for kind, mark in (("checked", chev("M4.2 8.3L6.9 11L11.8 5.2", t("accent_fg"), 1.9)), ("tristate", chev("M4 8H12", t("accent_fg"), 1.9))):
        fcol = "accent" if st == "normal" else "accent_hover"
        raw(CHECK, CHECK, f'<g id="checkbox-{kind}-{st}"><rect width="{CHECK}" height="{CHECK}" fill="{t(fcol)}" rx="{rc}"/>{mark}</g>')
    raw(CHECK, CHECK, f'<g id="radio-{st}"><rect width="{CHECK}" height="{CHECK}" opacity="0"/><circle cx="{c2}" cy="{c2}" r="{num(CHECK/2-o)}" fill="{t(fillc)}" stroke="{t(ring)}" stroke-width="{num(sw)}"/></g>')
    fcol = "accent" if st == "normal" else "accent_hover"
    raw(CHECK, CHECK, f'<g id="radio-checked-{st}"><rect width="{CHECK}" height="{CHECK}" opacity="0"/><circle cx="{c2}" cy="{c2}" r="{c2}" fill="{t(fcol)}"/><circle cx="{c2}" cy="{c2}" r="3" fill="{t("accent_fg")}"/></g>')

# slider knob: total size = slider_knob (r = half - 0.25, plus a 0.5 stroke)
k2 = num(KNOB / 2)
for st, o in (("normal", None), ("focused", None), ("pressed", None), ("toggled", None), ("disabled", 0.55)):
    oa = f' opacity="{o}"' if o else ""
    raw(KNOB, KNOB, f'<g id="slidercursor-{st}"{oa}><rect width="{KNOB}" height="{KNOB}" opacity="0"/><circle cx="{k2}" cy="{num(KNOB/2+0.7)}" r="{num(KNOB/2-0.7)}" fill="#000" fill-opacity="0.18"/><circle cx="{k2}" cy="{k2}" r="{num(KNOB/2-0.25)}" fill="{t("switch_knob_color")}" stroke="{t("border_hex")}" stroke-width="0.5"/></g>')

height = cur["y"] + cur["rowh"] + 8
head = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.0" width="{W}" height="{height}">\n'
        '<!-- Slate Kvantum sheet, GENERATED by scripts/gen-kvantum-svg.py from tokens.json: do not edit by hand. '
        f'Corner radii in the paths: {R_CTL} = radius_control (button, tbutton, lineedit, tabbar, tabframe, group, common, dock, tooltip, menu), '
        f'{R_ITEM} = radius_menu_item (menuitem, menubaritem, itemview), {R_INNER} = radius_inner (tab segment), '
        f'{R_BAR} = progress_height / 2, {R_TRACK} = slider_track / 2. The menu uses radius_control because Kvantum scales the menu tile into the menu frame. '
        f'Scrollbar tiles are {SB_TILE} with a {MARGIN} px inset = scrollbar_margin (thumb {THUMB} = scrollbar_thumb_hover). '
        f'Check and knob are drawn at check_size ({CHECK}) and slider_knob ({KNOB}); checkbox rx is the radius_check token. '
        'Each assembled widget = 8 frame pieces + interior; expand-* are empty markers for Kvantum frame.expansion. -->\n'
        '<!-- Opacity of flat_hover, flat_active, scrollbar and accent_soft comes from the alpha token filter. '
        'Default button: Kvantum cannot color default-button text, so it is an accent tint over the normal button. -->\n'
        f'<rect width="{W}" height="{height}" fill="{t("window_bg")}"/>\n')
OUT.write_text(head + "\n".join(items) + "\n</svg>\n")
print("wrote", OUT, len(items), "cells", height)
