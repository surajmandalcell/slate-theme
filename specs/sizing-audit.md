# Slate sizing audit

Every size in the sources that breaks `specs/sizing.md`, or where GTK and Qt
disagree. Line numbers are for the current tree. "Current" is the rendered
value; "Proposed" names the token from `specs/tokens-proposed.json`.

Paths:
G3 = `gtk/gtk-3.0/gtk.css.in`, G4 = `gtk/gtk-4.0/gtk.css.in`,
KV = `kde/kvantum/__NAME__/__NAME__.kvconfig.in`, KS = `kde/kvantum/__NAME__/__NAME__.svg.in`,
AU = `kde/aurorae/__NAME__/`, PL = `kde/plasma/desktoptheme/__NAME__/`.

Before switching to the proposed tokens, replace every `{{spacing_s}}` (6 px,
off grid): 17 uses in G3, 12 in G4, 16 in PL. The proposed file drops
`spacing_s`, so the build fails loudly on any use left over.

## Cross-toolkit mismatches (fix first)

| # | Widget | GTK3 | GTK4 | Qt / KDE | Proposed (all) |
|---|---|---|---|---|---|
| 1 | Traffic light left inset | G3:154 + G3:348: 6 + 4 = 10 | G4:129 + G4:158 + G4:163: 8 + 12 + 4 = 24 | AU rc:30 TitleEdgeLeft 12 | 12: G3 header pad 8 + 4; G4:158 `margin: 0` |
| 2 | Header bar height | G3:144,153 38 | G4:128,145 38 | AU rc:13,17,26 38; ButtonMarginTop 13 literal (rc:44-45) | `headerbar_height` 40; derive ButtonMarginTop = 14 |
| 3 | Text button side padding | G3:185,215 `10px` literal | G4:201 8 | KV:106-124 frame 6 + text 6 = 12 | `spacing_l` 12 |
| 4 | Icon button side padding | G3:214 4 | G4:243 6 | KV:131-133 PanelButtonTool frame 6 + text 3 = 9 (34 px wide) | `spacing_xs` 4 (24 x 24); KV frame 4 + `frame.expansion=12`, text 0 |
| 5 | Checkbox / radio size | G3:460-461, 501-502 14 | G4:320-322 16 | KV:41 check_size 14; KS:482-486 14 boxes | `check_size` 16 |
| 6 | Check-label gap | G3:462 6, G3:503 4 | G4:323 2 each side | Qt fixed ~4 | `spacing_xs` 4 (margin 0 4 0 0) |
| 7 | Check row height | G3: no padding (16) | G4:349 2 0 (20) | KV:168,175 min_height 0 | pad 4 0 (row 24) |
| 8 | Progress bar thickness | G3:594-595 6 | G4:411-415 4 | KV:13 progressbar_thickness 5 | `progress_height` 6 |
| 9 | Scrollbar thumb, hover | G3:637-640 6 + 3 border = 12 | G4:430-432 6 + 2 = 10 | KV:28 scroll_width 8 | thumb 8 + margin 2 = 12 |
| 10 | Scrollbar thumb, idle | G3:651-653 2 + 2 border | G4:441 3 + 2 | KV:368 transient only | `scrollbar_thumb` 4, margin 2 |
| 11 | Scrollbar min length | G3:646-647 32 | G4:438-439 32 | KV:29 36 | `scrollbar_min_length` 32 |
| 12 | Slider knob centering | G3:572,580,590 -6 (correct) | G4:397 -8 (knob off center) | KS:492-493 knob r 7 = 14 px | margin -6; knob 16 everywhere |
| 13 | Menu radius | G3:880,885 10 | G4:596 10 | KV:451-454 frame 5; KS:186-193 literal r 5 | 10: KV frame 4 + `frame.expansion=20`, KS r 10 |
| 14 | Menu item height | G3:849,888 22 | G4:311,604 22 | KV:405 22 | `menu_item_height` 24 |
| 15 | Menu item padding | G3:851,889 8 | G4:312,606 8 | KV:397-404 frame 5 + text 6 = 11, top/bottom 1 | 8: KV frame 6 + text 2, top/bottom 0 |
| 16 | Menu item radius | G3:854,892 5 | G4:314,608 5 | KV:401-404 5; KS:202-209 literal 5 | `radius_control` 6 (merge `radius_menu_item`) |
| 17 | Menu separator | G3:886, 908 1 + 4/4, inset 4 | G4:625 inset 8 | KV:59 menu_separator_height 5 | 1 + 4/4 = 9, inset 8 |
| 18 | Menu-bar item | G3:917 r 6, pad 8 | G4:636 r 5, pad 8 | KV:419-424 frame 5 + text 4 = 9 | r 6, pad 8 (KV frame 6 + text 2) |
| 19 | Tabs | G3:274-278 20 in 2 px track, pad 12, r 5 | G4:495-498 same | KV:216-222 text 10 + frame 6 = 16, h 24, no track (KV:235) | segment 20, pad 12, r 4; KV text 6, min_height 20, `[TabBarFrame] frame=true` frame 2 |
| 20 | Table header | G3:716-723 24, 11/600, view_bg | G4:545-551 24, 13/600, window_bg | KV:251-254 text 6 | 24, 11/600, view_bg, pad 8 |
| 21 | List / item view row padding | G3:742 8 | G4:523 8; G4:543 cell 6 more (14) | KV:323-331 frame 5 + text 1 = 6; PL widgets/viewitem.svg.in:43-56 16 | 8: G4 cell 0 4 with row 0 4; KV frame 6 + text 2; PL `spacing_m` |
| 22 | Item view radius | G3:745 6 | G4:525 6 | KV:323-326 5; PL viewitem.svg.in:2-5 5 | `radius_control` 6 |
| 23 | Tooltip padding | G3:949 4 x 8 | G4:646 4 x 8 | KV:477-482 frame 6, text 0 (6 x 6); PL tooltip ok | KV frame 4 + `frame.expansion=12`, text.margin.left/right 4 |
| 24 | Layout spacing | headerbar child spacing unset (GTK default 6) | same | KV:10 toolbar_item_spacing 2, KV:46 layout_spacing 6 | 8 (G4 `headerbar > box { border-spacing: 8px }`; KV 8) |
| 25 | Container margin | G3:969 16, G3:966/972/973 8-12 | G4:655,660 12 | KV:47 layout_margin 8 | dialogs 16 (`spacing_xl`); KV layout_margin 12 |
| 26 | Splitter handle | G3:815 wide 5 | - | KV:27 splitter_width 7 | 4 (wide); 1 px line otherwise |
| 27 | Combo arrow | G3:330-331 14 | G4:305 12 | KV:444 indicator 9; KS:459-461 9 box | 12 |
| 28 | Combo padding | G3:326 0 6 0 8 | G4:303 0 6 0 8 | KV:445 text right 2 + frame 6 | 0 4 0 8 |
| 29 | Focus ring | G3:45-47 2 inset; G3:202 3 r 8; G3:494,536,583,759 2 | G4:124 2 offset 1; G4:214,350,369,409 3 | Kvantum: none | `focus_ring_width` 3, offset 0, radius = widget radius |
| 30 | Font size | 13 px | 13 px | scripts/apply-kde.sh:20 `font_size=10` pt (13.3 px); :79 small 9 pt (12 px) | `font_size_kde_pt` 9.75, `font_size_small_kde_pt` 8.25 |

