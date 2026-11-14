#!/usr/bin/env bash
# qt-run.sh <Slate-Light|Slate-Dark> <temp home> [gallery args]: run the Qt gallery on Wayland with the Kvantum env.
. "$(dirname "$0")/../qt-env.sh" "$1" "$2" >&2 || exit 1
shift 2
QT_QPA_PLATFORM=wayland exec "$SLATE_QT_GALLERY" "$@"
