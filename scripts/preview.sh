#!/bin/sh
# Render the GTK3 and GTK4 demo apps with each built Slate theme and save
# screenshots to preview/demo-gtk<N>-<mode>.png. Uses a temp HOME and a
# virtual X server, so the real desktop config is never touched.
# Run after ./install.sh or python3 build.py. Needs xvfb-run, imagemagick, PyGObject.
set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)

# Inner mode: runs inside xvfb-run. $2 = demo script, $3 = output png.
if [ "${1:-}" = --shot ]; then
    python3 "$2" 2>/dev/null &
    pid=$!
    sleep 4
    import -window root "$3"
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
    exit 0
fi

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$ROOT/preview"

for mode in light dark; do
    if [ "$mode" = light ]; then name=Slate-Light; else name=Slate-Dark; fi
    dist=$ROOT/dist/$name
    [ -d "$dist" ] || { echo "no $dist, run build.py first" >&2; continue; }

    home=$TMP/home-$mode
    mkdir -p "$home/.themes/$name" "$home/.config/gtk-3.0" "$home/.config/gtk-4.0" \
        "$home/.cache" "$home/.local/share"
    cp -a "$dist/index.theme" "$home/.themes/$name/" 2>/dev/null || true
    for v in gtk-3.0 gtk-4.0; do
        [ -d "$dist/$v" ] && cp -a "$dist/$v" "$home/.themes/$name/$v"
        printf '[Settings]\ngtk-theme-name=%s\ngtk-decoration-layout=close,minimize,maximize:\ngtk-font-name=Inter 10\n' \
            "$name" > "$home/.config/$v/settings.ini"
    done

    for n in 3 4; do
        demo=$ROOT/scripts/demo-gtk$n.py
        [ -f "$demo" ] || { echo "missing $demo" >&2; continue; }
        out=$ROOT/preview/demo-gtk$n-$mode.png
        env HOME="$home" XDG_CONFIG_HOME="$home/.config" XDG_DATA_HOME="$home/.local/share" \
            XDG_CACHE_HOME="$home/.cache" GDK_BACKEND=x11 GSK_RENDERER=cairo \
            GTK_A11Y=none NO_AT_BRIDGE=1 \
            xvfb-run -a -s "-screen 0 1280x800x24" sh "$0" --shot "$demo" "$out"
        echo "wrote $out"
    done
done
