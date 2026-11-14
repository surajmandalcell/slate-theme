#!/bin/sh
# Slate installer: builds the themes and copies them into the user's home.
# No sudo. Run ./install.sh -h for the options.
set -eu

ROOT=$(cd "$(dirname "$0")" && pwd)
THEMES="Slate-Light Slate-Dark"
TAG=bak-slate
GTK_LAYOUT="close,minimize,maximize:"

usage() {
    cat <<EOF
Usage: ./install.sh [--apply light|dark] [--uninstall] [--prefix DIR] [-h]

  (no flags)        build and install Slate-Light and Slate-Dark
  --apply MODE      also make MODE (light or dark) the active theme
                    (GTK settings.ini, libadwaita gtk.css, gsettings, KDE)
  --uninstall       remove what this script installed, restore backups
  --prefix DIR      use DIR as the home directory (for testing; gsettings
                    and the KDE apply script are skipped)
  -h, --help        show this help
EOF
}

APPLY=
UNINSTALL=0
PREFIX=
while [ $# -gt 0 ]; do
    case $1 in
        --apply)
            [ $# -ge 2 ] || { echo "--apply needs light or dark" >&2; exit 2; }
            APPLY=$2
            shift 2
            ;;
        --uninstall) UNINSTALL=1; shift ;;
        --prefix)
            [ $# -ge 2 ] || { echo "--prefix needs a directory" >&2; exit 2; }
            PREFIX=$2
            shift 2
            ;;
        -h|--help) usage; exit 0 ;;
        *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
    esac
done

case $APPLY in
    ""|light|dark) ;;
    *) echo "--apply takes light or dark" >&2; exit 2 ;;
esac

if [ -n "$PREFIX" ]; then
    mkdir -p "$PREFIX"
    H=$(cd "$PREFIX" && pwd)
else
    H=$HOME
fi
[ -n "$H" ] && [ "$H" != / ] || { echo "refusing to use / as home" >&2; exit 1; }

DATA=$H/.local/share
CONF=$H/.config
STATE=$CONF/slate-theme

# --- helpers ---------------------------------------------------------------

# Copy directory $1 to $2 (replacing $2). Skip when $1 is missing.
put_dir() {
    [ -d "$1" ] || return 0
    rm -rf "$2"
    mkdir -p "$(dirname "$2")"
    cp -a "$1" "$2"
}

# Copy file $1 to $2. Skip when $1 is missing.
put_file() {
    [ -f "$1" ] || return 0
    mkdir -p "$(dirname "$2")"
    cp -a "$1" "$2"
}

# Remember what was at $1 before Slate touched it: a copy (.bak-slate),
# or a marker (.slate-new) when nothing was there. Only the first call counts.
backup() {
    [ -e "$1.$TAG" ] || [ -e "$1.slate-new" ] && return 0
    if [ -e "$1" ]; then
        cp -a "$1" "$1.$TAG"
    else
        mkdir -p "$(dirname "$1")"
        : > "$1.slate-new"
    fi
}

# Undo backup() for $1.
restore() {
    if [ -e "$1.$TAG" ]; then
        rm -rf "$1"
        mv "$1.$TAG" "$1"
    elif [ -e "$1.slate-new" ]; then
        rm -rf "$1" "$1.slate-new"
    fi
}

