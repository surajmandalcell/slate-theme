# Motion

Slate moves like macOS Sequoia/Tahoe: most state changes are instant, a few
fade or zoom briefly, and nothing changes layout while it animates. GTK4 is
the reference; GTK3, Kvantum and KWin follow it as far as each can.

Tokens (`tokens.json`, `common`): `duration_fast` 120ms, `duration_release`
100ms, `duration_focus` 150ms, `duration_popover` 180ms, `duration_normal`
200ms, `popover_scale_from` 0.95, `check_scale_from` 0.7, `ease_standard`,
`ease_emphasized` (ease-out), `ease_spring` (small overshoot). KWin targets:
`kwin_window_ms` 200, `kwin_window_scale` 0.94, `kwin_minimize_ms` 350,
`kwin_popup_slide_ms` 200, `kwin_animation_factor` 0.7.

## Per interaction

| State | macOS | GTK4 | GTK3 | Qt (Kvantum) | KWin |
|---|---|---|---|---|---|
| Button hover | none (Tahoe toolbar items only) | color change, 100ms fade; the hover color itself is a pixel decision | same | `animate_states` fade, fixed timing | - |
| Button press | darken at once, fade back ~100ms on release | `button:active { transition-duration: 0 }`, base 100ms | same | `animate_states` fades both ways (no per-state timing) | - |
| Default button | steady accent, no pulse | no animation | same | no animation | - |
| Traffic light press | darken at once | `filter` instant in, 100ms out | color only | Aurorae | - |
| Checkbox / radio | fill at once, mark pops in | `transition: none`; `slate-check-in` scales the mark 0.7 -> 1 over 120ms `ease_spring` | same (`-gtk-icon-transform`) | `animate_states` fade | - |
| Switch | knob slides ~200ms ease-out, track crossfades with it | knob slide is GTK code (~100ms ease-out cubic), not themable; GTK sets `:checked` when the knob lands, so the track crossfade is 120ms | same | no switch widget (QtQuick switches use Kirigami durations x factor) | - |
| Slider knob | follows the pointer, no motion | shadow 120ms; position is code | same | - | - |
| Focus ring | fades in ~150ms, grows from the control edge | `slate-focus-in`: outline 0 -> 3px and transparent -> ring color, 150ms; entries fade their box-shadow ring 150ms | same on `:focus` | `animate_states` fades the focus frame | - |
| List / sidebar / menu item highlight | instant | `transition: none` on rows and model buttons | rows, model buttons, menu items | instant (Kvantum does not animate menu items) | - |
| Menus | appear at once, fade out ~200ms | `popover.menu > contents { animation: none }`; dismiss fade is impossible (the surface unmaps at once) | GTK3 popover fade/slide is code; menus are separate windows | - | `fadingpopups`: in 150 x 0.7 = 105ms, out 600 x 0.7 = 420ms OutQuart (no config keys) |
| Popovers | fade + scale from 0.95 at the anchor ~180ms | `slate-popover-in` 180ms `ease_emphasized`, `transform-origin: top center` (GTK4 gives no arrow-side class) | no CSS `transform`; GTK3's built-in fade + slide | - | `slidingpopups` for Plasma popups, 200ms target |
| Tooltips | delayed fade in | delay is GTK's (500ms); `slate-fade-in` 120ms | same | `tooltip_delay=500` | `fadingpopups` |
| Window open / close | zoom from ~0.94 + fade ~200ms | - | - | - | `scale`: `Duration`, `InScale`/`OutScale` 0.94 |
| Minimize | genie ~350ms | - | - | - | `magiclamp`: `AnimationDuration` |
| Maximize | smooth zoom | - | - | - | `maximize`: 250 x factor = 175ms OutCubic (no key) |
| Workspace switch | slide | - | - | - | `slide` (500 x factor = 350ms; no duration key) |
| Scrollbars | appear on scroll, hide after ~1s, widen on hover | overlay indicator show/hide is GTK code; widen 4 -> 8px over 200ms (overlay, so content does not move) | same | `transient_scrollbar=true` (Kvantum's own timing) | - |

KWin multiplies every effect duration by `AnimationDurationFactor`, so
`apply-kde.sh` writes `round(target / factor)` (for example 200 / 0.7 = 286).

## Not possible

- GTK CSS cannot set the switch knob's slide duration or curve, a spring on
  it, the overlay scrollbar fade, the tooltip delay (GTK4), or any exit
  animation of a popover or menu.
- GTK3 has no CSS `transform` or `filter`.
- Kvantum has one built-in animation timing (`animate_states` on or off) and
  no menu fade.
- KWin `fadingpopups`, `maximize` and `slide` have no duration keys; only
  the global factor changes them.