## GTK3 only (G3)

| # | Line | Current | Proposed |
|---|---|---|---|
| 31 | 72-75 | headings 24/22/18/15 literals | `font_size_large_title` 26, `title1` 22, `title2` 17, `title3` 15 |
| 32 | 118 | shadow margin `24px 36px 48px 36px` literal | `shadow_pad_top/side/bottom` (shared with AU rc:21-24) |
| 33 | 154 | header bar padding 6 | `spacing_m` 8 |
| 34 | 218 | arrow button 20 literal | `control_height_sm` |
| 35 | 261 | segmented track pad 2 literal | `spacing_2xs` |
| 36 | 274 | segment 20 literal | `control_height_sm` |
| 37 | 278 | segment radius 5 | `radius_inner` 4 |
| 38 | 338-339 | menu-button arrow 12 literal | 12 via token, same as combo |
| 39 | 421-422 | entry icon gap 6 | `spacing_xs` 4 |
| 40 | 435 | spin step button 20 literal | `control_height_sm` |
| 41 | 518-519 | switch 40 x 20 | 36 x 20 |
| 42 | 540-542 | knob 18, margin 1 | `switch_knob` 16, `switch_inset` 2 |
| 43 | 518 | switch has no vertical margin (G4 has 2) | margin 2 0 (box 24) |
| 44 | 641, 656 | scrollbar radius 8 literal | `radius_pill` |
| 45 | 675 | notebook header pad 6 x 8 | 8 x 8 |
| 46 | 762 | rich-list row 32 | `rich_row_height` 36 |
| 47 | 764 | row + row gap 1 | 0 |
| 48 | 772-775 | sidebar row 24, margin 1 x 6 | `sidebar_row_height` 28, margin 0 8 |
| 49 | 791-792 | extra place-sidebar padding 6 + label 4 | 0 (row padding 8 is enough) |
| 50 | 793 | sidebar icon gap 6 | 8 |
| 51 | 803 | stack-sidebar margin 1 x 6 | 0 8 |
| 52 | 841 | popover separator inset 4 | 4 8 |
| 53 | 850 | model button min width 80 (G4 40) | 80 both |
| 54 | 924-925 | app notification pad 6 x 12, no height | 32 high, pad 0 12, same as G4 toast |
| 55 | 954 | info bar pad 6 x 8 | 8 x 12 |
| 56 | 966, 969, 972, 973 | dialog areas 8/12/16 mixed | 16 all sides, button gap 8 |
| 57 | 970 | dialog title 15 literal | `font_size_title3` |
| 58 | 977, 1058, 1064 | path-bar, font, color, emoji buttons pad 6 | 8 |
| 59 | 984 | calendar pad 4, cells unset | pad 4, cell min 24 x 24 |
| 60 | 1007 | toolbar pad 4 x 6 | 4 x 8 |
| 61 | 836-837 | popover arrow 14 literal | 12 (on fine step, matches combo arrow) |

