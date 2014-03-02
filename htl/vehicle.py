# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Osmo Salomaa
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

"""Properties of a public transportation vehicle."""

import htl

__all__ = ("Vehicle",)


class Vehicle:

    """Properties of a public transportation vehicle."""

    def __init__(self, **kwargs):
        """Initialize a :class:`Vehicle` instance."""
        self.id = None
        self.route = None
        self.x = 0
        self.y = 0
        self.bearing = 0
        self.state = htl.states.OK
        for name, value in kwargs.items():
            setattr(self, name, value)

    @property
    def color(self):
        """Return `type`-dependent color for icons and text."""
        if self.type == "train":
            return "#DA1551"
        if self.type == "metro":
            return "#FE631E"
        if self.type == "tram":
            return "#169660"
        if self.type == "bus":
            return "#0A79C7"
        if self.type == "kutsuplus":
            return "#0A79C7"
        return "#000000"

    @property
    def line(self):
        """Return human readable line number by parsing `route`."""
        # It seems that tram routes are possibly abbreviated 4-7 letter
        # variants of JORE-codes documented as part of the Reittiopas API.
        # Train, metro and kutsuplus routes are the same as lines.
        # http://developer.reittiopas.fi/pages/en/http-get-interface-version-2.php
        line = self.route
        if len(line) >= 4:
            line = line[1:5].strip()
            while len(line) > 1 and line.startswith("0"):
                line = line[1:]
        # For metro, "M" and "V" make more sense than "1" and "2".
        if self.id.startswith("metro"):
            if line == "1":
                line = "M"
            if line == "2":
                line = "V"
        return(line)

    @property
    def type(self):
        """Return vehicle type guessed from `id` and `line`."""
        if self.id.startswith("metro"):
            return "metro"
        if self.id.startswith("RHKL"):
            return "tram"
        line = self.line.upper()
        if not line or line == "0":
            return "unknown"
        if line[0].isdigit():
            while line[-1].isalpha():
                line = line[:-1]
            if line.isdigit():
                if int(line) <= 10:
                    return "tram"
                return "bus"
        if line[0].isalpha():
            if line.startswith("K") and line[-1].isdigit():
                return "kutsuplus"
            if self.route.isdigit():
                return "metro"
            return "train"
        return "unknown"
