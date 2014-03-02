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

"""Show real-time locations of HSL public transportation vehicles."""

import htl
import pyotherside
import sys
import threading
import time
import urllib.request

__all__ = ("Application",)


class Application:

    """Show real-time locations of HSL public transportation vehicles."""

    def __init__(self, interval):
        """Initialize an :class:`Application` instance."""
        self.bbox = htl.BBox(0,0,0,0)
        self.interval = interval
        self.opener = None
        self.thread_queue = []
        self.vehicles = {}
        self._init_url_opener()

    def _init_url_opener(self):
        """Initialize the URL opener to use for downloading data."""
        self.opener = urllib.request.build_opener()
        agent = "helsinki-transit-live/{}".format(htl.__version__)
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
            print("Failed to download data: {}"
                  .format(str(error)),
                  file=sys.stderr)

            return
        for id, vehicle in self.vehicles.items():
            vehicle.state = htl.states.REMOVE
        for line in text.splitlines():
            items = line.split(";")
            if not items[1:]: continue
            try:
                id, route = items[0:2]
                x, y, bearing = map(float, items[2:5])
            except Exception:
                print("Failed to parse line: {}"
                      .format(repr(line)),
                      file=sys.stderr)

                continue
            try:
                vehicle = self.vehicles[id]
                vehicle.state = htl.states.UPDATE
            except KeyError:
                # A new vehicle has entered the bounding box.
                self.vehicles[id] = htl.Vehicle(id=id, route=route)
                vehicle = self.vehicles[id]
                vehicle.state = htl.states.ADD
            vehicle.route = route
            vehicle.x = x
            vehicle.y = y
            vehicle.bearing = bearing

    def update_map(self):
        """Update vehicle markers."""
        for id, vehicle in list(self.vehicles.items()):
            if vehicle.state == htl.states.ADD:
                pyotherside.send("add-vehicle",
                                 vehicle.id,
                                 vehicle.x,
                                 vehicle.y,
                                 vehicle.bearing,
                                 vehicle.type,
                                 vehicle.line,
                                 vehicle.color)

                vehicle.state = htl.states.OK
            if vehicle.state == htl.states.UPDATE:
                pyotherside.send("update-vehicle",
                                 vehicle.id,
                                 vehicle.x,
                                 vehicle.y,
                                 vehicle.bearing,
                                 vehicle.line)

                vehicle.state = htl.states.OK
            if vehicle.state == htl.states.REMOVE:
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