## GTK4 only (G4)

| # | Line | Current | Proposed |
|---|---|---|---|
| 62 | 104-107 | title-1 24, title-2 18 (G3 has 22, 18) | 22, 17 via tokens |
| 63 | 155 | `.toolbar` pad 6 | 4 x 8 |
| 64 | 158 | windowcontrols margin 12 (adds to header pad) | 0 |
| 65 | 241 | pill 32 literal | `control_height_lg` |
| 66 | 283, 285-286 | search entry icon gap 6 | 4 |
| 67 | 293 | spin step 20 literal | `control_height_sm` |
| 68 | 313 | dropdown item margin 1 0 | 0 |
| 69 | 355-358 | switch width `2 x 18 + 4` = 40 | `switch_width` 36 |
| 70 | 373 | knob margin 1 | `switch_inset` 2 |
| 71 | 454 | notebook header pad 4 x 6 | 8 x 8 |
| 72 | 471 | tab-bar tab margin `7px` literal | `calc((headerbar_height - control_height) / 2)` = 8 |
| 73 | 486, 495, 498 | segmented pad 2 literal, segment radius 5 | `spacing_2xs`, `radius_inner` 4 |
| 74 | 510 | view-switcher margin `7px` literal | same calc = 8 |
| 75 | 542, 562 | row + row gap 1 | 0 |
| 76 | 561 | boxed-list row 32 | `rich_row_height` 36 |
| 77 | 564-567 | places-sidebar row 24, margin 1 0 | 28, margin 0 8 |
| 78 | 569 | sidebar row `row_height` | `sidebar_row_height` |
| 79 | 587 | stack-sidebar margin `1px 6px` literal | 0 8 |
| 80 | 602 | inline menu buttons 28 | 24 |
| 81 | 605 | model button min width 40 | 80 |
| 82 | 655, 660 | dialog areas 12 | 16 |
| 83 | 658 | dialog title 15 literal | `font_size_title3` |
| 84 | 666-672 | toast has no height | min-height 32 |
| 85 | 681 | info bar pad 6 x 12 | 8 x 12 |
| 86 | 690, 695, 700 | adw rows 36 literal | `rich_row_height` |
| 87 | 705 | status page title 20 | `font_size_title1` 22 |
| 88 | 717 | calendar pad 6 | 4, cells 24 x 24 |

