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

"""Coordinates of a rectangular area."""

__all__ = ("BBox",)


class BBox:

    """Coordinates of a rectangular area."""

    def __init__(self, xmin=0, xmax=0, ymin=0, ymax=0):
        """Initialize a :class:`BBox` instance."""
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

    @property
    def area(self):
        """Area of the bounding box."""
        return (self.xmax - self.xmin) * (self.ymax - self.ymin)
