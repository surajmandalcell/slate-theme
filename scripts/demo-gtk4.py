#!/usr/bin/env python3
"""GTK4 widget gallery for screenshots of the Slate theme (scripts/shoot.sh).

Every widget carries its gallery id as widget name, the same ids as the Qt
gallery. Flags:
  --bounds FILE   write {"window":[x,y,w,h], "<id>":[x,y,w,h]} (logical px,
                  relative to the visible window frame) once the window is up
  --show WHAT     open a transient surface: menu | popover | tooltip | dialog
No toast: it needs libadwaita (Adw), which is not installed.
"""
import argparse
import json
import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GLib, Gtk

ap = argparse.ArgumentParser()
ap.add_argument("--bounds")
ap.add_argument("--show", choices=["menu", "popover", "tooltip", "dialog"])
ARGS = ap.parse_args()

IDS = {}
NAMES = {
    "button": "Button", "button-suggested": "Suggested button", "button-destructive": "Destructive button",
    "button-flat": "Flat button", "segmented": "Segmented control", "entry": "Text field",
    "search": "Search field", "spin": "Spin button", "dropdown": "Dropdown", "check": "Checkbox",
    "radio": "Radio button", "switch": "Switch", "slider": "Slider", "progress": "Progress bar",
    "levelbar": "Level bar", "scrollbar": "Scrollbar", "tooltip": "Tooltip", "popover": "Popover",
    "dialog": "Dialog", "tabs": "Tabs", "infobar": "Info bar", "list": "List", "sidebar": "Sidebar",
    "tree": "Table", "calendar": "Calendar", "expander": "Expander",
}
# controls that keep their natural width, left-aligned (like macOS); the rest fill their cell
NATURAL = {"button", "button-suggested", "button-destructive", "button-flat", "spin", "dropdown", "tooltip",
           "popover-button", "dialog-button", "segmented"}


class TipPopover(Gtk.Popover):
    pass


TipPopover.set_css_name("tooltip")


def caption(text):
    lab = Gtk.Label(label=text, xalign=0)
    lab.add_css_class("dim-label")
    lab.add_css_class("caption")
    return lab


def cell(grid, wid, widget, col, row, cols=1, rows=1, label=None):
    """Put widget under a small caption; remember it as gallery id wid."""
    widget.set_name(wid)
    IDS[wid] = widget
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    box.append(caption(NAMES.get(label or wid, label or wid)))
    if wid in NATURAL:
        widget.set_halign(Gtk.Align.START)
    widget.set_vexpand(False)
    widget.set_valign(Gtk.Align.START)
    box.append(widget)
    grid.attach(box, col, row, cols, rows)


def hbox(*widgets, spacing=12):
    box = Gtk.Box(spacing=spacing)
    for w in widgets:
        box.append(w)
    return box


def build_header(app):
    header = Gtk.HeaderBar()
    header.set_name("titlebar-toolbar")
    header.set_title_widget(Gtk.Label(label="Slate"))
    header.pack_start(Gtk.Button.new_from_icon_name("go-previous-symbolic"))
    header.pack_start(Gtk.Button.new_from_icon_name("go-next-symbolic"))
    header.pack_end(Gtk.Button.new_from_icon_name("system-search-symbolic"))

    menu = Gio.Menu()
    sec1 = Gio.Menu()
    for label, act in (("New Window", "new"), ("Open…", "open"), ("Save As…", "save")):
        sec1.append(label, "app." + act)
    sec2 = Gio.Menu()
    for label, act in (("Preferences", "prefs"), ("Keyboard Shortcuts", "keys")):
        sec2.append(label, "app." + act)
    sec3 = Gio.Menu()
    sec3.append("About Slate", "app.about")
    for s in (sec1, sec2, sec3):
        menu.append_section(None, s)
    mb = Gtk.MenuButton(icon_name="open-menu-symbolic", menu_model=menu)
    IDS["menu"] = mb
    IDS["titlebar-toolbar"] = header
    header.pack_end(mb)
    return header, mb


