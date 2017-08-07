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
import pyotherside
import sys
import time

DOMAIN = "213.138.147.225"
PORT = 1883


class Tracker:

    def __init__(self):
        """Initialize a :class:`Tracker` instance."""
        self._client = None
        self._disconnected = False
        self._topics = []
        self._utime = -1
        self._init_client()

    def _init_client(self):
        """Initialize and connect the MQTT client."""
        self._client = paho.mqtt.client.Client()
        self._client.on_connect  = self._on_connect
        self._client.on_disconnect  = self._on_disconnect
        self._client.on_message = self._on_message
        self._connect()

    @htl.util.silent(Exception, tb=True)
    def bootstrap(self):
        """Fetch the last known positions of vehicles."""
        self._utime = time.time()
        url = "http://api.digitransit.fi/realtime/vehicle-positions/v1/hfp/journey/"
        vehicles = htl.http.get_json(url)
        lines = htl.app.filters.get_lines()
        pyotherside.send("remove-all-vehicles")
        for topic, payload in vehicles.items():
            parts = topic.split("/")
            if len(parts) < 6: continue
            if not parts[5] in lines: continue
            message = paho.mqtt.client.MQTTMessage()
            message.topic = topic
            message.payload = json.dumps(payload)
            self._on_message(self._client, None, message)

    def _connect(self):
        """Establish MQTT connection to DOMAIN, PORT."""
        try:
            self._client.connect(DOMAIN, PORT)
        except Exception as error:
            print("Failed to establish MQTT connection: {}"
                  .format(str(error)),
                  file=sys.stderr)

    def _ensure_str(self, blob):
        """Return `blob` converted to ``str`` if ``bytes``."""
        if isinstance(blob, bytes):
            return blob.decode("utf_8", errors="replace")
        return blob

    @htl.util.api_query(fallback=[])
    def list_lines(self):
        """Return a list of available lines."""
        # XXX: There doesn't seem to be any list of lines available
        # that support realtime information, so we have to get the
        # full list of lines from the Digitransit routing API.
        url = "http://api.digitransit.fi/routing/v1/routers/hsl/index/routes"
        lines = htl.http.get_json(url)
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

    def _on_connect(self, client, userdata, flags, rc):
        """Keep track of `client`'s connection state."""
        self._disconnected = False
        for topic in self._topics:
            print("Subscribe: {}".format(topic))
            self._client.subscribe(topic)

    def _on_disconnect(self, client, userdata, rc):
        """Keep track of `client`'s connection state."""
        self._disconnected = True
        for topic in self._topics:
            print("Unsubscribe: {}".format(topic))
            self._client.unsubscribe(topic)

    @htl.util.silent(Exception)
    def _on_message(self, client, userdata, message):
        """Parse and relay updates to positions of vehicles."""
        self._utime = time.time()
        topic = self._ensure_str(message.topic).split("/")
        payload = self._ensure_str(message.payload)
        payload = json.loads(payload)["VP"]
        vehicle = {
            "id":   topic[4],
            "code": topic[5],
            "line": self._parse_line(topic[5]),
            "type": self._parse_type(topic[3]),
            "x":    float(payload["long"]),
            "y":    float(payload["lat"]),
        }
        if vehicle["id"] in ("0", "XXX"): raise ValueError
        if vehicle["line"] in ("0", "XXX"): raise ValueError
        with htl.util.silent(Exception):
            vehicle["bearing"] = float(payload["hdg"])
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
            return code[4] if len(code) > 4 else ""
        # Buses, trams and ferries.
        line = code[1:5].strip()
        while len(line) > 1 and line.startswith("0"):
            line = line[1:].strip()
        return line if line else ""

    def _parse_type(self, type):
        """Parse human readable type from `type`."""
        return dict(rail="train",
                    subway="metro",
                    tram="tram",
                    bus="bus",
                    ferry="ferry").get(type.lower(), "")

    def quit(self):
        """Stop monitoring and disconnect the client."""
        self._client.loop_stop()
        self._client.disconnect()

    def start(self):
        """Start monitoring for updates to vehicle positions."""
        if self._disconnected:
            self._connect()
        # At application start or after a significant period inactivity
        # (using another application), load a cache dump of last known
        # vehicle locations and update all vehicles in one go.
        if time.time() - self._utime > 300:
            self.bootstrap()
        self._client.loop_start()

    def stop(self):
        """Stop monitoring for updates to vehicle positions."""
        self._client.loop_stop()

    def update_filters(self):
        """Update vehicle filters, return ``True`` if changed."""
        topics = []
        filters = htl.app.filters.get_filters()
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