# Set key $2 to value $3 in the [Settings] section of ini file $1.
set_ini() {
    f=$1 k=$2 v=$3
    [ -f "$f" ] || printf '[Settings]\n' > "$f"
    grep -q '^\[Settings\]' "$f" || printf '\n[Settings]\n' >> "$f"
    tmp=$f.slate-tmp
    awk -v k="$k" -v v="$v" '
        /^\[/ { if (insec && !done) { print k "=" v; done = 1 } insec = ($0 == "[Settings]") }
        insec && index($0, k "=") == 1 { if (!done) print k "=" v; done = 1; next }
        { print }
        END { if (!done) print k "=" v }
    ' "$f" > "$tmp"
    mv "$tmp" "$f"
}

mode_name() { [ "$1" = light ] && echo Slate-Light || echo Slate-Dark; }

# --- install ---------------------------------------------------------------

install_theme() {
    n=$1
    d=$ROOT/dist/$n
    if [ ! -d "$d" ]; then echo "missing $d, skipped" >&2; return 0; fi
    echo "installing $n"
    for base in "$H/.themes" "$DATA/themes"; do
        put_file "$d/index.theme" "$base/$n/index.theme"
        put_dir "$d/gtk-3.0" "$base/$n/gtk-3.0"
        put_dir "$d/gtk-4.0" "$base/$n/gtk-4.0"
    done
    put_dir "$d/kde/kvantum/$n" "$CONF/Kvantum/$n"
    put_dir "$d/kde/aurorae/$n" "$DATA/aurorae/themes/$n"
    put_file "$d/kde/color-schemes/$n.colors" "$DATA/color-schemes/$n.colors"
    put_dir "$d/kde/plasma/desktoptheme/$n" "$DATA/plasma/desktoptheme/$n"
    if [ -d "$d/kde/look-and-feel" ]; then
        for lf in "$d"/kde/look-and-feel/*; do
            [ -d "$lf" ] || continue
            put_dir "$lf" "$DATA/plasma/look-and-feel/$(basename "$lf")"
        done
    fi
}

apply_theme() {
    mode=$1
    n=$(mode_name "$mode")
    d=$ROOT/dist/$n
    [ -d "$d" ] || { echo "cannot apply: $d missing" >&2; return 1; }
    echo "applying $n"

    for v in 3.0 4.0; do
        ini=$CONF/gtk-$v/settings.ini
        mkdir -p "$CONF/gtk-$v"
        backup "$ini"
        set_ini "$ini" gtk-theme-name "$n"
        set_ini "$ini" gtk-decoration-layout "$GTK_LAYOUT"
    done

    # libadwaita apps ignore the theme name and read ~/.config/gtk-4.0/gtk.css
    if [ -f "$d/gtk-4.0/gtk.css" ]; then
        backup "$CONF/gtk-4.0/gtk.css"
        cp -a "$d/gtk-4.0/gtk.css" "$CONF/gtk-4.0/gtk.css"
        if [ -d "$d/gtk-4.0/assets" ]; then
            backup "$CONF/gtk-4.0/assets"
            rm -rf "$CONF/gtk-4.0/assets"
            cp -a "$d/gtk-4.0/assets" "$CONF/gtk-4.0/assets"
        fi
    fi

    if [ -n "$PREFIX" ]; then
        echo "prefix mode: gsettings and KDE apply skipped"
        return 0
    fi

    if command -v gsettings >/dev/null 2>&1; then
        if [ ! -f "$STATE/gsettings" ]; then
            mkdir -p "$STATE"
            {
                echo "gtk-theme $(gsettings get org.gnome.desktop.interface gtk-theme 2>/dev/null || true)"
                echo "color-scheme $(gsettings get org.gnome.desktop.interface color-scheme 2>/dev/null || true)"
                echo "button-layout $(gsettings get org.gnome.desktop.wm.preferences button-layout 2>/dev/null || true)"
            } > "$STATE/gsettings"
        fi
        scheme=prefer-$mode
        gsettings set org.gnome.desktop.interface gtk-theme "$n" || true
        gsettings set org.gnome.desktop.interface color-scheme "$scheme" || true
        gsettings set org.gnome.desktop.wm.preferences button-layout "$GTK_LAYOUT" || true
    fi

    case ${XDG_CURRENT_DESKTOP:-} in
        *KDE*)
            if [ -f "$ROOT/scripts/apply-kde.sh" ]; then
                sh "$ROOT/scripts/apply-kde.sh" "$n"
            fi
            ;;
    esac
}

# --- uninstall -------------------------------------------------------------

uninstall_all() {
    for n in $THEMES; do
        echo "removing $n"
        rm -rf "$H/.themes/$n" "$DATA/themes/$n" \
            "$CONF/Kvantum/$n" "$DATA/aurorae/themes/$n" \
            "$DATA/color-schemes/$n.colors" "$DATA/plasma/desktoptheme/$n" \
            "$DATA/plasma/look-and-feel/org.slate.$n.desktop"
    done
    for f in "$CONF/gtk-3.0/settings.ini" "$CONF/gtk-4.0/settings.ini" \
        "$CONF/gtk-4.0/gtk.css" "$CONF/gtk-4.0/assets"; do
        restore "$f"
    done
    if [ -f "$STATE/gsettings" ] && command -v gsettings >/dev/null 2>&1; then
        while read -r key val; do
            [ -n "$val" ] || continue
            case $key in
                gtk-theme) gsettings set org.gnome.desktop.interface gtk-theme "$val" || true ;;
                color-scheme) gsettings set org.gnome.desktop.interface color-scheme "$val" || true ;;
                button-layout) gsettings set org.gnome.desktop.wm.preferences button-layout "$val" || true ;;
            esac
        done < "$STATE/gsettings"
    fi
    rm -rf "$STATE"
    if [ -n "$PREFIX" ]; then
        # remove the empty folders install created, deepest first
        for p in "$DATA/plasma/look-and-feel" "$DATA/plasma/desktoptheme" "$DATA/plasma" \
            "$DATA/aurorae/themes" "$DATA/aurorae" "$DATA/color-schemes" "$DATA/themes" \
            "$CONF/Kvantum" "$CONF/gtk-3.0" "$CONF/gtk-4.0" "$CONF" "$DATA" "$H/.local" \
            "$H/.themes" "$H"; do
            rmdir "$p" 2>/dev/null || true
        done
    fi
}

# --- main ------------------------------------------------------------------

if [ "$UNINSTALL" -eq 1 ]; then
    uninstall_all
    echo done
    exit 0
fi

python3 "$ROOT/build.py"
for n in $THEMES; do install_theme "$n"; done
[ -z "$APPLY" ] || apply_theme "$APPLY"
echo done
