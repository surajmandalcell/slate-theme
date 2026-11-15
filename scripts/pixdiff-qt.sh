#!/usr/bin/env bash
# Run the Qt gallery inside the Slate Kvantum env: pixdiff-qt.sh <Slate-Light|Slate-Dark> <temp-home> <gallery args...>
# Used by pixdiff.py (each job has its own temp home, so jobs never share config files).
. "$(dirname "${BASH_SOURCE[0]}")/qt-env.sh" "$1" "$2" || exit 1
shift 2
exec "$SLATE_QT_GALLERY" "$@"