def build_grid(win):
    grid = Gtk.Grid(column_spacing=12, row_spacing=14, column_homogeneous=True)
    for side in ("top", "bottom", "start", "end"):
        getattr(grid, f"set_margin_{side}")(16)

    cell(grid, "button", Gtk.Button(label="Button"), 0, 0)
    sug = Gtk.Button(label="Suggested")
    sug.add_css_class("suggested-action")
    cell(grid, "button-suggested", sug, 1, 0)
    des = Gtk.Button(label="Destructive")
    des.add_css_class("destructive-action")
    cell(grid, "button-destructive", des, 2, 0)
    flat = Gtk.Button(label="Flat")
    flat.add_css_class("flat")
    cell(grid, "button-flat", flat, 3, 0)

    seg = Gtk.Box()
    seg.add_css_class("linked")
    first = None
    for i, t in enumerate(("Day", "Week", "Month")):
        b = Gtk.ToggleButton(label=t, hexpand=True)
        if first is None:
            first = b
            b.set_active(True)
        else:
            b.set_group(first)
        seg.append(b)
    cell(grid, "segmented", seg, 0, 1)
    cell(grid, "entry", Gtk.Entry(text="Text entry"), 1, 1)
    cell(grid, "search", Gtk.SearchEntry(text="slate"), 2, 1)
    cell(grid, "spin", Gtk.SpinButton.new_with_range(0, 100, 1), 3, 1)
    IDS["spin"].set_value(42)

    cell(grid, "dropdown", Gtk.DropDown.new_from_strings(["Dropdown", "Second", "Third"]), 0, 2)
    cell(grid, "check", hbox(Gtk.CheckButton(label="On", active=True), Gtk.CheckButton(label="Off")), 1, 2)
    r1 = Gtk.CheckButton(label="On", active=True)
    r2 = Gtk.CheckButton(label="Off")
    r2.set_group(r1)
    cell(grid, "radio", hbox(r1, r2), 2, 2)
    cell(grid, "switch", hbox(Gtk.Switch(active=True), Gtk.Switch()), 3, 2)

    scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
    scale.set_value(40)
    scale.set_draw_value(False)
    cell(grid, "slider", scale, 0, 3, 2)
    cell(grid, "progress", Gtk.ProgressBar(fraction=0.6), 2, 3)
    lvl = Gtk.LevelBar.new_for_interval(0, 10)
    lvl.set_value(7)
    cell(grid, "levelbar", lvl, 3, 3)

    adj = Gtk.Adjustment(value=20, lower=0, upper=100, step_increment=1, page_increment=10, page_size=40)
    cell(grid, "scrollbar", Gtk.Scrollbar(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj), 0, 4)
    tip = Gtk.Button(label="Hover me")
    tip.set_tooltip_text("A tooltip in Slate")
    cell(grid, "tooltip", tip, 1, 4)
    pop_btn = Gtk.MenuButton(label="Open popover")
    pop = Gtk.Popover()
    pbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin_top=12, margin_bottom=12,
                   margin_start=12, margin_end=12)
    pbox.append(Gtk.Label(label="Notifications", xalign=0, css_classes=["heading"]))
    pbox.append(hbox(Gtk.Label(label="Do not disturb", hexpand=True, xalign=0), Gtk.Switch(active=True)))
    pbox.append(Gtk.Entry(placeholder_text="Snooze for…"))
    pop.set_child(pbox)
    pop_btn.set_popover(pop)
    pop.set_name("popover")
    IDS["popover"] = pop
    cell(grid, "popover-button", pop_btn, 2, 4, label="popover")
    IDS.pop("popover-button")
    dlg = Gtk.Button(label="Show dialog")
    cell(grid, "dialog-button", dlg, 3, 4, label="dialog")
    IDS.pop("dialog-button")

    nb = Gtk.Notebook()
    for t in ("General", "Appearance", "Advanced"):
        nb.append_page(Gtk.Label(label=f"{t} settings", margin_top=12, margin_bottom=12), Gtk.Label(label=t))
    cell(grid, "tabs", nb, 0, 5, 2)

    bar = Gtk.InfoBar(message_type=Gtk.MessageType.INFO, show_close_button=True)
    bar.add_child(Gtk.Label(label="A new Slate build is ready."))
    bar.add_button("Update", 1)
    bar.set_revealed(True)
    cell(grid, "infobar", bar, 2, 5, 2)

    lb = Gtk.ListBox()
    for t in ("Inbox", "Drafts", "Sent"):
        lb.append(Gtk.Label(label=t, xalign=0, margin_top=7, margin_bottom=7, margin_start=10, margin_end=10))
    lb.select_row(lb.get_row_at_index(1))
    frame = Gtk.Frame()
    frame.set_child(lb)
    cell(grid, "list", frame, 0, 6)

    stack = Gtk.Stack()
    for name in ("Library", "Recent", "Starred"):
        stack.add_titled(Gtk.Label(label=name), name.lower(), name)
    side = Gtk.StackSidebar(stack=stack)
    side.set_size_request(-1, 105)
    win._stack = stack
    cell(grid, "sidebar", side, 1, 6)

    store = Gtk.ListStore(str, str, str)
    for r in (("slate.css", "CSS", "12 KB"), ("tokens.json", "JSON", "4 KB"), ("build.py", "Python", "9 KB")):
        store.append(r)
    tv = Gtk.TreeView(model=store)
    for i, t in enumerate(("Name", "Kind", "Size")):
        tv.append_column(Gtk.TreeViewColumn(t, Gtk.CellRendererText(), text=i))
    tv.get_selection().select_path(Gtk.TreePath.new_from_string("1"))
    tframe = Gtk.Frame()
    tframe.set_child(tv)
    cell(grid, "tree", tframe, 2, 6)

    cell(grid, "calendar", Gtk.Calendar(), 3, 6, 1, 2)

    exp = Gtk.Expander(label="Expander", expanded=True)
    exp.set_child(Gtk.Label(label="Hidden details appear here.\nSecond line of the content.", xalign=0,
                            margin_top=4, margin_start=16))
    cell(grid, "expander", exp, 0, 7, 3)
    return grid, dlg, tip


