#!/usr/bin/env python3
"""Per-widget pixel diff of the Slate theme: GTK4 (reference) vs GTK3 and Qt (Kvantum).

  pixdiff.py [light|dark|both] [widget ids...]     run everything, write the report
  pixdiff.py shot <toolkit> <mode> <show>          internal: one gallery run, called under xvfb-run

Each gallery runs under Xvfb (no window manager, scale 2, same fonts), is screenshotted whole, then every
widget is cropped by its bounds JSON. Output in $AGENT_DATA_DIR/Slate-pixdiff/out/<mode>/: <id>.png is a strip
[GTK4 | GTK3 | Qt | diff GTK4-Qt in red] and report.txt lists the widgets worst first.
"""
import json
import os
import re
import subprocess
import sys
import time
import zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TAG = os.environ.get("PIXDIFF_TAG", "main")
DATA = Path(os.environ.get("AGENT_DATA_DIR", "/mnt/nvme1/data/_custom/orca/workspaces")) / f"Slate-pixdiff-{TAG}"
DIST = Path(os.environ.get("SLATE_DIST") or DATA / "dist")
TOOLKITS = ("gtk4", "gtk3", "qt")
ONLY = os.environ.get("PIXDIFF_ONLY", "")  # gtk3 | qt: skip the other toolkit (GTK4 is the reference and always runs)
ACTIVE = tuple(t for t in TOOLKITS if t == "gtk4" or not ONLY or t == ONLY)
SHOWS = ("window", "menu", "popover", "tooltip", "dialog")
SCALE = 2
SCREEN_W, SCREEN_H = 3400, 2400  # GTK3 adds a big CSD shadow around the 2x window
SCREEN = f"{SCREEN_W}x{SCREEN_H}x24"
FUZZ = "6%"
REAL_HOME = Path.home()
FONTCONF = DATA / "fonts.conf"


def write_fontconf():
    """The repo's fontconfig plus the real font dir and one shared cache (every temp home would otherwise rebuild it)."""
    src = (REPO / "scripts/pixdiff-fonts.conf").read_text()
    extra = f"  <dir>{REAL_HOME}/.local/share/fonts</dir>\n  <cachedir>{DATA}/fontcache</cachedir>\n</fontconfig>"
    DATA.mkdir(parents=True, exist_ok=True)
    FONTCONF.write_text(src.replace("</fontconfig>", extra))
    run(["fc-cache"], env=dict(os.environ, FONTCONFIG_FILE=str(FONTCONF)))


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


# ---------------------------------------------------------------- one gallery run (inside xvfb-run)
def prepare_home(home, name, mode):
    (home / ".config").mkdir(parents=True, exist_ok=True)
    (home / ".cache").mkdir(exist_ok=True)
    (home / ".local/share").mkdir(parents=True, exist_ok=True)
    (home / ".themes").mkdir(exist_ok=True)
    for link, target in ((home / ".local/share/fonts", REAL_HOME / ".local/share/fonts"),
                         (home / ".themes" / name, DIST / name)):
        if not link.is_symlink():
            link.symlink_to(target)
    for v in ("3.0", "4.0"):
        d = home / ".config" / f"gtk-{v}"
        d.mkdir(exist_ok=True)
        (d / "settings.ini").write_text(
            "[Settings]\n"
            f"gtk-theme-name={name}\n"
            f"gtk-application-prefer-dark-theme={1 if mode == 'dark' else 0}\n"
            "gtk-decoration-layout=close,minimize,maximize:\n"
            "gtk-xft-antialias=1\ngtk-xft-hinting=0\ngtk-xft-hintstyle=hintnone\ngtk-xft-rgba=none\n"
            "gtk-xft-dpi=98304\n")