## Kvantum only (KV, KS)

| # | Line | Current | Proposed |
|---|---|---|---|
| 89 | KV:11 | toolbar_interior_spacing 2 | 4 |
| 90 | KV:106-109 | button frame bottom 7, others 6 (text 0.5 px high) | 6 all; keep the shadow inside the 6 px tile |
| 91 | KV:112 | button arrow indicator 9 | 12 |
| 92 | KV:183-186 | GenericFrame 4 (GTK frame radius 6, G3:1035) | `radius_control` 6 |
| 93 | KV:280-283 | slider groove frame 3 for a 4 px track | 2 (`slider_track` / 2) |
| 94 | KS:1-50, 55-80 | button, tbutton corner tiles drawn with literal radius 6 | template the radius or note the lock to `radius_control` |
| 95 | KS:186-209 | menu and menu-item corner tiles literal radius 5 | 10 and 6 |
| 96 | KS:482-486 | check, radio drawn at 14 | 16 |
| 97 | KS:492-493 | slider knob r 7 in a 16 tile | r 7.5 + 0.5 stroke = 16 |

## Aurorae (AU) and Plasma (PL)

| # | Location | Current | Proposed |
|---|---|---|---|
| 98 | AU `__NAME__rc.in`:37-38 | TitleBorderLeft 8 / Right 72 literals derived from traffic sizes | derive from tokens: Right = Left + 3 x size + 2 x gap + margin |
| 99 | AU `__NAME__rc.in`:44-45 | ButtonMarginTop 13 literal | `(headerbar_height - traffic_size) / 2` = 14 |
| 100 | AU `close/minimize/maximize/restore.svg.in` | 12 px cells and r 5.75 literal | template from `traffic_size` |
| 101 | AU `decoration.svg.in`:5-6 | corner pieces 12 wider than padding, literal | tie to `radius_window` |
| 102 | PL `widgets/background.svg.in`:53-56, `dialogs/background.svg.in`:53-56, `solid/*/background.svg.in`:53-56 | hint margins `spacing_s` 6 | `spacing_m` 8 |
| 103 | PL `widgets/viewitem.svg.in`:2-5 | 5 px side inset literal, radius 5 | inset 4 (`spacing_xs`), radius 6 |
| 104 | PL `widgets/viewitem.svg.in`:43-56 | hint left/right `spacing_xl` 16 | `spacing_m` 8 (GTK row padding) |
| 105 | `scripts/apply-kde.sh` | panel height not set | `panel_height` 28 |

Correct already (no change): control height 24, row height 24, window radius
12, popover radius 10 (GTK, Plasma), tooltip radius 6, list inset 4, slider
track 4, level bar 6, tab close 16, traffic size 12 and gap 8, entry padding 8,
Plasma panel hint margin 4, Kvantum LineEdit padding (6 + 2 = 8).

Total: 105 findings (30 cross-toolkit, 31 GTK3, 27 GTK4, 9 Kvantum, 8 Aurorae and Plasma).
