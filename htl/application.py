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

"""Show real-time locations of HSL public transportation vehicles."""

import htl
import pyotherside
import time

__all__ = ("Application",)


class Application:

    """Show real-time locations of HSL public transportation vehicles."""

    def __init__(self):
        """Initialize an :class:`Application` instance."""
        self.filters = htl.Filters("hsl")
        self._lines = []
        self._times_started = 0
        self._tracker = htl.Tracker("hsl")
        self._utimes = {}

    def bootstrap(self):
        """Fetch the last known positions of vehicles."""
        return self._tracker.bootstrap()

    def list_lines(self):
        """Return a list of available lines."""
        # Cache list of lines, assuming it is acquired via
        # a possibly slow API call or file read.
        if self._lines:
            return self._lines
        lines = self._tracker.list_lines()
        if lines:
            self._lines = lines
        return lines

    def quit(self):
        """Quit the application."""
        self.filters.write()
        self._tracker.stop()
        htl.http.pool.terminate()

    def start(self):
        """Start threaded periodic updates."""
        if self._times_started == 0:
            self.update_filters()
        self._tracker.start()
        self._times_started += 1

    def stop(self):
        """Stop threaded periodic updates."""
        self._tracker.stop()

    def update_filters(self):
        """Update vehicle filters, return ``True`` if changed."""
        return self._tracker.update_filters()

    def update_vehicle(self, vehicle):
        """Update `vehicle` in QML map or add if missing."""
        if vehicle["id"] in self._utimes:
            # XXX: QML gets confused if we send updates faster than
            # the QML animation duration. We might need a queue here,
            # instead of just discarding updates.
            utime = self._utimes[vehicle["id"]]
            if time.time() - utime < 3.5: return
        vehicle["color"] = htl.util.type_to_color(vehicle["type"])
        pyotherside.send("update-vehicle", vehicle)
        self._utimes[vehicle["id"]] = time.time()
