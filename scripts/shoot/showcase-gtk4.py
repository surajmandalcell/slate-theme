#!/usr/bin/env python3
"""A Finder-like GTK4 window for the README cover: python3 showcase-gtk4.py [--dark]."""
import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, GLib, Gtk

GLib.set_prgname("org.slate.Showcase")
DARK = "Dark" in GLib.getenv("GTK_THEME") if GLib.getenv("GTK_THEME") else False
ACCENT = "#0A84FF" if DARK else "#007AFF"  # tokens.json accent

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
FILES = [
    ("Archive", "folder"), ("Design", "folder"), ("Music", "folder"),
    ("Photos", "folder"), ("Projects", "folder"), ("Videos", "folder"),
    ("Slate.pdf", "application-pdf"), ("tokens.json", "application-json"), ("Notes.txt", "text-plain"),
    ("Cover.png", "image-png"), ("Budget.ods", "x-office-spreadsheet"), ("Talk.mp3", "audio-mpeg"),
    ("Roadmap.odt", "x-office-document"), ("Logo.svg", "image-svg+xml"), ("Release.zip", "application-zip"),
    ("Demo.mp4", "video-mp4"), ("Install.sh", "application-x-shellscript"), ("Palette.png", "image-png"),
]


def sidebar():
    box = Gtk.ListBox(css_classes=["navigation-sidebar"])
    selected = None
    for name, icon in SIDEBAR:
        if icon is None:
            label = Gtk.Label(label=name, xalign=0, css_classes=["dim-label", "caption-heading"],
                              margin_top=10, margin_start=8)
            row = Gtk.ListBoxRow(child=label, selectable=False, activatable=False)
        else:
            line = Gtk.Box(spacing=8)
            line.append(Gtk.Image(icon_name=icon))
            line.append(Gtk.Label(label=name, xalign=0))
            row = Gtk.ListBoxRow(child=line)
            if name == "Documents":
                selected = row
        box.append(row)
    box.select_row(selected)
    pane = Gtk.ScrolledWindow(child=box, width_request=200, css_classes=["sidebar-pane"],
                              hscrollbar_policy=Gtk.PolicyType.NEVER)
    return pane


def accent_icon(path):
    """Breeze icon as a texture, with Breeze blue replaced by the Slate accent, as KDE does for Dolphin."""
    svg = open(path).read().replace("#3daee9", ACCENT)
    return Gdk.Texture.new_from_bytes(GLib.Bytes.new(svg.encode()))


def content():
    grid = Gtk.FlowBox(max_children_per_line=6, min_children_per_line=6, row_spacing=4, column_spacing=12,
                       homogeneous=True, selection_mode=Gtk.SelectionMode.SINGLE,
                       margin_top=20, margin_bottom=20, margin_start=20, margin_end=20, valign=Gtk.Align.START)
    theme = Gtk.IconTheme.get_for_display(grid.get_display())
    for i, (name, icon) in enumerate(FILES):
        tile = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin_top=6, margin_bottom=6)
        # load the icon file as a picture: GTK recolors Breeze's ColorScheme icons into flat glyphs,
        # Dolphin shows them in full colour, and the cover must show the same icons in both apps
        path = theme.lookup_icon(icon, None, 64, 1, Gtk.TextDirection.NONE, 0).get_file().get_path()
        tile.append(Gtk.Image(paintable=accent_icon(path), pixel_size=48))
        tile.append(Gtk.Label(label=name, ellipsize=3, max_width_chars=12))
        grid.append(tile)
        if i == 3:
            grid.select_child(grid.get_child_at_index(i))
    return Gtk.ScrolledWindow(child=grid, css_classes=["view"], hexpand=True)


def headerbar():
    bar = Gtk.HeaderBar(title_widget=Gtk.Label(label="Documents", css_classes=["title"]))
    nav = Gtk.Box(spacing=4)
    nav.append(Gtk.Button(icon_name="go-previous-symbolic", css_classes=["flat"]))
    nav.append(Gtk.Button(icon_name="go-next-symbolic", css_classes=["flat"], sensitive=False))
    bar.pack_start(nav)
    search = Gtk.SearchEntry(placeholder_text="Search", width_chars=16)
    bar.pack_end(search)
    views = Gtk.Box(css_classes=["linked"])
    grid_btn = Gtk.ToggleButton(icon_name="view-grid-symbolic", active=True)
    list_btn = Gtk.ToggleButton(icon_name="view-list-symbolic", group=grid_btn)
    views.append(grid_btn)
    views.append(list_btn)
    bar.pack_end(views)
    return bar


def on_activate(app):
    paned = Gtk.Paned(start_child=sidebar(), end_child=content(), position=200,
                      shrink_start_child=False, resize_start_child=False)
    win = Gtk.ApplicationWindow(application=app, title="Documents", default_width=1080, default_height=420,
                                child=paned)
    win.set_titlebar(headerbar())
    win.present()


app = Gtk.Application(application_id="org.slate.Showcase")
app.connect("activate", on_activate)
app.run([sys.argv[0]])
