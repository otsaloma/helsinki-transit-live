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
import http.client
import pyotherside
import queue
import sys
import threading
import time

__all__ = ("Application",)


class Application:

    """Show real-time locations of HSL public transportation vehicles."""

    def __init__(self, interval):
        """Initialize an :class:`Application` instance."""
        self.bbox = htl.BBox(0,0,0,0)
        self._event_queue = queue.Queue()
        self._headers = None
        self.interval = interval
        self._http = None
        self._timestamp = int(time.time()*1000)
        self.vehicles = {}
        self._init_event_thread()
        self._init_http_connection()

    def _init_event_thread(self):
        """Initialize the event handling thread."""
        target = self._process_event_queue
        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    def _init_http_connection(self):
        """Initialize a persistent HTTP connection."""
        # http://developer.reittiopas.fi/pages/en/other-apis.php
        self._http = http.client.HTTPConnection("83.145.232.209:10001", timeout=10)
        agent = "helsinki-transit-live/{}".format(htl.__version__)
        self._headers = {"Connection": "Keep-Alive",
                         "User-Agent": agent}

    def _process_event_queue(self):
        """Monitor the event queue and feed items for update."""
        while True:
            do_update, timestamp = self._event_queue.get()
            if do_update:
                self._update(timestamp)
            self._event_queue.task_done()

    def set_bbox(self, xmin, xmax, ymin, ymax):
        """Set coordinates of the bounding box."""
        self.bbox.xmin = xmin
        self.bbox.xmax = xmax
        self.bbox.ymin = ymin
        self.bbox.ymax = ymax

    def start(self):
        """Start threaded infinite periodic updates."""
        self._timestamp = int(time.time()*1000)
        self._event_queue.put((True, self._timestamp))

    def stop(self):
        """Stop threaded infinite periodic updates."""
        self._timestamp = int(time.time()*1000)
        self._event_queue.put((False, self._timestamp))

    def _update(self, timestamp):
        """Start infinite periodic updates."""
        while timestamp == self._timestamp:
            pyotherside.send("send-bbox")
            time.sleep(self.interval/2)
            if self.bbox.area > 0:
                self._update_locations()
                self._update_map()
            time.sleep(self.interval/2)

    def _update_locations(self):
        """Download and update locations of vehicles."""
        try:
            self._http.request("GET", self._url, headers=self._headers)
            response = self._http.getresponse()
            if response.status != 200:
                raise Exception("Server responded {}: {}"
                                .format(repr(response.status),
                                        repr(response.reason)))

            text = response.read(102400).decode("ascii", errors="ignore")
        except Exception as error:
            print("Failed to download data: {}"
                  .format(str(error)),
                  file=sys.stderr)

            self._http.close()
            self._init_http_connection()
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

    def _update_map(self):
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
    def _url(self):
        """URL pointing to HSL Live data for the current bounding box."""
        # http://developer.reittiopas.fi/pages/en/other-apis.php
        return ("http://83.145.232.209:10001/?type=vehicles"
                "&lng1={:.6f}&lat1={:.6f}&lng2={:.6f}&lat2={:.6f}"
                .format(self.bbox.xmin,
                        self.bbox.ymin,
                        self.bbox.xmax,
                        self.bbox.ymax))
