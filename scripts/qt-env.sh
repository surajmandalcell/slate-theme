#!/usr/bin/env bash
# Source me: . scripts/qt-env.sh Slate-Light <temp-home>
# Builds Kvantum (style plugin only, Qt6, user space) and the Qt gallery on first use, then exports the env
# so Qt apps render with the Slate Kvantum theme. Needs no sudo, never touches the real ~/.config.
# Exports HOME (the temp home), XDG_CONFIG_HOME, QT_PLUGIN_PATH, QT_STYLE_OVERRIDE, SLATE_QT_GALLERY.
# Run it in a subshell if you want to keep your own HOME.
if [ -n "$BASH_VERSION" ]; then _qe_src="${BASH_SOURCE[0]}"; else eval '_qe_src=${(%):-%x}'; fi
_qe_repo="$(cd "$(dirname "$_qe_src")/.." && pwd)"
_qe_theme="${1:-Slate-Light}"
_qe_home="${2:-${TMPDIR:-/tmp}/slate-qt-home-$_qe_theme}"
_qe_root="${AGENT_DATA_DIR:-/mnt/nvme1/data/_custom/orca/workspaces}/Slate-theme-qt"
_qe_prefix="$_qe_root/prefix"

if [ ! -f "$_qe_prefix/plugins/styles/libkvantum.so" ]; then
    mkdir -p "$_qe_root" "$_qe_prefix/plugins/styles"
    [ -d "$_qe_root/kvantum-src" ] || git clone --depth 1 https://github.com/tsujan/Kvantum "$_qe_root/kvantum-src" >&2
    # Top-level project (the style dir has no cmake_minimum_required); only the `kvantum` target is built.
    cmake -S "$_qe_root/kvantum-src/Kvantum" -B "$_qe_root/build-kvantum" -G Ninja -DENABLE_QT5=OFF \
        -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DCMAKE_INSTALL_PREFIX="$_qe_prefix" >&2 &&
        ninja -C "$_qe_root/build-kvantum" kvantum >&2 &&
        cp "$_qe_root/build-kvantum/style/libkvantum.so" "$_qe_prefix/plugins/styles/libkvantum.so"
fi
if [ ! -x "$_qe_root/build-gallery/slate-qt-gallery" ]; then
    cmake -S "$_qe_repo/scripts/demo-qt" -B "$_qe_root/build-gallery" -G Ninja -DCMAKE_BUILD_TYPE=Release >&2 &&
        ninja -C "$_qe_root/build-gallery" >&2
fi
[ -d "$_qe_repo/dist/$_qe_theme" ] || (cd "$_qe_repo" && python3 build.py >&2)

mkdir -p "$_qe_home/.config/Kvantum/$_qe_theme"
cp -r "$_qe_repo/dist/$_qe_theme/kde/kvantum/$_qe_theme/." "$_qe_home/.config/Kvantum/$_qe_theme/"
printf '[General]\ntheme=%s\n' "$_qe_theme" >"$_qe_home/.config/Kvantum/kvantum.kvconfig"

# Same text as GTK (13px / 11px at 96 dpi): Inter 9.75pt and 8.25pt, one fontconfig for both toolkits.
printf '[General]\nfont=Inter,9.75,-1,5,50,0,0,0,0,0\nsmallestReadableFont=Inter,8.25,-1,5,50,0,0,0,0,0\n' >"$_qe_home/.config/kdeglobals"
mkdir -p "$_qe_home/.local/share" "$_qe_home/.cache"
ln -sfn "$HOME/.local/share/fonts" "$_qe_home/.local/share/fonts"
export FONTCONFIG_FILE="${FONTCONFIG_FILE:-$_qe_repo/scripts/pixdiff-fonts.conf}" SLATE_QT_FONT=1 QT_FONT_DPI=96
export HOME="$_qe_home" XDG_CONFIG_HOME="$_qe_home/.config"
export QT_PLUGIN_PATH="$_qe_prefix/plugins" QT_STYLE_OVERRIDE=kvantum
unset QT_QPA_PLATFORMTHEME
export SLATE_QT_GALLERY="$_qe_root/build-gallery/slate-qt-gallery"
unset _qe_src _qe_repo _qe_theme _qe_home _qe_root _qe_prefix
