# -*- coding: utf-8-unix -*-

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

"""
Show real-time locations of HSL public transportation vehicles.

http://developer.reittiopas.fi/pages/en/other-apis.php
http://transport.wspgroup.fi/hklkartta/
"""

__version__ = "0.2.4"

import collections
import threading
import time
import urllib.request

try:
    import pyotherside
except ImportError:
    # Allow testing Python part alone.
    print("PyOtherSide not found, continuing anyway!")
    class pyotherside:
        def send(*args):
            pass

states = collections.namedtuple("State", "OK ADD REMOVE UPDATE")(1,2,3,4)


class BBox:

    """Coordinates of a rectangular area."""

    def __init__(self, xmin=0, xmax=0, ymin=0, ymax=0):
        """Initialize a :class:`BBox` object."""
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

    @property
    def area(self):
        """Area of the bounding box."""
        return (self.xmax - self.xmin) * (self.ymax - self.ymin)


class Vehicle:

    """Properties of a public transportation vehicle."""

    def __init__(self, **kwargs):
        """Initialize a :class:`Vehicle` object."""
        self.id = None
        self.route = None
        self.x = 0
        self.y = 0
        self.bearing = 0
        self.state = states.OK
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


class Application:

    """Show real-time locations of HSL public transportation vehicles."""

    def __init__(self, interval):
        """Initialize an :class:`Application` object."""
        self.bbox = BBox(0,0,0,0)
        self.interval = interval
        self.opener = None
        self.thread_queue = []
        self.vehicles = {}
        self._init_url_opener()

    def _init_url_opener(self):
        """Initialize the URL opener to use for downloading data."""
        self.opener = urllib.request.build_opener()
        agent = "helsinki-transit-live/{}".format(__version__)
        self.opener.addheaders = [("User-agent", agent)]

    def set_bbox(self, xmin, xmax, ymin, ymax):
        """Set coordinates of the bounding box."""
        self.bbox.xmin = xmin
        self.bbox.xmax = xmax
        self.bbox.ymin = ymin
        self.bbox.ymax = ymax

    def start(self):
        """Start threaded infinite periodic updates."""
        # Queue a new update thread, but delay start until
        # previous start and stop events have been processed.
        thread = threading.Thread(target=self.update)
        self.thread_queue.append(thread)
        while (self.thread_queue and
               self.thread_queue[0] is not thread):
            time.sleep(self.interval/2)
        thread.start()

    def stop(self):
        """Stop threaded infinite periodic updates."""
        self.thread_queue.append(None)

    def update(self):
        """Start infinite periodic updates."""
        while True:
            pyotherside.send("send-bbox")
            time.sleep(self.interval/2)
            if self.bbox.area > 0:
                self.update_locations()
            self.update_map()
            time.sleep(self.interval/2)
            if len(self.thread_queue) > 1:
                # Quit this thread if later start and/or
                # stop events have been queued.
                self.thread_queue.pop(0)
                while (self.thread_queue and
                       self.thread_queue[0] is None):
                    self.thread_queue.pop(0)
                break

    def update_locations(self):
        """Download and update locations of vehicles."""
        try:
            f = self.opener.open(self.url, timeout=10)
            text = f.read(102400).decode("ascii", errors="ignore")
            f.close()
        except Exception as error:
            print("Failed to download data: {}".format(str(error)))
            return
        for id, vehicle in self.vehicles.items():
            vehicle.state = states.REMOVE
        for line in text.splitlines():
            items = line.split(";")
            if not items[1:]: continue
            try:
                id, route = items[0:2]
                x, y, bearing = map(float, items[2:5])
            except Exception:
                print("Failed to parse line: {}".format(repr(line)))
                continue
            try:
                vehicle = self.vehicles[id]
                vehicle.state = states.UPDATE
            except KeyError:
                # A new vehicle has entered the bounding box.
                self.vehicles[id] = Vehicle(id=id, route=route)
                vehicle = self.vehicles[id]
                vehicle.state = states.ADD
            vehicle.route = route
            vehicle.x = x
            vehicle.y = y
            vehicle.bearing = bearing

    def update_map(self):
        """Update vehicle markers."""
        for id, vehicle in list(self.vehicles.items()):
            if vehicle.state == states.ADD:
                pyotherside.send("add-vehicle",
                                 vehicle.id,
                                 vehicle.x,
                                 vehicle.y,
                                 vehicle.bearing,
                                 vehicle.type,
                                 vehicle.line,
                                 vehicle.color)

                vehicle.state = states.OK
            if vehicle.state == states.UPDATE:
                pyotherside.send("update-vehicle",
                                 vehicle.id,
                                 vehicle.x,
                                 vehicle.y,
                                 vehicle.bearing,
                                 vehicle.line)

                vehicle.state = states.OK
            if vehicle.state == states.REMOVE:
                pyotherside.send("remove-vehicle", vehicle.id)
                del self.vehicles[id]

    @property
    def url(self):
        """URL pointing to HSL Live data for the current bounding box."""
        return ("http://83.145.232.209:10001/?type=vehicles"
                "&lng1={:.6f}&lat1={:.6f}&lng2={:.6f}&lat2={:.6f}"
                .format(self.bbox.xmin,
                        self.bbox.ymin,
                        self.bbox.xmax,
                        self.bbox.ymax))


app = Application(interval=3)
