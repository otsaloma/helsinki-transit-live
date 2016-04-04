# -*- coding: utf-8 -*-

# Copyright (C) 2016 Osmo Salomaa
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

"""Monitoring for updates to vehicle positions."""

import htl
import importlib.machinery
import os
import time

__all__ = ("Tracker",)


def Tracker(id):
    """Return a vehicle tracking provider for `id`."""
    leaf = os.path.join("trackers", "{}.py".format(id))
    path = os.path.join(htl.DATA_HOME_DIR, leaf)
    if not os.path.isfile(path):
        path = os.path.join(htl.DATA_DIR, leaf)
    name = "htl.tracker.provider{:d}".format(int(1000*time.time()))
    loader = importlib.machinery.SourceFileLoader(name, path)
    return loader.load_module(name).Tracker()
