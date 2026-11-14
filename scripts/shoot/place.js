// KWin script used by scripts/shoot.sh inside the private compositor.
// Places the demo windows, keeps the wallpaper window at the bottom and
// prints every window geometry as "SLATE_WIN|class|caption|popup|dialog|x y w h"
// (logical px; frame x y w h, then client x y w h) so shoot.sh can crop popups.
// shoot.sh replaces __LAYOUT__ with window (center each window) or hero (overlap two).
const SCREEN = { w: 2400, h: 1500 };
const layout = "__LAYOUT__";
const HERO_SLOTS = [{ x: 110, y: 120 }, { right: 110, bottom: 120 }];
let slot = 0;

function geo(w) {
    const g = w.frameGeometry;
    const c = w.clientGeometry;
    return [g.x, g.y, g.width, g.height, c.x, c.y, c.width, c.height].map(Math.round).join(" ");
}

function report(w) {
    print("SLATE_WIN|" + w.resourceClass + "|" + w.caption + "|" + (w.popupWindow ? 1 : 0) + "|" +
          (w.dialog ? 1 : 0) + "|" + geo(w));
}

function target(w, s) {
    const g = w.frameGeometry;
    if (!s) return { x: (SCREEN.w - g.width) / 2, y: (SCREEN.h - g.height) / 2 };
    return {
        x: s.right !== undefined ? SCREEN.w - g.width - s.right : s.x,
        y: s.bottom !== undefined ? SCREEN.h - g.height - s.bottom : s.y,
    };
}

function manage(w) {
    if (String(w.resourceClass) === "org.slate.Bg") {
        w.noBorder = true;
        w.keepBelow = true;
        w.frameGeometry = { x: 0, y: 0, width: SCREEN.w, height: SCREEN.h };
        return;
    }
    if (w.popupWindow || w.dialog || w.specialWindow) {
        report(w);
        w.frameGeometryChanged.connect(function () { report(w); });
        return;
    }
    const s = layout === "hero" ? HERO_SLOTS[Math.min(slot++, HERO_SLOTS.length - 1)] : null;
    let last = "";
    function fit() {
        const g = w.frameGeometry;
        if (g.width < 100) return;
        const t = target(w, s);
        if (Math.round(g.x) !== Math.round(t.x) || Math.round(g.y) !== Math.round(t.y)) {
            w.frameGeometry = { x: Math.round(t.x), y: Math.round(t.y), width: g.width, height: g.height };
        }
        const now = geo(w);
        if (now !== last) { last = now; report(w); }
    }
    w.frameGeometryChanged.connect(fit);
    fit();
}

workspace.windowAdded.connect(manage);
workspace.windowList().forEach(manage);
