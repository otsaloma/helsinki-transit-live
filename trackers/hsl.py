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

"""
Public transport vehicles in the Helsinki region.

http://digitransit.fi/en/developers/service-catalogue/apis/realtime-api/
http://digitransit.fi/en/developers/service-catalogue/internal-components/navigator-server/
http://dev.hsl.fi/live/
"""

import htl
import json
import paho.mqtt.client
import re
import threading


class Tracker:

    def __init__(self):
        """Initialize a :class:`Tracker` instance."""
        self._client = paho.mqtt.client.Client()
        self._client.max_inflight_messages_set(100)
        self._client.on_message = self._on_message
        self._client.connect("213.138.147.225", port=1883, keepalive=60)
        self._lock = threading.Lock()
        self._topics = []

    def _guess_type(self, line):
        """Guess vehicle type based on `line`."""
        if re.match(r"^[MV]$", line):
            return "metro"
        if re.match(r"^[A-Z]$", line):
            return "train"
        if re.match(r"^([1-9]|10)[A-Z]?$", line):
            return "tram"
        return "bus"

    @htl.util.silent(Exception)
    def _on_message(self, client, userdata, message):
        """Parse and relay updates to positions of vehicles."""
        blob = message.payload.decode("utf_8", errors="replace")
        blob = json.loads(blob)["VP"]
        vehicle = dict(id=str(blob["veh"]),
                       line=str(blob["desi"]),
                       x=float(blob["long"]),
                       y=float(blob["lat"]))

        if vehicle["id"] in ("0", "XXX"): raise ValueError
        if vehicle["line"] in ("0", "XXX"): raise ValueError
        with htl.util.silent(Exception):
            vehicle["bearing"] = float(blob["hdg"])
        vehicle["type"] = self._guess_type(vehicle["line"])
        htl.app.update_vehicle(vehicle)

    def start(self):
        """Start monitoring for updates to vehicle positions."""
        self._client.loop_start()

    def stop(self):
        """Stop monitoring for updates to vehicle positions."""
        self._client.loop_stop()

    @htl.util.locked_method
    def update(self, props):
        """Update tracking to match `props`."""
        topics = []
        xmin = int(10 * props["xmin"])
        xmax = int(10 * props["xmax"])
        ymin = int(10 * props["ymin"])
        ymax = int(10 * props["ymax"])
        for x in range(xmin, xmax+1):
            for y in range(ymin, ymax+1):
                x0 = int(x / 10)
                x1 = int(x % 10)
                y0 = int(y / 10)
                y1 = int(y % 10)
                topics.append((
                    "/hfp/journey/+/+/+/+/+/+/+/"
                    "{y0:d};{x0:d}/{y1:d}{x1:d}/#"
                    .format(**locals())))

        for topic in set(self._topics) - set(topics):
            print("Unsubscribe: {}".format(topic))
            self._client.unsubscribe(topic)
            self._topics.remove(topic)
        for topic in set(topics) - set(self._topics):
            print("Subscribe: {}".format(topic))
            self._client.subscribe(topic)
            self._topics.append(topic)
