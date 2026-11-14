#!/bin/sh
# Apply Slate to the running KDE Plasma session. Idempotent.
# Usage: apply-kde.sh <Slate-Light|Slate-Dark>
# DRY_RUN=1 prints every command; kwriteconfig6 only runs when XDG_CONFIG_HOME
# is set too (point it at a scratch dir to inspect the result, never at ~/.config).
set -eu

name=${1:-}
case $name in
  Slate-Light|Slate-Dark) ;;
  *) echo "usage: $0 <Slate-Light|Slate-Dark>" >&2; exit 2 ;;
esac

root=$(cd "$(dirname "$0")/.." && pwd)
dry=${DRY_RUN:-0}
write_cfg=1
if [ "$dry" = 1 ] && [ -z "${XDG_CONFIG_HOME:-}" ]; then write_cfg=0; fi

# Tuning values the tokens do not cover.
font_size=10
blur_strength=9
blur_noise=2
scale_in_out=0.92
genie_ms=400

tok() {
  python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["common"][sys.argv[2]].removesuffix("px"))' \
    "$root/tokens.json" "$1"
}
factor=$(tok kwin_animation_factor)
family=$(tok font_family_kde)
radius=$(tok radius_window)

# kw <file> <group> <key> <value>: write one config key.
kw() {
  if [ "$dry" = 1 ]; then echo "+ kwriteconfig6 --file $1 --group $2 --key $3 '$4'"; fi
  if [ "$dry" != 1 ] || [ "$write_cfg" = 1 ]; then
    kwriteconfig6 --file "$1" --group "$2" --key "$3" "$4"
  fi
}
# act <cmd...>: run a command that touches the live session (skipped on dry run).
act() {
  if [ "$dry" = 1 ]; then echo "+ $*"; else "$@"; fi
}

command -v kwriteconfig6 >/dev/null 2>&1 || { echo "kwriteconfig6 not found (install KDE Frameworks 6)" >&2; exit 1; }

# Colors, widget style, Plasma theme.
kw kdeglobals General ColorScheme "$name"
act plasma-apply-colorscheme "$name"
kw kdeglobals KDE widgetStyle kvantum
if command -v kvantummanager >/dev/null 2>&1; then
  act kvantummanager --set "$name"
else
  echo "Kvantum is not installed: install kvantum (and run install.sh) for the Slate widget style."
fi
kw plasmarc Theme name "$name"
act plasma-apply-desktoptheme "$name"

# Window decoration: Aurorae, traffic lights on the left, no frame.
if [ ! -d "${XDG_DATA_HOME:-$HOME/.local/share}/aurorae/themes/$name" ]; then
  echo "note: Aurorae theme $name is not installed yet (run install.sh)."
fi
kw kwinrc org.kde.kdecoration2 library org.kde.kwin.aurorae.v2
kw kwinrc org.kde.kdecoration2 theme "__aurorae__svg__$name"
kw kwinrc org.kde.kdecoration2 ButtonsOnLeft XIA
kw kwinrc org.kde.kdecoration2 ButtonsOnRight ""
kw kwinrc org.kde.kdecoration2 BorderSize None
kw kwinrc org.kde.kdecoration2 BorderSizeAuto false
kw kwinrc org.kde.kdecoration2 CloseOnDoubleClickOnMenu false
kw kwinrc Windows TitlebarDoubleClickCommand Maximize

# Font: only when the family is installed.
if fc-list : family 2>/dev/null | grep -qiE "(^|,)$family(,|\$)"; then
  f="$family,$font_size,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
  kw kdeglobals General font "$f"
  kw kdeglobals General menuFont "$f"
  kw kdeglobals General toolBarFont "$f"
  kw kdeglobals General smallestReadableFont "$family,$((font_size - 1)),-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
  kw kdeglobals WM activeFont "$family,$font_size,-1,5,600,0,0,0,0,0,0,0,0,0,0,1"
else
  echo "note: font $family is not installed; fonts left as they are."
fi

# Motion.
kw kdeglobals KDE AnimationDurationFactor "$factor"
for id in scale magiclamp blur fadingpopups slidingpopups overview fullscreen maximize; do
  kw kwinrc Plugins "${id}Enabled" true
done
for id in squash fade wobblywindows; do   # squash and fade clash with scale and genie
  kw kwinrc Plugins "${id}Enabled" false
done
kw kwinrc Effect-scale InScale "$scale_in_out"
kw kwinrc Effect-scale OutScale "$scale_in_out"
kw kwinrc Effect-magiclamp AnimationDuration "$genie_ms"
kw kwinrc Effect-blur BlurStrength "$blur_strength"
kw kwinrc Effect-blur NoiseStrength "$blur_noise"

# Window corner radius: KWin 6.8 has no core key; use the shapecorners effect when installed.
if [ -e /usr/lib/qt6/plugins/kwin/effects/plugins/kwin4_effect_shapecorners.so ] ||
   [ -e "$HOME/.local/lib/qt6/plugins/kwin/effects/plugins/kwin4_effect_shapecorners.so" ]; then
  kw kwinrc Plugins kwin4_effect_shapecornersEnabled true
  kw kwinrc Round-Corners Size "$radius"
  kw kwinrc Round-Corners InactiveCornerRadius "$radius"
else
  echo "note: no window corner radius effect installed; window corners come from the Aurorae theme."
fi

# Reload KWin when it is on the session bus.
if [ "$dry" = 1 ]; then
  echo "+ qdbus6 org.kde.KWin /KWin reconfigure"
elif command -v qdbus6 >/dev/null 2>&1 && qdbus6 org.kde.KWin /KWin reconfigure >/dev/null 2>&1; then
  :
else
  echo "note: KWin is not on the session bus; log out and in to load the new settings."
fi
echo "Slate applied: $name"
