# Slate sizing system

One size system for GTK3, GTK4, Kvantum (Qt), Aurorae and Plasma. The look is
compact modern macOS: Sequoia density, Tahoe shapes (unified title bar, round
traffic lights, soft radii), not the oversized Tahoe controls.

All values are in px at scale 1. Token names refer to `specs/tokens-proposed.json`.

## Rules

- **Base grid 4 px.** Heights, paddings, gaps and margins are multiples of 4.
- **Fine step 2 px.** Only radii, track thickness, insets inside a control, and
  hairlines may use the 2 px step (2, 6, 10).
- **One control height: 24** (`control_height`). Button, entry, search, spin,
  combo, segmented track, tab track, menu item, table row, menu-bar item all
  share it. Smaller: 20 (`control_height_sm`, segment inside a track). Larger:
  28 (sidebar row), 32 (pill button, toast), 36 (rich and boxed rows), 40 (title bar).
- **Concentric radii.** Outer radius = inner radius + padding between them.
  Segment 4 + 2 track inset = control 6. Menu item 6 + 4 menu padding = menu 10.
  Window 12. Check 4. Pill 999.
- **One gap: 8** between sibling controls (`spacing_m`). 4 between an icon or
  check and its label. 0 between linked or stacked rows (they touch).
- **Center everything vertically** in its row: margin = (row - child) / 2,
  computed from tokens, never typed as a literal (7px, 13px).
- **Icons 16** everywhere in controls and rows. 32 for large icons.
- **Fonts:** 13 body, 11 small, 13/600 title. Headings follow Apple macOS text
  styles: 26, 22, 17, 15, 13. KDE gets the same size in points: 9.75 pt = 13 px
  at 96 dpi, 8.25 pt = 11 px.

## Widget table

Columns: H = height, Pad = horizontal padding, R = radius, Gap = gap to the
neighbour, Font = size/weight, Icon = icon size. Apple and MacTahoe columns show
height / radius unless noted. Apple values are measured AppKit metrics
(Sequoia, then Tahoe after the slash); `~` marks an approximate value.

