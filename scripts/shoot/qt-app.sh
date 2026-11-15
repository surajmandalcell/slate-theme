#!/usr/bin/env bash
# qt-app.sh <Slate-Light|Slate-Dark> <temp home> <command> [args]: run any Qt app on Wayland with the Slate Kvantum env.
. "$(dirname "$0")/../qt-env.sh" "$1" "$2" >&2 || exit 1
shift 2
QT_QPA_PLATFORM=wayland exec "$@"
