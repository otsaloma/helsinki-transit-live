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

"""A collection of vehicle filters."""

import copy
import htl
import os

__all__ = ("Filters",)


class Filters:

    """A collection of vehicle filters."""

    def __init__(self, id):
        """Initialize a :class:`Filters` instance."""
        self._filters = {}
        self.id = id
        self._path = os.path.join(htl.CONFIG_HOME_DIR, "filters.json")
        self._read()

    def add_line(self, line):
        """Add `line` to the list of line filters."""
        if not line in self._filters[self.id]["lines"]:
            self._filters[self.id]["lines"].append(line)

    def get_filters(self):
        """Return a dictionary of vehicle filters."""
        return copy.deepcopy(self._filters[self.id])

    def get_lines(self):
        """Return a list of line filters."""
        return sorted(self._filters[self.id]["lines"])

    def _read(self):
        """Read list of filters from file."""
        if os.path.isfile(self._path):
            with htl.util.silent(Exception):
                self._filters = htl.util.read_json(self._path)
        if not self.id in self._filters:
            self._filters[self.id] = {}
        for id in self._filters:
            if not "lines" in self._filters[id]:
                self._filters[id]["lines"] = []

    def remove_line(self, line):
        """Remove `line` from the list of line filters."""
        with htl.util.silent(ValueError):
            self._filters[self.id]["lines"].remove(line)

    def write(self):
        """Write list of filters to file."""
        for id in self._filters:
            self._filters[id]["lines"].sort()
        with htl.util.silent(Exception):
            htl.util.write_json(self._filters, self._path)