| Widget | H | Pad | R | Gap | Font | Icon | Apple ref | MacTahoe (laptop) | Slate |
|---|---|---|---|---|---|---|---|---|---|
| Title bar / header bar | 40 | 8 edge | 12 top | 8 | 13/600 | 16 | title bar 28; compact unified toolbar 38; unified 52 | 48 | 40, controls centered (8 above, 8 below) |
| Traffic lights | 12 dia | inset 12 left | circle | 8 | glyph 8 | - | 12 dia, 8 gap (20 c-c), inset ~8 title bar / ~20 unified | 16 cell, gap ~9, inset ~17 | 12, gap 8, inset 12, top (40-12)/2 = 14 |
| Toolbar / flat button | 24 | 4 icon, 12 text | 6 | 8 | 13/400 | 16 | toolbar item ~28 / Tahoe glass ~36 | 24 | 24 x 24 square for icon-only |
| Push button | 24 | 12 | 6 | 8 | 13/400 | 16 | ~21 / ~24 regular, r ~5 / capsule | 24, r 6 | 24 |
| Suggested / destructive | 24 | 12 | 6 | 8 | 13/400 | 16 | same as push, accent fill | 24, r 6 | same as push, fill only |
| Pill button | 32 | 16 | pill | 8 | 13/600 | 16 | large control 28 / 32 | 32 | 32 |
| Segmented control | 24 track, 20 segment | 12 | 6 track, 4 segment | 0 inside, 8 outside | 13/400 | 16 | ~22 / 24 | 24, r 6 | track inset 2 |
| Text entry | 24 | 8 | 6 | 8; icon-text 4 | 13/400 | 16 | ~22 / 24 | 24, r 6 | 24 |
| Search field | 24 | 8 | pill | 8; icon-text 4 | 13/400 | 16 | ~22 / 24 capsule | 24 | 24 pill |
| Spin button | 24 | 8 text | 6 | buttons 20 wide | 13/400 | 16 | stepper 13x22 / 24 | 28 | 24, step buttons 20 x 24 |
| Dropdown / combo | 24 | 8 left, 4 right | 6 | 8 | 13/400 | arrow 12 | popup ~21 / 24 | 24 | 24, arrow 12 |
| Checkbox | 16 | - | 4 | label 4 | 13/400 | - | 14 box (16 frame), r ~3 | 14 | 16 box, row 24 |
| Radio | 16 | - | circle | label 4 | 13/400 | - | 14 (16 frame) | 14 | 16, row 24 |
| Switch | 20 (36 wide) | knob inset 2 | pill | 8 | - | - | 38x22 regular, 32x18 small / ~42x24 | 42x18, knob 20x14 | 36 x 20, knob 16 |
| Slider | track 4, knob 16 | - | pill | 8 | 11 marks | - | track ~4, knob ~20 / pill knob | track 6, knob 30x20 | track 4, knob 16, row 24 |
| Progress bar | 6 | - | pill | 8 | 11 | - | ~6 | 6 | 6 |
| Level bar | 6 | - | pill | blocks 2 | - | - | ~6 continuous | 6 | 6, block gap 2 |
| Scrollbar | thumb 4 idle, 8 hover | margin 2 | pill | - | - | - | overlay ~7 idle, ~11 hover | 4 idle, 10 hover | 4 / 8 thumb, 8 / 12 total, min length 32 |
| Tabs (notebook, Qt tabs) | 24 track, 20 tab | 12 | 6 track, 4 tab | 0 | 13/400 | 16, close 16 | segmented style ~22 / 24 | 24 | same as segmented |
| List row | 24 | 8 | 6 | 0; list inset 4 | 13/400 | 16 | table row 24 (inset style) | 24-28 | 24 |
| Rich / boxed row | 36 | 12 | 10 group | 0 (1 px separator) | 13/400 | 16 | grouped form row ~40 / 44 | 36-44 | 36 |
| Sidebar row | 28 | 8; sidebar inset 8 | 6 | 0 | 13/400; header 11/600 | 16, icon-text 8 | 28 (medium), inset ~10, r ~5 / 8 | 28 | 28 |
| Table / tree row + header | 24 row, 24 header | 8 | 0 | 0 | row 13/400, header 11/600 | 16 | row 24, header ~28 | 24 | 24 / 24 |
| Menu | item 24 | 4 menu, 8 item | 10 menu, 6 item | separator 1 + 4/4, inset 8 | 13/400, accel 13 | 16, accel gap 12 | item 22 / ~24, inset 5, r 6 / ~12, sel r 4 | item 22-25, r 12-14 | 24, total separator 9 |
| Popover | content | 4 (menus), 8 (content) | 10 | - | 13/400 | 16 | r ~10 / ~16 | r 14-16 | 10 |
| Tooltip | 24 min | 8 (4 vert) | 6 | - | 11/400 | - | pad 4/6, r ~4 / ~8 | pad 6-7, r 12-14 | 4 x 8, r 6 |
| Dialog | content | 16 | 12 | buttons 8 | title 15/700, body 13 | 48 dialog icon | alert inset 20, button gap 12 | 12-18 | pad 16, button row 24, gap 8, trailing |
| Info bar | 24 controls | 12 (8 vert) | 0 | 8 | 13/400 | 16 | banner pad 8/12 | - | 8 x 12 |
| Expander | 24 title | 0 (4 vert) | - | arrow-label 4 | 13/400 | arrow 16 | disclosure 13 / 16 | - | 24 row |
| Calendar cell | 24 x 24 | 4 widget | 6 | 0 | 13/400, header 13/600, days 11/600 | 16 nav | date cell ~20-24 | - | 24 cell |
| Toast / notification | 32 | 12 left, 4 right | pill | margin 12 | 13/400 | 16 | banner r ~16, 344 wide | - | 32 pill; Plasma notification = Plasma popup |
| Plasma panel | 28 | 4 | 12 when floating | 8 | 13/400 | 16 | menu bar 24 / ~24 | - | 28, hint margin 4 |
| Plasma popup | content | 8 | 10 | items 0, inset 4 | 13/400 | 16 | Control Center r ~16 | r 14-16 | pad 8, view items 24, item pad 8 |

## Sources

- Apple HIG: Layout, Buttons, Toggles, Sliders, Menus, Sidebars, Windows,
  Typography (developer.apple.com/design/human-interface-guidelines). The HIG
  gives the 8/20 spacing rule and the text styles. It publishes no control
  heights.
- AppKit `NSControl.ControlSize` (mini, small, regular, large; `extraLarge`
  since macOS 26) and WWDC25 "Build an AppKit app with the new design":
  Tahoe controls are taller and rounder. Heights in the table are measured
  from Sequoia and Tahoe screenshots at 1x and are approximate.
- vinceliuice/MacTahoe-gtk-theme `src/sass/_variables.scss` and
  `src/sass/gtk/_common-4.0.scss`; vinceliuice/WhiteSur-gtk-theme
  `src/sass/_variables.scss`; vinceliuice/MacTahoe-kde
  `Kvantum/MacTahoe/MacTahoe.kvconfig` (read with `gh api`).

## Notes for Qt

- Kvantum uses `frame.*` as both padding and corner size. To get a radius
  larger than the padding, set `frame.expansion` (MacTahoe-kde uses
  expansion 12 for radius 6). Use this for Menu (frame 4, radius 10) and
  ToolTip (frame 4, radius 6).
- Kvantum padding = `frame` + `text.margin`. Example: menu item frame 6 +
  text margin 2 = 8.
- Qt has no switch widget and no tab track. Draw the track with
  `[TabBarFrame]` (frame 2, fill as the segmented track) so tabs match GTK.
- Kvantum transient scrollbars cannot show a thin idle thumb. Qt shows the
  8 px thumb on hover only.
