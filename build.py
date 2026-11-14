#!/usr/bin/env python3
"""Render src/ into dist/Slate-Light and dist/Slate-Dark from tokens.json.

Files ending in `.in` are templates: `{{key}}` becomes the token value, and
`{{key|rgb}}` becomes "r,g,b" (for KDE .colors files). `__NAME__` in a path
becomes the theme name. Other files are copied as they are.
"""
import json, re, shutil, sys
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


FILTERS = {"rgb": rgb, "px": lambda v: v.removesuffix("px")}


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
    src, dist = ROOT / "src", ROOT / "dist"
    shutil.rmtree(dist, ignore_errors=True)
    for mode in ("light", "dark"):
        tokens = {**data["common"], **data[mode]}
        out_root = dist / tokens["name"]
        for f in sorted(src.rglob("*")):
            if not f.is_file():
                continue
            rel = str(f.relative_to(src)).replace("__NAME__", tokens["name"])
            out = out_root / rel.removesuffix(".in")
            out.parent.mkdir(parents=True, exist_ok=True)
            if f.suffix == ".in":
                out.write_text(render(f.read_text(), tokens, f))
            else:
                shutil.copy2(f, out)
        print(f"built {out_root.relative_to(ROOT)}")


if __name__ == "__main__":
    assert rgb("#007AFF") == "0,122,255" and rgb("rgba(1, 2, 3, 0.5)") == "1,2,3"
    build()
