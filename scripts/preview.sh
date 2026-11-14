#!/bin/sh
# Real screenshots of the Slate theme: see scripts/shoot.sh (private nested KWin, no live desktop touched).
exec zsh "$(dirname "$0")/shoot.sh" "$@"
