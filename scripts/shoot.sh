#!/bin/zsh
# Real screenshots of the Slate theme inside a private nested KWin (Wayland):
# real Aurorae decorations, rounded corners, shadows, a wallpaper.
#   scripts/shoot.sh [Slate-Light|Slate-Dark ...]
# Writes preview/hero-{light,dark}.png and preview/widgets/<id>-<gtk4|gtk3|qt>-<light|dark>.png
# (plus window-<toolkit>-<mode>.png). Everything runs on a private D-Bus session with a temp
# HOME under $AGENT_DATA_DIR/Slate-theme-shots, so the live desktop and ~/.config are never touched.
# Needs kwin_wayland, spectacle, imagemagick, PyGObject (GTK3 and GTK4), jq. Qt is added when
# scripts/qt-env.sh and scripts/demo-qt exist (they build Kvantum and the gallery on first use).
set -u
setopt null_glob
ROOT=${0:A:h:h}
SHOTS=${AGENT_DATA_DIR:-/mnt/nvme1/data/_custom/droid}/Slate-theme-shots
SELF=${0:A}
W=2400 H=1500   # logical screen size; the compositor runs at scale 2, so captures are 4800x3000

# ---------------------------------------------------------------- inner: runs inside dbus-run-session
if [[ ${1:-} == --inner ]]; then
    name=$2
    mode=${${name#Slate-}:l}
    home=$SHOTS/home-$name
    run=$SHOTS/run-$name
    work=$SHOTS/work-$name
    out=$ROOT/preview/widgets
    klog=$work/kwin.log
    sock=slate-shot-$name
    # never talk to the owner's session bus
    [[ ${DBUS_SESSION_BUS_ADDRESS:-} != "$ORIG_BUS" && -n ${DBUS_SESSION_BUS_ADDRESS:-} ]] || { echo "refusing: not a private bus" >&2; exit 1; }
    unset DISPLAY WAYLAND_DISPLAY
    export HOME=$home XDG_CONFIG_HOME=$home/.config XDG_DATA_HOME=$home/.local/share XDG_CACHE_HOME=$home/.cache
    export XDG_RUNTIME_DIR=$run XDG_SESSION_TYPE=wayland
    export QT_FORCE_STDERR_LOGGING=1 QT_LOGGING_RULES='kwin_scripting.debug=true'
    export GTK_A11Y=none NO_AT_BRIDGE=1 GTK_USE_PORTAL=0 GDK_DEBUG=no-portals GSK_RENDERER=cairo GSETTINGS_BACKEND=keyfile
    : > $klog

    pids=()
    cleanup() { for p in $pids; do kill $p 2>/dev/null; done; }
    trap cleanup EXIT

    kwin_wayland --virtual --width $W --height $H --scale 2 --socket $sock --xwayland >> $klog 2>&1 &
    pids+=($!)
    for i in {1..100}; do [[ -S $run/$sock ]] && break; sleep 0.2; done
    [[ -S $run/$sock ]] || { echo "kwin did not start, see $klog" >&2; exit 1; }
    sleep 2
    export WAYLAND_DISPLAY=$sock
    # --scale does not reach the output in virtual mode: set it through the output management protocol
    kscreen-doctor output.Virtual-0.scale.2 >> $work/kscreen.log 2>&1
    sleep 1

    load_place() {  # $1 = window | hero
        qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript slate-place >/dev/null 2>&1
        sed "s/__LAYOUT__/$1/" $ROOT/scripts/shoot/place.js > $work/place-$1.js
        local id=$(qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript $work/place-$1.js slate-place)
        qdbus6 org.kde.KWin /Scripting/Script$id org.kde.kwin.Script.run >/dev/null
    }

    GDK_BACKEND=wayland GTK_THEME=Adwaita python3 $ROOT/scripts/shoot/bg.py $work/wallpaper.png >> $work/bg.log 2>&1 &
    bgpid=$!
    pids+=($bgpid)
    load_place window
    sleep 3

    have_qt=0
    [[ -f $ROOT/scripts/qt-env.sh && -f $ROOT/scripts/demo-qt/main.cpp ]] && have_qt=1
    toolkits=(gtk4 gtk3)
    (( have_qt )) && toolkits+=(qt)

    # launch <toolkit> [app args]; leaves the pid in $apid
    launch() {
        local tk=$1; shift
        case $tk in
            gtk4) GDK_BACKEND=wayland GTK_THEME=$name python3 $ROOT/scripts/demo-gtk4.py "$@" >> $work/app.log 2>&1 & ;;
            gtk3) GDK_BACKEND=wayland GTK_THEME=$name python3 $ROOT/scripts/demo-gtk3.py "$@" >> $work/app.log 2>&1 & ;;
            qt)   bash $ROOT/scripts/shoot/qt-run.sh $name $home --mode $mode "$@" >> $work/app.log 2>&1 & ;;
        esac
        apid=$!
    }

    capture() {  # $1 = png
        spectacle -b -n -f -o $1 >> $work/spectacle.log 2>&1
        [[ -s $1 ]] || { echo "capture failed: $1" >&2; return 1; }
    }

    # phase <toolkit> [window|menu|popover|tooltip|dialog]
    phase() {
        local tk=$1 show=$2 bj=$work/$1-$2.json cap=$work/$1-$2.png
        local n0=$(wc -l < $klog)
        rm -f $bj
        echo "PHASE $tk $show" >> $klog
        if [[ $show == window ]]; then launch $tk --bounds $bj; else launch $tk --show $show --bounds $bj; fi
        for i in {1..100}; do [[ -s $bj ]] && break; sleep 0.3; done
        [[ -s $bj ]] || echo "no bounds for $tk $show" >&2
        sleep 3
        capture $cap || { kill $apid 2>/dev/null; return 1; }
        kill $apid 2>/dev/null; wait $apid 2>/dev/null
        tail -n +$((n0 + 1)) $klog | grep 'SLATE_WIN|' > $work/win-$tk-$show.log
        if [[ $show == window ]]; then
            python3 $ROOT/scripts/shoot/crops.py $cap $work/win-$tk-$show.log $tk $mode $out $bj
        else
            python3 $ROOT/scripts/shoot/crops.py $cap $work/win-$tk-$show.log $tk $mode $out $show $bj || echo "no $show crop for $tk" >&2
        fi
        sleep 1
    }

    for tk in $toolkits; do
        [[ -n ${HERO_ONLY:-} ]] && break
        for show in window menu popover tooltip dialog; do
            # Qt popups (menu, tooltip) need an input-device grab, which the nested compositor has none of
            # (they never map); the Qt gallery has no popover. Those three ids exist for GTK only.
            [[ $tk == qt && $show == (popover|menu|tooltip) ]] && continue
            phase $tk $show
        done
    done

    # hero: a Finder-like GTK4 window behind a real Dolphin window (Kvantum), both in this mode
    load_place hero
    for d in Desktop Documents Downloads Music Pictures; do mkdir -p $home/$d; done
    for d in Design Photos Music Projects Videos Archive; do mkdir -p $home/Documents/$d; done
    for f in Slate.pdf tokens.json Notes.txt Cover.png Budget.ods Talk.mp3 Roadmap.odt Logo.svg Release.zip Demo.mp4 Install.sh Palette.png; do
        : > $home/Documents/$f
    done
    # only the user folders in Dolphin's Places; never the host's disks or network
    mkdir -p $home/.local/share
    sed "s#__HOME__#$home#g" $ROOT/scripts/shoot/user-places.xbel > $home/.local/share/user-places.xbel
    # the cover is the 1440 x 900 middle of the screen: the photo fills that crop, not the whole screen
    kill $bgpid 2>/dev/null
    GDK_BACKEND=wayland GTK_THEME=Adwaita python3 $ROOT/scripts/shoot/bg.py $work/wallpaper-hero.png >> $work/bg.log 2>&1 &
    pids+=($!)
    # macOS-style icons (WhiteSur) for both apps; the outer script installs them into $SHOTS/icons
    if [[ -d $SHOTS/icons/WhiteSur ]]; then
        mkdir -p $home/.local/share/icons
        ln -sfn $SHOTS/icons/WhiteSur $home/.local/share/icons/WhiteSur
        ln -sfn $SHOTS/icons/WhiteSur-dark $home/.local/share/icons/WhiteSur-dark
        icons=WhiteSur; [[ $mode == dark ]] && icons=WhiteSur-dark
        sed -i "s/^gtk-icon-theme-name=.*/gtk-icon-theme-name=$icons/" $home/.config/gtk-4.0/settings.ini
        export SLATE_ICON_THEME=$icons   # qt-env.sh rewrites kdeglobals and adds it there
    fi
    # Dolphin like Finder: 64 px icons, no status bar, Finder's toolbar buttons only
    printf '[General]\nShowStatusBar=Disabled\n\n[PlacesPanel]\nIconSize=16\n\n[IconsMode]\nIconSize=64\nPreviewSize=64\n' > $home/.config/dolphinrc
    mkdir -p $home/.local/share/kxmlgui5/dolphin
    cp $ROOT/scripts/shoot/dolphinui.rc $home/.local/share/kxmlgui5/dolphin/dolphinui.rc
    sleep 2
    # Dolphin first (behind, top left), then the GTK4 window in front with focus (bottom right)
    if (( have_qt )); then
        bash $ROOT/scripts/shoot/qt-app.sh $name $home dolphin --new-window $home/Documents >> $work/app.log 2>&1 &
    else
        launch gtk3
    fi
    hero_a=$!; sleep 8
    GDK_BACKEND=wayland GTK_THEME=$name python3 $ROOT/scripts/shoot/showcase-gtk4.py >> $work/app.log 2>&1 &
    hero_b=$!; sleep 5
    capture $work/hero.png && magick $work/hero.png -crop 2880x1800+960+600 +repage -quality 90 $ROOT/preview/hero-$mode.jpg
    kill $hero_a $hero_b 2>/dev/null
    pkill -f "dolphin --new-window $home" 2>/dev/null
    exit 0
