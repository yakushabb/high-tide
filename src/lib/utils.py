# utils.py
#
# Copyright 2023 Nokse
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Gdk

import tidalapi
from tidalapi.page import PageItem, PageLink
from tidalapi.mix import Mix, MixType
from tidalapi.artist import Artist
from tidalapi.album import Album
from tidalapi.media import Track
from tidalapi.playlist import Playlist
from tidalapi.user import Favorites

import requests
from pathlib import Path

def pretty_duration(secs):
    if not secs:
        return "00:00"

    hours = secs // 3600
    minutes = (secs % 3600) // 60
    seconds = secs % 60

    if hours > 0:
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    else:
        return f"{int(minutes):02}:{int(seconds):02}"

    return "00:00"

def add_image(image_widget, item):

    """Retrieves and adds an image"""

    file_path = Path(f"tmp_img/{item.id}.jpg")

    if file_path.is_file():
        GLib.idle_add(_add_image, image_widget, str(file_path))

    try:
        image_url = item.image()
        response = requests.get(image_url)
    except Exception as e:
        print(str(e))
        return
    if response.status_code == 200:
        image_data = response.content

        with open(file_path, "wb") as file:
            file.write(image_data)

        GLib.idle_add(_add_image, image_widget, str(file_path))

def _add_image(image_widget, file_path):
        image_widget.set_from_file(file_path)

def add_image_to_avatar(avatar_widget, item):

    """Same ad the previous function, but for Adwaita's avatar widgets"""

    def _add_image_to_avatar(avatar_widget, file_path):
            file = Gio.File.new_for_path(file_path)
            image = Gdk.Texture.new_from_file(file)
            avatar_widget.set_custom_image(image)

    file_path = Path(f"tmp_img/{item.id}.jpg")

    if file_path.is_file():
        GLib.idle_add(_add_image_to_avatar, avatar_widget, str(file_path))

    try:
        image_url = item.image()
        response = requests.get(image_url)
    except Exception as e:
        print(str(e))
        artist_picture.set_icon_name("emblem-music-symbolic")
        return
    if response.status_code == 200:
        image_data = response.content

        with open(file_path, "wb") as file:
            file.write(image_data)

        GLib.idle_add(_add_image_to_avatar, avatar_widget, str(file_path))
