#!/usr/bin/env python3
"""GTK3 widget gallery for screenshots of the Slate theme (scripts/shoot.sh).

Every widget carries its gallery id as widget name, the same ids as the Qt
gallery. Flags:
  --bounds FILE   write {"window":[x,y,w,h], "<id>":[x,y,w,h]} (logical px,
                  relative to the visible window frame) once the window is up
  --show WHAT     open a transient surface: menu | popover | tooltip | dialog
No toast: that is a libadwaita (GTK4) widget.
"""
import argparse
import json
import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, GLib, Gtk

ap = argparse.ArgumentParser()
ap.add_argument("--bounds")
ap.add_argument("--show", choices=["menu", "popover", "tooltip", "dialog"])
ARGS = ap.parse_args()

IDS = {}
SHOWN = {}  # popovers opened by --show
TIP = []    # the stand-in tooltip window and its position in the main window
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


class TipWindow(Gtk.Window):
    pass


TipWindow.set_css_name("tooltip")


def add_class(widget, name):
    widget.get_style_context().add_class(name)


def caption(text):
    lab = Gtk.Label(label=text, xalign=0)
    add_class(lab, "dim-label")
    return lab


def cell(grid, wid, widget, col, row, cols=1, rows=1, label=None):
    """Put widget under a small caption; remember it as gallery id wid."""
    widget.set_name(wid)
    IDS[wid] = widget
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    box.pack_start(caption(NAMES.get(label or wid, label or wid)), False, False, 0)
    if wid in NATURAL:
        widget.set_halign(Gtk.Align.START)
    widget.set_valign(Gtk.Align.START)
    box.pack_start(widget, False, False, 0)
    grid.attach(box, col, row, cols, rows)


def hbox(*widgets, spacing=12):
    box = Gtk.Box(spacing=spacing)
    for w in widgets:
        box.pack_start(w, False, False, 0)
    return box


def build_header():
    header = Gtk.HeaderBar(show_close_button=True, title="Slate")
    header.set_name("titlebar-toolbar")
    for icon in ("go-previous-symbolic", "go-next-symbolic"):
        header.pack_start(Gtk.Button.new_from_icon_name(icon, Gtk.IconSize.BUTTON))
    header.pack_end(Gtk.Button.new_from_icon_name("system-search-symbolic", Gtk.IconSize.BUTTON))

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
    mb = Gtk.MenuButton(menu_model=menu)
    mb.add(Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON))
    header.pack_end(mb)
    IDS["titlebar-toolbar"] = header
    return header, mb


def build_grid():
    grid = Gtk.Grid(column_spacing=12, row_spacing=14, column_homogeneous=True, margin=16)

    cell(grid, "button", Gtk.Button(label="Button"), 0, 0)
    sug = Gtk.Button(label="Suggested")
    add_class(sug, "suggested-action")
    cell(grid, "button-suggested", sug, 1, 0)
    des = Gtk.Button(label="Destructive")
    add_class(des, "destructive-action")
    cell(grid, "button-destructive", des, 2, 0)
    flat = Gtk.Button(label="Flat")
    add_class(flat, "flat")
    cell(grid, "button-flat", flat, 3, 0)

    seg = Gtk.Box()
    add_class(seg, "linked")
    first = None
    for t in ("Day", "Week", "Month"):
        b = Gtk.RadioButton.new_with_label_from_widget(first, t)
        b.set_mode(False)  # toggle-button look, one active
        if first is None:
            first = b
        seg.pack_start(b, True, True, 0)
    cell(grid, "segmented", seg, 0, 1)
    cell(grid, "entry", Gtk.Entry(text="Text entry"), 1, 1)
    cell(grid, "search", Gtk.SearchEntry(text="slate"), 2, 1)
    spin = Gtk.SpinButton.new_with_range(0, 100, 1)
    spin.set_value(42)
    cell(grid, "spin", spin, 3, 1)

    combo = Gtk.ComboBoxText()
    for t in ("Dropdown", "Second", "Third"):
        combo.append_text(t)
    combo.set_active(0)
    cell(grid, "dropdown", combo, 0, 2)
    cell(grid, "check", hbox(Gtk.CheckButton(label="On", active=True), Gtk.CheckButton(label="Off")), 1, 2)
    r1 = Gtk.RadioButton.new_with_label_from_widget(None, "On")
    r2 = Gtk.RadioButton.new_with_label_from_widget(r1, "Off")
    cell(grid, "radio", hbox(r1, r2), 2, 2)
    off = Gtk.Switch()
    on = Gtk.Switch(active=True)
    cell(grid, "switch", hbox(on, off), 3, 2)

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
    pbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin=12)
    title = Gtk.Label(label="Notifications", xalign=0)
    add_class(title, "heading")
    pbox.pack_start(title, False, False, 0)
    row = Gtk.Box(spacing=24)
    row.pack_start(Gtk.Label(label="Do not disturb", xalign=0), True, True, 0)
    row.pack_start(Gtk.Switch(active=True), False, False, 0)
    pbox.pack_start(row, False, False, 0)
    pbox.pack_start(Gtk.Entry(placeholder_text="Snooze for…"), False, False, 0)
    pbox.show_all()
    pop.add(pbox)
    pop_btn.set_popover(pop)
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
    bar.get_content_area().add(Gtk.Label(label="A new Slate build is ready."))
    bar.add_button("Update", 1)
    cell(grid, "infobar", bar, 2, 5, 2)

    lb = Gtk.ListBox()
    for t in ("Inbox", "Drafts", "Sent"):
        lb.add(Gtk.Label(label=t, xalign=0, margin=7, margin_start=10))
    lb.select_row(lb.get_row_at_index(1))
    frame = Gtk.Frame()
    frame.add(lb)
    cell(grid, "list", frame, 0, 6)

    stack = Gtk.Stack()
    for name in ("Library", "Recent", "Starred"):
        stack.add_titled(Gtk.Label(label=name), name.lower(), name)
    stack.show_all()  # the sidebar lists only visible pages
    side = Gtk.StackSidebar(stack=stack)
    side.set_size_request(-1, 105)
    cell(grid, "sidebar", side, 1, 6)
    IDS["_stack"] = stack  # keep the stack alive; its bounds are never written

    store = Gtk.ListStore(str, str, str)
    for r in (("slate.css", "CSS", "12 KB"), ("tokens.json", "JSON", "4 KB"), ("build.py", "Python", "9 KB")):
        store.append(r)
    tv = Gtk.TreeView(model=store)
    for i, t in enumerate(("Name", "Kind", "Size")):
        tv.append_column(Gtk.TreeViewColumn(t, Gtk.CellRendererText(), text=i))
    tv.get_selection().select_path(Gtk.TreePath.new_from_string("1"))
    tframe = Gtk.Frame()
    tframe.add(tv)
    cell(grid, "tree", tframe, 2, 6)

    cell(grid, "calendar", Gtk.Calendar(), 3, 6, 1, 2)

    exp = Gtk.Expander(label="Expander", expanded=True)
    exp.add(Gtk.Label(label="Hidden details appear here.\nSecond line of the content.", xalign=0,
                      margin_top=4, margin_start=16))
    cell(grid, "expander", exp, 0, 7, 3)
    return grid, dlg, tip