fi

# ---------------------------------------------------------------- outer: prepare per-mode homes
cd $ROOT
modes=(Slate-Light Slate-Dark)
(( $# )) && modes=($@)
mkdir -p $ROOT/preview/widgets $SHOTS
pgrep -f 'kwin_wayland --virtual.*slate-shot' >/dev/null && { echo "a slate-shot compositor already runs" >&2; exit 1; }

for name in $modes; do
    mode=${${name#Slate-}:l}
    home=$SHOTS/home-$name
    work=$SHOTS/work-$name
    [[ -n $SHOTS && $SHOTS == */Slate-theme-shots ]] || exit 1
    rm -rf $home $work $SHOTS/run-$name
    mkdir -p $home/.config/gtk-3.0 $home/.config/gtk-4.0 $home/.cache $work $SHOTS/run-$name
    chmod 700 $SHOTS/run-$name
    sh $ROOT/install.sh --prefix $home > $work/install.log 2>&1 || { echo "install failed, see $work/install.log" >&2; exit 1; }

    printf '[General]\nColorScheme=%s\n\n[KDE]\nwidgetStyle=kvantum\n' $name > $home/.config/kdeglobals
    printf '[org.kde.kdecoration2]\nlibrary=org.kde.kwin.aurorae.v2\ntheme=__aurorae__svg__%s\nButtonsOnLeft=XIA\nButtonsOnRight=\nBorderSize=None\nBorderSizeAuto=false\n\n[Plugins]\nkwin4_effect_shapecornersEnabled=true\n\n[Round-Corners]\nSize=12\nInactiveCornerRadius=12\nOutlineThickness=0\nInactiveOutlineThickness=0\nSecondOutlineThickness=0\nInactiveSecondOutlineThickness=0\nOuterOutlineThickness=0\nInactiveOuterOutlineThickness=0\nUseNativeDecorationShadows=true\n' $name > $home/.config/kwinrc
    # Aurorae has no bottom border (BorderSize=None) and KWin 6.8 cannot round a client by itself, so the
    # bottom corners come from the shapecorners effect, as scripts/apply-kde.sh sets it (outlines off).
    # GTK3 on Wayland takes the button layout from GSettings, not settings.ini
    mkdir -p $home/.config/glib-2.0/settings
    printf "[org/gnome/desktop/wm/preferences]\nbutton-layout='close,minimize,maximize:'\n\n[org/gnome/desktop/interface]\ngtk-theme='%s'\n" $name > $home/.config/glib-2.0/settings/keyfile
    for v in 3.0 4.0; do
        printf '[Settings]\ngtk-theme-name=%s\ngtk-icon-theme-name=breeze\ngtk-decoration-layout=close,minimize,maximize:\ngtk-application-prefer-dark-theme=%s\n' \
            $name $([[ $mode == dark ]] && echo 1 || echo 0) > $home/.config/gtk-$v/settings.ini
    done

    # wallpaper: assets/wallpaper.jpg (apple blossom) in its own tone, dimmed in dark mode; the hero copy
    # puts the whole photo in the 1440 x 900 cover crop (2880 x 1800 device px at the screen centre)
    tone=(); [[ $mode == dark ]] && tone=(-modulate 70)
    magick $ROOT/assets/wallpaper.jpg -resize $((W * 2))x$((H * 2))^ -gravity center -extent $((W * 2))x$((H * 2)) \
        $tone $work/wallpaper.png
    magick $ROOT/assets/wallpaper.jpg -resize 2880x1800^ -gravity center -extent 2880x1800 $tone \
        -background black -extent $((W * 2))x$((H * 2)) $work/wallpaper-hero.png
    # WhiteSur icons (GPL-3, github.com/vinceliuice/WhiteSur-icon-theme) for the cover, installed once
    if [[ ! -d $SHOTS/icons/WhiteSur ]]; then
        git clone -q --depth 1 https://github.com/vinceliuice/WhiteSur-icon-theme.git $SHOTS/whitesur-src &&
            bash $SHOTS/whitesur-src/install.sh -d $SHOTS/icons > $SHOTS/icons.log 2>&1
    fi

    [[ -n ${HERO_ONLY:-} ]] || rm -f $ROOT/preview/widgets/*-$mode.png
    rm -f $ROOT/preview/hero-$mode.png $ROOT/preview/hero-$mode.jpg
    ORIG_BUS=${DBUS_SESSION_BUS_ADDRESS:-} timeout 600 dbus-run-session -- zsh $SELF --inner $name > $work/session.log 2>&1
    sleep 2   # let the nested kwin exit before the next mode
    [[ -n ${HERO_ONLY:-} ]] || zsh $ROOT/scripts/shoot/compare.sh $mode
    echo "$name: exit $?, $(ls $ROOT/preview/widgets/*-$mode.png 2>/dev/null | wc -l) crops, log $work/session.log"
done
pgrep -fa 'slate-shot' | grep -v pgrep && echo "leftover processes" >&2
exit 0
