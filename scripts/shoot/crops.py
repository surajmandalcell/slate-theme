#!/usr/bin/env python3
"""Cut crops out of one workspace capture (used by scripts/shoot.sh).

crops.py CAPTURE.png WINLOG TOOLKIT MODE OUTDIR [BOUNDS.json | menu|popover|tooltip|dialog]

WINLOG holds the SLATE_WIN lines of this capture (see place.js). With BOUNDS.json:
window-<tk>-<mode>.png plus one crop per widget id. With a surface name: that
popup or dialog, cut from the compositor geometry of the last such window.
Bounds units: gtk logical px (capture is x2), qt device px (already x2).
"""
import json
import subprocess
import sys

PAD = 5             # logical px around every crop (12 would cut neighbours' captions in half)
SHADOW = 56         # logical px around the whole-window crop
SCALE = 2           # capture pixels per logical px
W, H = 2400 * SCALE, 1500 * SCALE   # keep in sync with shoot.sh and place.js

cap, winlog, tk, mode, outdir, what = sys.argv[1:7]

wins = []
for line in open(winlog):
    if "SLATE_WIN|" in line:
        p = line.split("SLATE_WIN|", 1)[1].strip().split("|")
        n = [int(v) for v in p[4].split()]
        wins.append({"cls": p[0], "popup": p[2] == "1", "dialog": p[3] == "1", "frame": n[:4], "client": n[4:]})
tops = [w for w in wins if not w["popup"] and not w["dialog"] and w["cls"] != "org.slate.Bg"]
if not tops:
    sys.exit("no top-level window in " + winlog)


def crop(name, x, y, w, h):
    """x y w h in capture pixels, clamped to the screen."""
    x0, y0 = max(0, round(x)), max(0, round(y))
    x1, y1 = min(W, round(x + w)), min(H, round(y + h))
    subprocess.run(["magick", cap, "-crop", f"{x1 - x0}x{y1 - y0}+{x0}+{y0}", "+repage",
                    f"{outdir}/{name}-{tk}-{mode}.png"], check=True)


if what.endswith(".json"):
    fx, fy, fw, fh = tops[-1]["frame"]
    cx, cy = tops[-1]["client"][:2]
    crop("window", (fx - SHADOW) * SCALE, (fy - SHADOW) * SCALE, (fw + 2 * SHADOW) * SCALE, (fh + 2 * SHADOW) * SCALE)
    f = 1 if tk == "qt" else SCALE
    for wid, (x, y, w, h) in json.load(open(what)).items():
        if wid not in ("window", "menu", "popover", "tooltip", "dialog"):
            crop(wid, cx * SCALE + x * f - PAD * SCALE, cy * SCALE + y * f - PAD * SCALE,
                 w * f + 2 * PAD * SCALE, h * f + 2 * PAD * SCALE)
else:
    # the last popup opened; a dialog is a top-level (Qt) or transient window (GTK) that is not the main one
    if what == "dialog":
        sel = [w for w in wins if w["dialog"] or (not w["popup"] and w["cls"] != "org.slate.Bg" and w["frame"] != tops[0]["frame"])]
    else:
        sel = [w for w in wins if w["popup"]]
    if sel:
        x, y, w, h = sel[-1]["frame"]
        crop(what, (x - PAD) * SCALE, (y - PAD) * SCALE, (w + 2 * PAD) * SCALE, (h + 2 * PAD) * SCALE)
    else:
        # surface drawn inside the main window (GTK3 popovers) or not seen by the compositor (Qt menus):
        # fall back to the rect the app wrote in its bounds file
        b = json.load(open(sys.argv[7])) if len(sys.argv) > 7 else {}
        if what not in b:
            sys.exit(f"no {what} window or bounds in {winlog}")
        x, y, w, h = b[what]
        f = 1 if tk == "qt" else SCALE
        cx, cy = tops[0]["client"][:2]
        crop(what, cx * SCALE + x * f - PAD * SCALE, cy * SCALE + y * f - PAD * SCALE,
             w * f + 2 * PAD * SCALE, h * f + 2 * PAD * SCALE)
