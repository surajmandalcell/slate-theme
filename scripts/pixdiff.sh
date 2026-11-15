#!/usr/bin/env zsh
# Per-widget pixel diff, GTK4 (reference) vs GTK3 and Qt/Kvantum, under Xvfb.
# usage: [PIXDIFF_TAG=main] [PIXDIFF_ONLY=gtk3|qt] scripts/pixdiff.sh [light|dark|both] [widget ids...]
# Output: $AGENT_DATA_DIR/Slate-pixdiff-<tag>/out/<mode>/<id>.png (strip GTK4 | GTK3 | Qt | diff) and report.txt
# Everything it writes (theme build, homes, shots) lives under that tag folder, so runs with different tags never collide.
ROOT=${0:A:h:h}
cd $ROOT || exit 1
export AGENT_DATA_DIR=${AGENT_DATA_DIR:-/mnt/nvme1/data/_custom/orca/workspaces}
export PIXDIFF_TAG=${PIXDIFF_TAG:-main}
export SLATE_DIST=$AGENT_DATA_DIR/Slate-pixdiff-$PIXDIFF_TAG/dist
[[ -f $HOME/.local/share/fonts/Inter/Inter-Regular.ttf ]] || { echo "Inter font missing in ~/.local/share/fonts/Inter" >&2; exit 1; }
mkdir -p ${SLATE_DIST:h}
python3 build.py >/dev/null || exit 1
# build Kvantum and the Qt gallery once (sourcing qt-env.sh does it); a throwaway home keeps ~/.config untouched
if [[ $PIXDIFF_ONLY != gtk3 ]]; then
    ( . scripts/qt-env.sh Slate-Light ${SLATE_DIST:h}/homes/prep ) >/dev/null 2>&1 || { echo "Qt gallery build failed" >&2; exit 1; }
    ninja -C $AGENT_DATA_DIR/Slate-theme-qt/build-gallery >/dev/null || exit 1
fi
exec python3 scripts/pixdiff.py "$@"
