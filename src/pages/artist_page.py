# artist_page.py
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

from ..lib import utils

import threading
import requests
import random
import copy

from .page import Page

class artistPage(Page):
    __gtype_name__ = 'artistPage'

    """It is used to display an artist page"""

    # FIXME The bio is not displayed properly, it all bold and the links are not working
    # TODO Add missing features: influences, appears on, credits and so on

    def __init__(self, _window, _item, _name):
        super().__init__(_window, _item, _name)

        self.top_tracks = []

    def _load_page(self):

        print(f"artist: {self.item.name}, id: {self.item.id}, {self.item.picture}")

        builder = Gtk.Builder.new_from_resource("/io/github/nokse22/high-tide/ui/pages_ui/artist_page_template.ui")

        page_content = builder.get_object("_main")
        top_tracks_list_box = builder.get_object("_top_tracks_list_box")
        carousel_box = builder.get_object("_carousel_box")
        top_tracks_list_box.connect("row-activated", self.on_row_selected)

        builder.get_object("_name_label").set_label(self.item.name)
        # builder.get_object("_bio_label").set_label(self.item.roles)

        builder.get_object("_play_button").connect("clicked", self.on_play_button_clicked)
        builder.get_object("_shuffle_button").connect("clicked", self.on_shuffle_button_clicked)

        builder.get_object("_follow_button").connect("clicked", self.on_add_to_my_collection_button_clicked)
        builder.get_object("_radio_button").connect("clicked", self.on_artist_radio_button_clicked)

        image = builder.get_object("_image")

        try:
            self.top_tracks = self.item.get_top_tracks(10)
        except:
            pass
        else:
            for index, track in enumerate(self.top_tracks):
                listing = self.get_track_listing(track)
                listing.set_name(str(index))
                top_tracks_list_box.append(listing)

        carousel, cards_box = self.get_carousel("Albums")
        carousel_box.append(carousel)

        try:
            albums = self.item.get_albums()
        except:
            pass
        else:
            for album in albums:
                album_card = self.get_album_card(album)
                cards_box.append(album_card)

        carousel, cards_box = self.get_carousel("Similar Artists")
        carousel_box.append(carousel)

        this_artist = self.window.session.artist(self.item.id)
        try:
            artists = this_artist.get_similar()
        except:
            pass
        else:
            for artist in artists:
                artist_card = self.get_artist_card(artist)
                cards_box.append(artist_card)

        try:
            bio = self.item.get_bio()
        except:
            pass
        else:
            expander = Gtk.Expander(label="Bio", css_classes=["title-3"], margin_bottom=50)
            label = Gtk.Label(label=bio, wrap=True, css_classes=[])
            expander.set_child(label)
            carousel_box.append(expander)

        artist_picture = builder.get_object("_avatar")

        th = threading.Thread(target=utils.add_image_to_avatar, args=(artist_picture, self.item))
        th.deamon = True
        th.start()

        self.content.remove(self.spinner)
        self.content.append(page_content)

    def on_row_selected(self, list_box, row):
        index = int(row.get_name())

        self.window.player_object.current_mix_album_list = self.top_tracks
        track = self.window.player_object.current_mix_album_list[index]
        self.window.player_object.current_mix_album = track.album
        self.window.player_object.play_track(track)
        self.window.player_object.current_song_index = index

    def on_play_button_clicked(self, btn):
        self.window.player_object.current_mix_album = self.item
        self.window.player_object.current_mix_album_list = self.top_tracks
        track = self.window.player_object.current_mix_album_list[0]
        self.window.player_object.play_track(track)
        self.window.player_object.current_song_index = 0

    def on_shuffle_button_clicked(self, btn):
        self.window.player_object.current_mix_album = None
        self.window.player_object.current_mix_album_list = self.top_tracks
        self.window.player_object.play_shuffle()

    def on_artist_radio_button_clicked(self, btn):
        from .track_radio_page import trackRadioPage
        page = trackRadioPage(self.window, self.item, f"Radio of {self.item.name}")
        page.load()
        self.window.navigation_view.push(page)
