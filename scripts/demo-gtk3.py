#!/usr/bin/env python3
"""GTK3 widget gallery used by preview.sh to screenshot the Slate theme."""
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk


def labelled(text, widget):
    box = Gtk.Box(spacing=8)
    box.pack_start(Gtk.Label(label=text, xalign=0, width_chars=10), False, False, 0)
    box.pack_start(widget, True, True, 0)
    return box


def controls():
    col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=16)

    row = Gtk.Box(spacing=8)
    suggested = Gtk.Button(label="Suggested")
    suggested.get_style_context().add_class("suggested-action")
    destructive = Gtk.Button(label="Destructive")
    destructive.get_style_context().add_class("destructive-action")
    off = Gtk.Button(label="Disabled")
    off.set_sensitive(False)
    for b in (Gtk.Button(label="Default"), suggested, destructive, off):
        row.pack_start(b, False, False, 0)
    col.pack_start(row, False, False, 0)

    entry = Gtk.Entry(text="Text entry")
    col.pack_start(labelled("Entry", entry), False, False, 0)

    row = Gtk.Box(spacing=12)
    row.pack_start(Gtk.CheckButton(label="Check", active=True), False, False, 0)
    row.pack_start(Gtk.CheckButton(label="Unchecked"), False, False, 0)
    radio = Gtk.RadioButton(label="Radio")
    row.pack_start(radio, False, False, 0)
    row.pack_start(Gtk.RadioButton.new_with_label_from_widget(radio, "Other"), False, False, 0)
    row.pack_start(Gtk.Switch(active=True, valign=Gtk.Align.CENTER), False, False, 0)
    row.pack_start(Gtk.Switch(valign=Gtk.Align.CENTER), False, False, 0)
    col.pack_start(row, False, False, 0)

    scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
    scale.set_value(40)
    col.pack_start(labelled("Scale", scale), False, False, 0)
    col.pack_start(labelled("Progress", Gtk.ProgressBar(fraction=0.6, valign=Gtk.Align.CENTER)), False, False, 0)

    combo = Gtk.ComboBoxText()
    for t in ("Dropdown", "Second", "Third"):
        combo.append_text(t)
    combo.set_active(0)
    col.pack_start(labelled("Combo", combo), False, False, 0)

    listbox = Gtk.ListBox()
    for i, t in enumerate(("Inbox", "Drafts", "Sent", "Archive")):
        listbox.add(Gtk.Label(label=t, xalign=0, margin=6))
    listbox.select_row(listbox.get_row_at_index(1))
    frame = Gtk.Frame()
    frame.add(listbox)
    col.pack_start(frame, False, False, 0)
    return col


def main():
    win = Gtk.Window(default_width=900, default_height=620)
    win.move(0, 0)
    header = Gtk.HeaderBar(title="Slate", subtitle="GTK3 demo", show_close_button=True)
    header.pack_start(Gtk.Button.new_from_icon_name("go-previous-symbolic", Gtk.IconSize.BUTTON))
    seg = Gtk.Box()
    seg.get_style_context().add_class("linked")
    first = Gtk.ToggleButton(label="Grid", active=True)
    second = Gtk.ToggleButton(label="List")
    seg.pack_start(first, False, False, 0)
    seg.pack_start(second, False, False, 0)
    header.pack_start(seg)
    header.pack_end(Gtk.Button.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON))
    win.set_titlebar(header)

    paned = Gtk.Box()
    sidebar = Gtk.ListBox()
    sidebar.get_style_context().add_class("sidebar")
    for name in ("Library", "Recent", "Starred", "Documents", "Downloads", "Trash"):
        row = Gtk.ListBoxRow()
        box = Gtk.Box(spacing=8)
        box.pack_start(Gtk.Image.new_from_icon_name("folder-symbolic", Gtk.IconSize.MENU), False, False, 0)
        box.pack_start(Gtk.Label(label=name, xalign=0), True, True, 0)
        row.add(box)
        sidebar.add(row)
    sidebar.select_row(sidebar.get_row_at_index(1))
    sidebar.set_size_request(180, -1)
    paned.pack_start(sidebar, False, False, 0)
    paned.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 0)

    nb = Gtk.Notebook()
    nb.append_page(controls(), Gtk.Label(label="Controls"))
    nb.append_page(Gtk.Label(label="Second tab"), Gtk.Label(label="Other"))
    nb.append_page(Gtk.Label(label="Third tab"), Gtk.Label(label="More"))
    paned.pack_start(nb, True, True, 0)

    win.add(paned)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    GLib.timeout_add_seconds(60, Gtk.main_quit)  # safety net, preview.sh kills earlier
    Gtk.main()


main()