def shot(tk, mode, show):
    name = f"Slate-{mode.capitalize()}"
    work = DATA / "work" / mode
    work.mkdir(parents=True, exist_ok=True)
    home = DATA / "homes" / f"{mode}-{tk}-{show}"
    prepare_home(home, name, mode)
    base = work / f"{tk}-{show}"
    bj = base.with_suffix(".json")
    bj.unlink(missing_ok=True)
    env = dict(os.environ, FONTCONFIG_FILE=str(FONTCONF),
               LANG="en_US.UTF-8", LC_ALL="en_US.UTF-8", GSETTINGS_BACKEND="keyfile", NO_AT_BRIDGE="1", GTK_A11Y="none")
    env.pop("QT_QPA_PLATFORMTHEME", None)
    # no session bus: parallel GTK apps with one application id would otherwise forward to each other (and to the owner's bus)
    env["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=/nonexistent"
    extra = ["--show", show] if show != "window" else []
    if tk != "qt":  # the Qt wrapper (qt-env.sh) sets its own HOME and config
        env.update(HOME=str(home), XDG_CONFIG_HOME=str(home / ".config"), XDG_DATA_HOME=str(home / ".local/share"),
                   XDG_CACHE_HOME=str(home / ".cache"))
    if tk == "qt":
        env.update(QT_QPA_PLATFORM="xcb", QT_SCALE_FACTOR=str(SCALE), QT_AUTO_SCREEN_SCALE_FACTOR="0")
        cmd = [str(REPO / "scripts/pixdiff-qt.sh"), name, str(home), "--mode", mode, "--bounds", str(bj), "--quit-after", "30000"] + extra
    else:
        env.update(GDK_BACKEND="x11", GDK_SCALE=str(SCALE), GSK_RENDERER="cairo", GTK_THEME=name, GTK_USE_PORTAL="0",
                   GDK_DEBUG="no-portals")
        cmd = ["python3", str(REPO / f"scripts/demo-{tk}.py"), "--bounds", str(bj)] + extra
    log = open(base.with_suffix(".log"), "w")
    t0 = time.time()
    proc = subprocess.Popen(cmd, env=env, stdout=log, stderr=log)
    try:
        while time.time() - t0 < 15 and not (bj.exists() and bj.stat().st_size > 0):
            if proc.poll() is not None:
                break
            time.sleep(0.1)
        # popups open at ~1.2 s (GTK) and 0.5 s (Qt); give them time to paint
        time.sleep(max(0.5, 2.2 - (time.time() - t0)) if show != "window" else 0.6)
        png = base.with_suffix(".png")
        r = run(["import", "-window", "root", str(png)])
        if r.returncode:
            print(f"import failed for {tk} {mode} {show}: {r.stderr}", file=sys.stderr)
        wins = {}
        for wid in run(["xdotool", "search", "--onlyvisible", "--maxdepth", "1", "--name", ""]).stdout.split():
            g = run(["xdotool", "getwindowgeometry", "--shell", wid]).stdout
            kv = dict(re.findall(r"(\w+)=(-?\d+)", g))
            if kv:
                wins[wid] = [int(kv["X"]), int(kv["Y"]), int(kv["WIDTH"]), int(kv["HEIGHT"])]
        base.with_suffix(".win.json").write_text(json.dumps(wins))
    finally:
        proc.terminate()
        try:
            proc.wait(5)
        except subprocess.TimeoutExpired:
            proc.kill()
    return 0 if bj.exists() else 1


# ---------------------------------------------------------------- crop + compare
def rects_for(tk, mode, show):
    """{id: [x, y, w, h]} in screenshot pixels for one gallery run."""
    base = DATA / "work" / mode / f"{tk}-{show}"
    if not base.with_suffix(".json").exists():
        return {}
    b = json.loads(base.with_suffix(".json").read_text())
    wins = json.loads(base.with_suffix(".win.json").read_text()) if base.with_suffix(".win.json").exists() else {}
    wins = [r for r in wins.values() if r[2] < SCREEN_W]  # drop the root window
    wins.sort(key=lambda r: -(r[2] * r[3]))
    if tk == "qt":
        ox, oy, k = b["window"][0], b["window"][1], 1  # Qt bounds are already device px
    else:
        # GTK bounds are relative to the visible frame; the CSD shadow around it is black on the black root
        bbox = magick_out("-quiet", DATA / "work" / mode / f"{tk}-{show}.png", "-fuzz", "2%", "-format", "%@", "info:")
        m = re.match(r"(\d+)x(\d+)\+(\d+)\+(\d+)", bbox)
        ox, oy, k = (int(m[3]), int(m[4]), SCALE) if m else (0, 0, SCALE)
    out = {}
    for key, (x, y, w, h) in b.items():
        if not key.startswith("surface:"):
            out[key] = [ox + x * k, oy + y * k, w * k, h * k] if key != "window" else [ox, oy, w * k, h * k]
    if show == "tooltip" and tk == "gtk3" and "tooltip" in out:
        out["tooltip-tip"] = out.pop("tooltip")  # GTK3 writes the tip window over the button id
    if show != "window" and len(wins) > 1:
        pid = "tooltip-tip" if show == "tooltip" else show
        sx, sy, sw, sh = b.get("surface:" + pid, (None,) * 4)
        if sx is not None:  # visible popup inside its own X surface (the surface also holds the shadow margin)
            out[pid] = [wins[1][0] + sx * SCALE, wins[1][1] + sy * SCALE, sw * SCALE, sh * SCALE]
        elif pid not in out:  # no offset exported: the biggest other X window
            out[pid] = wins[1]
    return out


def collect(mode):
    """{toolkit: {id: (png path, rect)}}, window run first, popup runs add menu/popover/tooltip-tip/dialog."""
    res = {tk: {} for tk in TOOLKITS}
    for tk in ACTIVE:
        for show in SHOWS:
            png = DATA / "work" / mode / f"{tk}-{show}.png"
            if not png.exists():
                continue
            rects = rects_for(tk, mode, show)
            if show == "window":
                for k, r in rects.items():
                    res[tk][k] = (png, r)
            else:
                pid = "tooltip-tip" if show == "tooltip" else show
                if pid in rects:
                    res[tk][pid] = (png, rects[pid])
    return res


def magick_out(*args):
    return run(["magick", *map(str, args)]).stdout.strip()


def magick(*args):
    r = run(["magick", *map(str, args)])
    if r.returncode not in (0, 1):
        print("magick failed:", " ".join(map(str, args))[:200], r.stderr[:200], file=sys.stderr)
    return r


def pad_crop(src, rect, w, h, dst):
    if src is None:
        magick("-size", f"{w}x{h}", "xc:magenta", dst)
        return
    x, y, rw, rh = rect
    magick(src, "-alpha", "off", "-crop", f"{rw}x{rh}+{x}+{y}", "+repage", "-background", "magenta", "-gravity", "NorthWest",
           "-extent", f"{w}x{h}", dst)


def diff_pct(a, b, w, h, dst=None):
    r = run(["magick", "compare", "-metric", "AE", "-fuzz", FUZZ, "-highlight-color", "red", "-lowlight-color", "#e6e6e6",
             str(a), str(b), str(dst) if dst else "null:"])
    try:
        ae = float(r.stderr.strip().split()[0])
    except (ValueError, IndexError):
        return 100.0
    return 100.0 * ae / (w * h)


def do_widget(mode, wid, data, out):
    got = {tk: data[tk].get(wid) for tk in TOOLKITS}
    sizes = {tk: (g[1][2], g[1][3]) if g else None for tk, g in got.items()}
    ref = sizes["gtk4"]
    if ref is None:
        return None
    w = max(s[0] for tk, s in sizes.items() if s and tk in ACTIVE)
    h = max(s[1] for tk, s in sizes.items() if s and tk in ACTIVE)
    tmp = out / ".tmp"
    tmp.mkdir(exist_ok=True)
    pads = {}
    for tk in ACTIVE:
        pads[tk] = tmp / f"{wid}-{tk}.png"
        pad_crop(got[tk][0] if got[tk] else None, got[tk][1] if got[tk] else None, w, h, pads[tk])
    pct = {tk: (diff_pct(pads["gtk4"], pads[tk], w, h, dif if tk == "qt" else None) if got[tk] else 100.0) if tk in ACTIVE and tk != "gtk4" else None
           for tk, dif in ((tk, tmp / f"{wid}-diff.png") for tk in TOOLKITS)}
    dif = tmp / f"{wid}-diff.png"
    if not dif.exists():  # the diff panel is GTK4-Qt, or GTK4-GTK3 when Qt is skipped
        if "qt" in ACTIVE:
            magick("-size", f"{w}x{h}", "xc:red", dif)
        else:
            diff_pct(pads["gtk4"], pads["gtk3"], w, h, dif)
    magick(*[pads[tk] for tk in ACTIVE if tk in pads], dif, "-bordercolor", "#888888", "-border", "2", "+append", out / f"{wid}.png")
    for p in (*pads.values(), dif):
        p.unlink(missing_ok=True)
    return wid, sizes, pct["gtk3"], pct["qt"]


def main_compare(mode, only):
    out = DATA / "out" / mode
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.png"):
        old.unlink()
    data = collect(mode)
    ids = [i for i in data["gtk4"] if not only or i in only]
    with ThreadPoolExecutor(6) as ex:
        rows = [r for r in ex.map(lambda i: do_widget(mode, i, data, out), ids) if r]
    try:
        (out / ".tmp").rmdir()
    except OSError:
        pass
    rows.sort(key=lambda r: (-(r[3] if r[3] is not None else r[2]), r[0]))
    fmt = lambda s: f"{s[0]}x{s[1]}" if s else "-"
    pf = lambda p: "-" if p is None else f"{p:.1f}"
    lines = [f"{'id':<20} {'GTK4':>10} {'GTK3':>10} {'Qt':>10} {'Qt-GTK4 (w,h)':>14} {'GTK3 diff%':>10} {'Qt diff%':>9}"]
    for wid, sizes, p3, pq in rows:
        d = f"({sizes['qt'][0] - sizes['gtk4'][0]:+d},{sizes['qt'][1] - sizes['gtk4'][1]:+d})" if sizes["qt"] else "n/a"
        lines.append(f"{wid:<20} {fmt(sizes['gtk4']):>10} {fmt(sizes['gtk3']):>10} {fmt(sizes['qt']):>10} {d:>14} {pf(p3):>10} {pf(pq):>9}")
    (out / "report.txt").write_text("\n".join(lines) + "\n")
    return out / "report.txt"


def main():
    args = sys.argv[1:]
    if args and args[0] == "shot":
        sys.exit(shot(*args[1:4]))
    modes = ["light", "dark"]
    if args and args[0] in ("light", "dark", "both"):
        modes = ["light", "dark"] if args[0] == "both" else [args[0]]
        args = args[1:]
    only = set(args)
    jobs = [(tk, m, s) for m in modes for s in SHOWS for tk in ACTIVE]

    def launch(j):
        i = jobs.index(j)
        tk, m, s = j
        r = run(["xvfb-run", "-n", str(1000 + zlib.crc32(TAG.encode()) % 500 * 40 + i), "-s", f"-screen 0 {SCREEN} -nolisten tcp", sys.executable, str(Path(__file__)), "shot", tk, m, s])
        if r.returncode:
            print(f"job {j} failed: {r.stderr.strip()[-300:]}", file=sys.stderr)

    write_fontconf()
    t0 = time.time()
    with ThreadPoolExecutor(5) as ex:
        list(ex.map(launch, jobs))
    print(f"galleries done in {time.time() - t0:.0f}s", file=sys.stderr)
    for m in modes:
        print(main_compare(m, only))


if __name__ == "__main__":
    main()
