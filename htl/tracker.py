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
import re
import time

__all__ = ("Tracker",)


class Tracker:

    """Monitoring for updates to vehicle positions."""

    def __new__(cls, id):
        """Return possibly existing instance for `id`."""
        if not hasattr(cls, "_instances"):
            cls._instances = {}
        if not id in cls._instances:
            cls._instances[id] = object.__new__(cls)
        return cls._instances[id]

    def __init__(self, id):
        """Initialize a :class:`Tracker` instance."""
        # Initialize properties only once.
        if hasattr(self, "id"): return
        path, values = self._load_attributes(id)
        self.description = values["description"]
        self.id = id
        self._lines = []
        self.name = values["name"]
        self._provider = None
        self._init_provider(re.sub(r"\.json$", ".py", path))

    def _init_provider(self, path):
        """Initialize tracking provider class from `path`."""
        name = "htl.tracker.provider{:d}".format(int(1000*time.time()))
        loader = importlib.machinery.SourceFileLoader(name, path)
        self._provider = loader.load_module(name).Tracker()

    def bootstrap(self):
        """Fetch the last known positions of vehicles."""
        return self._provider.bootstrap()

    def list_lines(self):
        """Return a list of available lines."""
        # Cache list of lines, assuming it is acquired via
        # a possibly slow API call or file read.
        if self._lines:
            return self._lines
        lines = self._provider.list_lines()
        if lines:
            self._lines = lines
        return lines

    def _load_attributes(self, id):
        """Read and return attributes from JSON file."""
        leaf = os.path.join("trackers", "{}.json".format(id))
        path = os.path.join(htl.DATA_HOME_DIR, leaf)
        if not os.path.isfile(path):
            path = os.path.join(htl.DATA_DIR, leaf)
        return path, htl.util.read_json(path)

    def set_filters(self, filters):
        """Set vehicle filters for downloading data."""
        return self._provider.set_filters(filters)

    def start(self):
        """Start monitoring for updates to vehicle positions."""
        return self._provider.start()

    def stop(self):
        """Stop monitoring for updates to vehicle positions."""
        return self._provider.stop()
