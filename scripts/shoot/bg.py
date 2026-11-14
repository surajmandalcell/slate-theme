#!/usr/bin/env python3
"""Wallpaper window for scripts/shoot.sh: python3 bg.py IMAGE.png (undecorated, app id org.slate.Bg)."""
import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk

GLib.set_prgname("org.slate.Bg")  # becomes the Wayland app id, which place.js matches

def on_activate(app):
    pic = Gtk.Picture.new_for_filename(sys.argv[1])
    pic.set_content_fit(Gtk.ContentFit.FILL)
    Gtk.ApplicationWindow(application=app, decorated=False, default_width=2400, default_height=1500,
                          child=pic).present()


app = Gtk.Application(application_id="org.slate.Bg")
app.connect("activate", on_activate)
app.run([sys.argv[0]])
