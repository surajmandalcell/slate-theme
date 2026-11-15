#!/usr/bin/env python3
"""Render gtk/ and kde/ into dist/Slate-Light and dist/Slate-Dark from tokens.json.

Files ending in `.in` are templates: `{{key}}` becomes the token value, and
`{{key|rgb}}` becomes "r,g,b" (for KDE .colors files), `{{key|alpha}}` the
alpha of an rgba() value (1 for hex), `{{key|px}}` the number without px. `__NAME__` in a path
becomes the theme name. Other files are copied as they are.
"""
import json, os, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOKEN = re.compile(r"\{\{\s*([a-z0-9_]+)(?:\|([a-z]+))?\s*\}\}")


def rgb(value):
    if value.startswith("#") and len(value) == 7:
        return ",".join(str(int(value[i:i + 2], 16)) for i in (1, 3, 5))
    m = re.match(r"rgba?\(([^)]*)\)", value)
    if m:
        return ",".join(p.strip() for p in m.group(1).split(",")[:3])
    raise ValueError(f"cannot convert {value!r} to rgb")


def alpha(value):
    m = re.match(r"rgba\(([^)]*)\)", value)
    return m.group(1).split(",")[3].strip() if m else "1"


FILTERS = {"rgb": rgb, "alpha": alpha, "px": lambda v: v.removesuffix("px")}


def render(text, tokens, where):
    def sub(m):
        key, flt = m.group(1), m.group(2)
        if key not in tokens:
            sys.exit(f"{where}: unknown token {key!r}")
        value = tokens[key]
        return FILTERS[flt](value) if flt else value
    return TOKEN.sub(sub, text)


def build():
    data = json.loads((ROOT / "tokens.json").read_text())
    dist = Path(os.environ.get("SLATE_DIST") or ROOT / "dist")  # scripts/pixdiff.sh builds into its own copy
    shutil.rmtree(dist, ignore_errors=True)
    # gtk/ renders to the theme root (gtk-3.0, gtk-4.0, index.theme); kde/ to kde/.
    sources = [(ROOT / "gtk", ""), (ROOT / "kde", "kde/")]
    for mode in ("light", "dark"):
        tokens = {**data["common"], **data[mode]}
        out_root = dist / tokens["name"]
        files = [(f, src, prefix) for src, prefix in sources for f in sorted(src.rglob("*")) if f.is_file()]
        for f, src, prefix in files:
            rel = prefix + str(f.relative_to(src)).replace("__NAME__", tokens["name"])
            out = out_root / rel.removesuffix(".in")
            out.parent.mkdir(parents=True, exist_ok=True)
            if f.suffix == ".in":
                out.write_text(render(f.read_text(), tokens, f))
            else:
                shutil.copy2(f, out)
        print(f"built {out_root.relative_to(dist.parent)}")


if __name__ == "__main__":
    assert rgb("#007AFF") == "0,122,255" and rgb("rgba(1, 2, 3, 0.5)") == "1,2,3"
    assert alpha("rgba(1, 2, 3, 0.5)") == "0.5" and alpha("#007AFF") == "1"
    build()
