#!/usr/bin/env python3
"""A Finder-like GTK4 window for the README cover: python3 showcase-gtk4.py.

Finder layout: the sidebar runs the full window height with the traffic lights on top of it, and the
toolbar (back, forward, bold folder title, view switch, search) sits over the file grid only.
"""
import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk

GLib.set_prgname("org.slate.Showcase")

SIDEBAR = [
    ("Favorites", None),
    ("Recents", "document-open-recent-symbolic"),
    ("Applications", "view-app-grid-symbolic"),
    ("Desktop", "user-desktop-symbolic"),
    ("Documents", "folder-documents-symbolic"),
    ("Downloads", "folder-download-symbolic"),
    ("Locations", None),
    ("Home", "user-home-symbolic"),
    ("Network", "network-workgroup-symbolic"),
    ("Trash", "user-trash-symbolic"),
]
# same files and order as the Dolphin window behind it (Dolphin sorts folders first, then by name)
FILES = [
    ("Archive", "folder"), ("Design", "folder"), ("Music", "folder"),
    ("Photos", "folder"), ("Projects", "folder"), ("Videos", "folder"),
    ("Budget.ods", "x-office-spreadsheet"), ("Cover.png", "image-png"), ("Demo.mp4", "video-mp4"),
    ("Install.sh", "application-x-shellscript"), ("Logo.svg", "image-svg+xml"), ("Notes.txt", "text-plain"),
    ("Palette.png", "image-png"), ("Release.zip", "application-zip"), ("Roadmap.odt", "x-office-document"),
    ("Slate.pdf", "application-pdf"), ("Talk.mp3", "audio-mpeg"), ("tokens.json", "application-json"),
]
SIDEBAR_W = 190


def sidebar():
    box = Gtk.ListBox(css_classes=["navigation-sidebar"])
    selected = None
    for name, icon in SIDEBAR:
        if icon is None:
            label = Gtk.Label(label=name, xalign=0, css_classes=["dim-label", "caption-heading"],
                              margin_top=12 if name != "Favorites" else 2, margin_bottom=2, margin_start=10)
            box.append(Gtk.ListBoxRow(child=label, selectable=False, activatable=False))
            continue
        line = Gtk.Box(spacing=0)
        line.append(Gtk.Image(icon_name=icon))
        line.append(Gtk.Label(label=name, xalign=0))
        row = Gtk.ListBoxRow(child=line)
        if name == "Documents":
            selected = row
        box.append(row)
    box.select_row(selected)
    bar = Gtk.HeaderBar(title_widget=Gtk.Box(), decoration_layout="close,minimize,maximize:")
    pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, width_request=SIDEBAR_W, css_classes=["sidebar-pane"])
    pane.append(bar)
    pane.append(Gtk.ScrolledWindow(child=box, vexpand=True, hscrollbar_policy=Gtk.PolicyType.NEVER))
    return pane


def toolbar():
    bar = Gtk.HeaderBar(title_widget=Gtk.Box(), decoration_layout=":")
    nav = Gtk.Box(spacing=2)
    nav.append(Gtk.Button(icon_name="go-previous-symbolic", css_classes=["flat"]))
    nav.append(Gtk.Button(icon_name="go-next-symbolic", css_classes=["flat"], sensitive=False))
    bar.pack_start(nav)
    bar.pack_start(Gtk.Label(label="Documents", css_classes=["heading"], margin_start=6))
    bar.pack_end(Gtk.Button(icon_name="system-search-symbolic", css_classes=["flat"]))
    views = Gtk.Box(css_classes=["linked"])
    grid_btn = Gtk.ToggleButton(icon_name="view-grid-symbolic", active=True)
    views.append(grid_btn)
    views.append(Gtk.ToggleButton(icon_name="view-list-symbolic", group=grid_btn))
    bar.pack_end(views)
    return bar


def content():
    grid = Gtk.FlowBox(max_children_per_line=6, min_children_per_line=6, row_spacing=10, column_spacing=8,
                       homogeneous=True, selection_mode=Gtk.SelectionMode.SINGLE,
                       margin_top=18, margin_bottom=18, margin_start=18, margin_end=18, valign=Gtk.Align.START)
    for name, icon in FILES:
        tile = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, margin_top=4, margin_bottom=4)
        tile.append(Gtk.Image(icon_name=icon, pixel_size=64))
        tile.append(Gtk.Label(label=name, ellipsize=3, max_width_chars=12))
        grid.append(tile)
    pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True)
    pane.append(toolbar())
    pane.append(Gtk.ScrolledWindow(child=grid, css_classes=["view"], vexpand=True,
                                   hscrollbar_policy=Gtk.PolicyType.NEVER))
    return pane


def on_activate(app):
    paned = Gtk.Paned(start_child=sidebar(), end_child=content(), position=SIDEBAR_W,
                      shrink_start_child=False, resize_start_child=False)
    win = Gtk.ApplicationWindow(application=app, title="Documents", default_width=860, default_height=540,
                                child=paned)
    win.set_titlebar(Gtk.Box(visible=False))  # no window-wide title bar: each pane has its own
    win.present()


app = Gtk.Application(application_id="org.slate.Showcase")
app.connect("activate", on_activate)
app.run([sys.argv[0]])
