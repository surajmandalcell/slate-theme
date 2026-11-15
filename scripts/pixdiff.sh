#!/usr/bin/env zsh
# Per-widget pixel diff, GTK4 (reference) vs GTK3 and Qt/Kvantum, under Xvfb.
# usage: scripts/pixdiff.sh [light|dark|both] [widget ids...]
# Output: $AGENT_DATA_DIR/Slate-pixdiff/out/<mode>/<id>.png (strip GTK4 | GTK3 | Qt | diff) and report.txt
ROOT=${0:A:h:h}
cd $ROOT || exit 1
export AGENT_DATA_DIR=${AGENT_DATA_DIR:-/mnt/nvme1/data/_custom/orca/workspaces}
[[ -f $HOME/.local/share/fonts/Inter/Inter-Regular.ttf ]] || { echo "Inter font missing in ~/.local/share/fonts/Inter" >&2; exit 1; }
python3 build.py >/dev/null || exit 1
# build Kvantum and the Qt gallery once (sourcing qt-env.sh does it); a throwaway home keeps ~/.config untouched
( . scripts/qt-env.sh Slate-Light $AGENT_DATA_DIR/Slate-pixdiff/homes/prep ) >/dev/null 2>&1 || { echo "Qt gallery build failed" >&2; exit 1; }
(cd $ROOT/scripts/demo-qt && ninja -C $AGENT_DATA_DIR/Slate-theme-qt/build-gallery >/dev/null) || exit 1
exec python3 scripts/pixdiff.py "$@"