def rect(win, widget):
    x, y = widget.translate_coordinates(win, 0, 0)
    a = widget.get_allocation()
    return x, y, a.width, a.height


def write_bounds(win, path):
    """Rects relative to the visible frame (titlebar + content), i.e. without the CSD shadow."""
    rects = [rect(win, win.get_titlebar()), rect(win, win.get_child())]
    ox = min(r[0] for r in rects)
    oy = min(r[1] for r in rects)
    w = max(r[0] + r[2] for r in rects) - ox
    h = max(r[1] + r[3] for r in rects) - oy
    out = {"window": [0, 0, w, h]}
    for wid, widget in IDS.items():
        if wid in ("popover", "_stack", "_tip") or not widget.get_mapped():
            continue
        x, y, ww, hh = rect(win, widget)
        out[wid] = [x - ox, y - oy, ww, hh]
    # GTK3 popovers are drawn inside the main surface: place them under their button like GTK does
    for name, pop in SHOWN.items():
        btn = pop.get_relative_to()
        bx, by, bw, bh = rect(win, btn)
        pw, ph = pop.get_allocated_width(), pop.get_allocated_height()
        px = min(max(bx + bw / 2 - pw / 2, ox), ox + w - pw)
        out[name] = [round(px - ox), by + bh - oy, pw, ph]
    for t, x, y in TIP:
        out["tooltip"] = [x - ox, y - oy, t.get_allocated_width(), t.get_allocated_height()]
    with open(path, "w") as f:
        json.dump(out, f)


def on_activate(app):
    win = Gtk.ApplicationWindow(application=app, default_width=1100, default_height=760)
    header, menubtn = build_header()
    win.set_titlebar(header)
    grid, dlg_btn, tip_btn = build_grid()
    win.add(grid)

    def show_dialog(*_):
        d = Gtk.MessageDialog(transient_for=win, modal=False, message_type=Gtk.MessageType.QUESTION,
                              text="Discard changes?", secondary_text="Unsaved edits will be lost.")
        d.add_button("Cancel", Gtk.ResponseType.CANCEL)
        d.add_button("Discard", Gtk.ResponseType.ACCEPT)
        d.connect("response", lambda dd, r: dd.destroy())
        d.show()

    dlg_btn.connect("clicked", show_dialog)
    win.show_all()

    def after_map():
        if ARGS.show == "menu":
            SHOWN["menu"] = menubtn.get_popover()
            SHOWN["menu"].popup()
        elif ARGS.show == "popover":
            SHOWN["popover"] = IDS["popover"]
            IDS["popover"].popup()
        elif ARGS.show == "dialog":
            show_dialog()
        elif ARGS.show == "tooltip":
            # no pointer in the nested compositor, so a real tooltip never fires: draw the same
            # `tooltip` CSS node as a popup window under the button
            t = TipWindow(type=Gtk.WindowType.POPUP, transient_for=win, decorated=False)
            add_class(t, "background")
            t.add(Gtk.Label(label=tip_btn.get_tooltip_text(), margin_top=4, margin_bottom=4,
                            margin_start=8, margin_end=8))
            x, y = tip_btn.translate_coordinates(win, 0, 0)
            t.move(x, y + tip_btn.get_allocated_height() + 4)
            t.show_all()
            IDS["_tip"] = t
            TIP.append((t, x, y + tip_btn.get_allocated_height() + 4))
        return False

    def write():
        if ARGS.bounds:
            write_bounds(win, ARGS.bounds)
        return False

    GLib.timeout_add(1800, write)  # after the popup at 1200 ms
    GLib.timeout_add(1200, after_map)
    GLib.timeout_add_seconds(90, app.quit)  # safety net, shoot.sh kills earlier


GLib.set_prgname("org.slate.Demo3")  # Wayland app id
app = Gtk.Application(application_id="org.slate.Demo3")
for _name in ("new", "open", "save", "prefs", "keys", "about"):
    app.add_action(Gio.SimpleAction.new(_name, None))
app.connect("activate", on_activate)
app.run([sys.argv[0]])