def frame_rect(win):
    """Visible frame (without the CSD shadow) in widget coordinates of win."""
    rects = []
    for w in (win.get_titlebar(), win.get_child()):
        ok, r = w.compute_bounds(win)
        rects.append(r)
    x0 = min(r.get_x() for r in rects)
    y0 = min(r.get_y() for r in rects)
    x1 = max(r.get_x() + r.get_width() for r in rects)
    y1 = max(r.get_y() + r.get_height() for r in rects)
    return x0, y0, x1 - x0, y1 - y0


def write_bounds(win, path):
    ox, oy, w, h = frame_rect(win)
    out = {"window": [0, 0, round(w), round(h)]}
    for wid, widget in IDS.items():
        if wid in ("popover", "menu") or not widget.get_mapped():  # surfaces: cropped from the compositor
            continue
        ok, r = widget.compute_bounds(win)
        if ok:
            out[wid] = [round(r.get_x() - ox), round(r.get_y() - oy), round(r.get_width()), round(r.get_height())]
    with open(path, "w") as f:
        json.dump(out, f)


def on_activate(app):
    win = Gtk.ApplicationWindow(application=app, default_width=1100, default_height=760)
    header, menubtn = build_header(app)
    win.set_titlebar(header)
    grid, dlg_btn, tip_btn = build_grid(win)
    win.set_child(grid)

    def show_dialog(*_):
        d = Gtk.AlertDialog(message="Discard changes?", detail="Unsaved edits will be lost.")
        d.set_buttons(["Cancel", "Discard"])
        d.set_cancel_button(0)
        d.set_default_button(1)
        d.choose(win, None, None, None)

    dlg_btn.connect("clicked", show_dialog)
    win.present()

    def after_map():
        if ARGS.show == "menu":
            menubtn.popup()
        elif ARGS.show == "popover":
            IDS["popover"].popup()
        elif ARGS.show == "dialog":
            show_dialog()
        elif ARGS.show == "tooltip":
            # no pointer in the nested compositor, so a real tooltip never fires: draw the same
            # `tooltip` CSS node as a popover under the button
            p = TipPopover(autohide=False, has_arrow=False, position=Gtk.PositionType.BOTTOM)
            p.add_css_class("background")
            p.set_child(Gtk.Label(label=tip_btn.get_tooltip_text(), margin_top=4, margin_bottom=4,
                                  margin_start=8, margin_end=8))
            p.set_parent(tip_btn)
            p.popup()
        return False

    def write():
        if ARGS.bounds:
            write_bounds(win, ARGS.bounds)
        return False

    GLib.timeout_add(900, write)
    GLib.timeout_add(1200, after_map)
    GLib.timeout_add_seconds(90, app.quit)  # safety net, shoot.sh kills earlier


GLib.set_prgname("org.slate.Demo4")  # Wayland app id
app = Gtk.Application(application_id="org.slate.Demo4")
for _name in ("new", "open", "save", "prefs", "keys", "about"):
    _a = Gio.SimpleAction.new(_name, None)
    app.add_action(_a)
app.connect("activate", on_activate)
app.run([sys.argv[0]])
