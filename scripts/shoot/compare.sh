#!/bin/zsh
# Side-by-side sheets from preview/widgets: GTK4 | GTK3 | KDE (Qt), one per widget id and mode.
#   compare.sh light|dark
# Writes preview/compare/<id>-<mode>.png and window-<mode>.png. Every crop keeps its 2x scale;
# cells share one background colour (taken from the GTK4 crop) and are centred in equal boxes.
set -u
setopt null_glob
ROOT=${0:A:h:h:h}
mode=$1
src=$ROOT/preview/widgets
dst=$ROOT/preview/compare
mkdir -p $dst
tks=(gtk4 gtk3 qt)
labels=("GTK4" "GTK3" "KDE (Qt)")
if [[ $mode == light ]]; then fg='#1d1d1f'; else fg='#f5f5f7'; fi

ids=()
for f in $src/*-gtk4-$mode.png $src/*-gtk3-$mode.png $src/*-qt-$mode.png; do
    n=${f:t}; n=${n%-gtk4-$mode.png}; n=${n%-gtk3-$mode.png}; n=${n%-qt-$mode.png}
    (( ${ids[(Ie)$n]} )) || ids+=($n)
done

for id in $ids; do
    first=$src/$id-gtk4-$mode.png; [[ -f $first ]] || first=$src/$id-gtk3-$mode.png
    bg=$(magick $first -format '%[pixel:p{2,2}]' info:)
    w=0; h=0
    for tk in $tks; do
        f=$src/$id-$tk-$mode.png; [[ -f $f ]] || continue
        read cw ch < <(magick identify -format '%w %h' $f)
        (( cw > w )) && w=$cw
        (( ch > h )) && h=$ch
    done
    cells=()
    i=1
    for tk in $tks; do
        f=$src/$id-$tk-$mode.png
        if [[ -f $f ]]; then
            magick $f -background $bg -gravity center -extent ${w}x${h} $dst/.cell.png
        else
            magick -size ${w}x${h} xc:$bg -font DejaVu-Sans -pointsize 26 -fill $fg -gravity center -annotate 0 'not available' $dst/.cell.png
        fi
        magick -size ${w}x70 xc:$bg -font DejaVu-Sans -pointsize 30 -fill $fg -gravity center -annotate 0 $labels[$i] \
            $dst/.cell.png -append $dst/.col$i.png
        i=$((i + 1))
    done
    magick $dst/.col1.png $dst/.col2.png $dst/.col3.png -background $bg +append $dst/$id-$mode.png
done
rm -f $dst/.cell.png $dst/.col1.png $dst/.col2.png $dst/.col3.png
echo "compare $mode: $(ls $dst/*-$mode.png | wc -l) sheets"
