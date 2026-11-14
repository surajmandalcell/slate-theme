#!/usr/bin/env python3
"""GTK4 widget gallery used by preview.sh to screenshot the Slate theme."""
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk


def labelled(text, widget):
    box = Gtk.Box(spacing=8)
    label = Gtk.Label(label=text, xalign=0, width_chars=10)
    widget.set_hexpand(True)
    box.append(label)
    box.append(widget)
    return box


def row(*widgets):
    box = Gtk.Box(spacing=8)
    for w in widgets:
        box.append(w)
    return box


def controls():
    col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    for side in ("top", "bottom", "start", "end"):
        getattr(col, f"set_margin_{side}")(16)

    suggested = Gtk.Button(label="Suggested")
    suggested.add_css_class("suggested-action")
    destructive = Gtk.Button(label="Destructive")
    destructive.add_css_class("destructive-action")
    off = Gtk.Button(label="Disabled")
    off.set_sensitive(False)
    col.append(row(Gtk.Button(label="Default"), suggested, destructive, off))

    col.append(labelled("Entry", Gtk.Entry(text="Text entry")))

    radio = Gtk.CheckButton(label="Radio")
    other = Gtk.CheckButton(label="Other")
    other.set_group(radio)
    col.append(row(
        Gtk.CheckButton(label="Check", active=True),
        Gtk.CheckButton(label="Unchecked"),
        radio, other,
        Gtk.Switch(active=True, valign=Gtk.Align.CENTER),
        Gtk.Switch(valign=Gtk.Align.CENTER),
    ))

    scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
    scale.set_value(40)
    col.append(labelled("Scale", scale))
    col.append(labelled("Progress", Gtk.ProgressBar(fraction=0.6, valign=Gtk.Align.CENTER)))
    col.append(labelled("Dropdown", Gtk.DropDown.new_from_strings(["Dropdown", "Second", "Third"])))

    listbox = Gtk.ListBox()
    listbox.add_css_class("rich-list")
    for t in ("Inbox", "Drafts", "Sent", "Archive"):
        listbox.append(Gtk.Label(label=t, xalign=0, margin_top=6, margin_bottom=6, margin_start=6))
    listbox.select_row(listbox.get_row_at_index(1))
    frame = Gtk.Frame()
    frame.set_child(listbox)
    col.append(frame)
    return col


def on_activate(app):
    win = Gtk.ApplicationWindow(application=app, default_width=1280, default_height=800)
    header = Gtk.HeaderBar()
    header.set_title_widget(Gtk.Label(label="Slate"))
    header.pack_start(Gtk.Button.new_from_icon_name("go-previous-symbolic"))
    header.pack_end(Gtk.Button.new_from_icon_name("open-menu-symbolic"))
    win.set_titlebar(header)

    paned = Gtk.Box()
    stack = Gtk.Stack()
    sidebar = Gtk.StackSidebar(stack=stack)
    for name in ("Library", "Recent", "Starred"):
        stack.add_titled(Gtk.Label(label=name), name.lower(), name)
    sidebar.set_size_request(180, -1)
    paned.append(sidebar)
    paned.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))

    nb = Gtk.Notebook(hexpand=True)
    nb.append_page(controls(), Gtk.Label(label="Controls"))
    nb.append_page(Gtk.Label(label="Second tab"), Gtk.Label(label="Other"))
    nb.append_page(Gtk.Label(label="Third tab"), Gtk.Label(label="More"))
    paned.append(nb)

    win.set_child(paned)
    win.present()
    GLib.timeout_add_seconds(60, app.quit)  # safety net, preview.sh kills earlier


app = Gtk.Application(application_id="org.slate.Demo4")
app.connect("activate", on_activate)
app.run(None)
