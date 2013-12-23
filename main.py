# -*- coding: utf-8-unix -*-

# Copyright (C) 2013 Osmo Salomaa
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

import collections
import threading
import re
import time
import urllib.request

try:
    import pyotherside
except ImportError:
    # Allow testing Python part alone.
    print("PyOtherSide not found, continuing anyway!")
    class pyotherside:
        def send(*args):
            print("send: {}".format(repr(args)))

states = collections.namedtuple("State", "OK ADD REMOVE UPDATE")(1,2,3,4)


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

    def __str__(self):
        """Return a string representation of `self`."""
        return ("BBox(xmin={:.3f}, xmax={:.3f}, ymin={:.3f}, ymax={:.3f})"
                .format(self.xmin, self.xmax, self.ymin, self.ymax))


class Vehicle:

    """Properties of a public transportation vehicle."""

    def __init__(self, **kwargs):
        """Initialize a :class:`Vehicle` instance."""
        self.type = type
        self.id = None
        self.route = None
        self.x = 0
        self.y = 0
        self.bearing = 0
        self.state = states.OK
        self.type_icon = None
        self.route_icon = None
        for name, value in kwargs.items():
            setattr(self, name, value)

    def guess_type(self):
        """Guess vehicle type based on `id`."""
        if self.id.startswith("RHKL"):
            return "tram"
        if self.id.startswith("metro"):
            return "metro"
        if self.id.startswith("H"):
            return "train"
        if self.id.startswith("K"):
            return "kutsu"
        return "bus"

    def set_icons(self):
        """Set URLs of type and route icons."""
        # Let's borrow icons from the official web interface.
        # http://transport.wspgroup.fi/hklkartta/
        bearing = round(self.bearing/45)*45
        if bearing > 315:
            bearing = 0
        self.type_icon = (
            "http://transport.wspgroup.fi/hklkartta/"
            "images/vehicles/{}{:.0f}.png"
            .format(self.type, bearing))
        if not self.route in ("", "0"):
            route = self.route
            route = re.sub(r" .*$", r"", route)
            route = re.sub(r"^([12])$", r"\1m", route)
            route = re.sub(r"(?<=[A-JL-Z])\d+$", r"", route)
            self.route_icon = (
                "http://transport.wspgroup.fi/hklkartta/"
                "images/vehicles/{}.png"
                .format(route))

    def __str__(self):
        """Return a string representation of `self`."""
        blob = "{} {} on {}:\n".format(self.type, self.id, self.route)
        for name in ("x", "y", "bearing", "state", "type_icon", "route_icon"):
            blob += " {}: {}\n".format(name, repr(getattr(self, name)))
        return(blob)


class Application:

    """Show real-time locations of HSL public transportation vehicles."""

    def __init__(self, interval):
        """Initialize an :class:`Application` instance."""
        self.bbox = BBox(0,0,0,0)
        self.interval = interval
        self.vehicles = {}

    def main(self):
        """Start infinite periodic updates."""
        while True:
            pyotherside.send("query-bbox")
            time.sleep(self.interval/2)
            if self.bbox.area > 0:
                self.update_locations()
            self.update_map()
            time.sleep(self.interval/2)

    def set_bbox(self, xmin, xmax, ymin, ymax):
        """Set coordinates of the bounding box."""
        self.bbox.xmin = xmin
        self.bbox.xmax = xmax
        self.bbox.ymin = ymin
        self.bbox.ymax = ymax

    def update_locations(self):
        """Download and update locations of vehicles."""
        try:
            f = urllib.request.urlopen(self.url, timeout=self.interval)
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
                vehicle.type = vehicle.guess_type()
                vehicle.state = states.ADD
            vehicle.x = x
            vehicle.y = y
            vehicle.bearing = bearing
            vehicle.set_icons()

    def update_map(self):
        """Update vehicle markers."""
        for id, vehicle in list(self.vehicles.items()):
            if vehicle.state == states.ADD:
                pyotherside.send("add-vehicle",
                                 vehicle.id,
                                 vehicle.x,
                                 vehicle.y,
                                 vehicle.type_icon,
                                 vehicle.route_icon)

                vehicle.state = states.OK
            if vehicle.state == states.UPDATE:
                pyotherside.send("update-vehicle",
                                 vehicle.id,
                                 vehicle.x,
                                 vehicle.y)

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
thread = threading.Thread(target=app.main)
thread.start()
