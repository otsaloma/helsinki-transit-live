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
import time


class Tracker:

    def __init__(self):
        """Initialize a :class:`Tracker` instance."""
        self._btime = -1
        self._client = paho.mqtt.client.Client()
        self._client.on_message = self._on_message
        self._client.connect("213.138.147.225", port=1883, keepalive=60)
        self._topics = []

    @htl.util.silent(Exception)
    def bootstrap(self):
        """Fetch the last known positions of vehicles."""
        self._btime = time.time()
        url = "http://beta.digitransit.fi/navigator-server/hfp/journey/#"
        vehicles = htl.http.request_json(url)
        lines = htl.app.filters.get_lines()
        for topic, payload in vehicles.items():
            parts = topic.split("/")
            if len(parts) < 6: continue
            if not parts[5] in lines: continue
            message = paho.mqtt.client.MQTTMessage()
            message.topic = topic
            message.payload = json.dumps(payload)
            self._on_message(self._client, None, message)

    def _guess_type(self, line):
        """Guess vehicle type based on `line`."""
        if re.match(r"^[MV]$", line):
            return "metro"
        if re.match(r"^[A-Z]$", line):
            return "train"
        if re.match(r"^([1-9]|10)[A-Z]?$", line):
            return "tram"
        return "bus"

    @htl.util.api_query(fallback=[])
    def list_lines(self):
        """Return a list of available lines."""
        # XXX: There doesn't seem to be any list of lines available
        # that support realtime information, so we have to get the
        # full list of lines from the Digitransit routing API.
        url = "http://beta.digitransit.fi/otp/routers/hsl/index/routes"
        lines = htl.http.request_json(url)
        lines = [{
            "code": x["id"].replace("HSL:", ""),
            "line": x.get("shortName", self._parse_line(x["id"])),
            "description": x.get("longName", ""),
            "type": self._parse_type(x.get("mode", "")),
            "area": self._parse_area(x["id"]),
        } for x in lines]
        def line_to_sort_key(line):
            """Construct a sortable key from `line`."""
            # Break into line and modifier, pad with zeros.
            head, tail = line["line"], ""
            while head and head[0].isdigit() and head[-1].isalpha():
                tail = head[-1] + tail
                head = head[:-1]
            return head.zfill(3), tail.zfill(3)
        return sorted(lines, key=line_to_sort_key)

    @htl.util.silent(Exception)
    def _on_message(self, client, userdata, message):
        """Parse and relay updates to positions of vehicles."""
        payload = message.payload
        if isinstance(payload, bytes):
            payload = payload.decode("utf_8", errors="replace")
        blob = json.loads(payload)["VP"]
        vehicle = dict(id=str(blob["veh"]),
                       line=str(blob["desi"]),
                       x=float(blob["long"]),
                       y=float(blob["lat"]))

        if vehicle["id"] in ("0", "XXX"): raise ValueError
        if vehicle["line"] in ("0", "XXX"): raise ValueError
        # If line looks like a JORE-code, try to parse it.
        if re.match(r"^[0-9]{4}", vehicle["line"]):
            vehicle["line"] = self._parse_line(vehicle["line"])
        with htl.util.silent(Exception):
            vehicle["bearing"] = float(blob["hdg"])
        vehicle["type"] = self._guess_type(vehicle["line"])
        htl.app.update_vehicle(vehicle)

    def _parse_area(self, code):
        """Parse operation area from `code`."""
        # codes are HSL: + shortened JORE-code.
        # http://developer.reittiopas.fi/pages/en/http-get-interface-version-2.php
        code = code.replace("HSL:", "")
        if len(code) < 1: return ""
        return {"1": "Helsinki",
                "2": "Espoo",
                "3": "Regional",
                "4": "Vantaa",
                "5": "Regional",
                "7": "U-line"}.get(code[0], "Other")

    def _parse_line(self, code):
        """Parse human readable line number from `code`."""
        # codes are HSL: + shortened JORE-code.
        # http://developer.reittiopas.fi/pages/en/http-get-interface-version-2.php
        code = code.replace("HSL:", "")
        if code.startswith(("13", "3")):
            # Metro and trains.
            return code[4] if len(code) > 4 else "X"
        # Buses, trams and ferries.
        line = code[1:5].strip()
        while len(line) > 1 and line.startswith("0"):
            line = line[1:].strip()
        return line if line else "X"

    def _parse_type(self, type):
        """Parse human readable type from `type`."""
        return dict(RAIL="train",
                    SUBWAY="metro",
                    TRAM="tram",
                    BUS="bus",
                    FERRY="ferry").get(type, "")

    def set_filters(self, filters):
        """Set vehicle filters for downloading data."""
        topics = []
        for line in filters.get("lines", []):
            topics.append("/hfp/journey/+/+/{}/#".format(line))
        changed = False
        for topic in set(self._topics) - set(topics):
            print("Unsubscribe: {}".format(topic))
            self._client.unsubscribe(topic)
            self._topics.remove(topic)
            changed = True
        for topic in set(topics) - set(self._topics):
            print("Subscribe: {}".format(topic))
            self._client.subscribe(topic)
            self._topics.append(topic)
            changed = True
        return changed

    def start(self):
        """Start monitoring for updates to vehicle positions."""
        self._client.loop_start()
        # At application start or after a significant period inactivity
        # (using another application), load a cache dump of last known
        # vehicle locations and update all vehicles in one go.
        if time.time() - self._btime > 300:
            self.bootstrap()

    def stop(self):
        """Stop monitoring for updates to vehicle positions."""
        self._client.loop_stop()
