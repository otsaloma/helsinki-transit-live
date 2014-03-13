/* -*- coding: utf-8-unix -*-
 *
 * Copyright (C) 2013-2014 Osmo Salomaa
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import QtQuick 2.0
import QtLocation 5.0
import QtPositioning 5.0
import "."

Map {
    id: map
    anchors.fill: parent
    center: QtPositioning.coordinate(60.169, 24.941)
    focus: true
    gesture.enabled: true
    plugin: MapPlugin {}

    property var gps: PositionSource {}
    property var position: map.gps.position
    property var positionMarker: PositionMarker {}
    property double positionPrevX: null
    property double positionPrevY: null
    property var vehicles: []

    Component.onCompleted: {
        map.zoomLevel = 15;
        map.gps.start();
    }

    Keys.onPressed: {
        // Allow zooming with plus and minus keys on the emulator.
        (event.key == Qt.Key_Plus) && map.zoomLevel++;
        (event.key == Qt.Key_Minus) && map.zoomLevel--;
    }

    onPositionChanged: {
        if (!map.positionPrevX) {
            // Center map on first position data received.
            map.center = map.position.coordinate;
        } else if (Date.now() - map.gps.initTime < 9999) {
            // Calculate approximate distance around Helsinki latitude
            // to the previous positioning value and center map if that
            // distance is above threshold.
            var x2 = map.position.coordinate.longitude;
            var y2 = map.position.coordinate.latitude;
            var xd = (x2 - map.positionPrevX) *  56000;
            var yd = (y2 - map.positionPrevY) * 111000;
            if (Math.sqrt(xd*xd + yd*yd) > 250)
                map.center = map.position.coordinate;
        } else if (map.gps.updateInterval < 5000) {
            map.gps.updateInterval = 5000;
        }
        map.positionMarker.coordinate = map.position.coordinate;
        map.positionPrevX = map.position.coordinate.longitude;
        map.positionPrevY = map.position.coordinate.latitude;
    }

    function addVehicle(id, x, y, bearing, type, line, color) {
        // Add a marker to the map for a new vehicle.
        var component = Qt.createComponent("Vehicle.qml");
        var item = component.createObject(map);
        item.vehicleId = id;
        item.coordinate = QtPositioning.coordinate(y, x);
        item.bearing = bearing;
        item.type = type;
        item.line = line;
        item.color = color;
        map.vehicles.push(item);
        map.addMapItem(item);
    }

    function removeVehicle(id) {
        // Remove vehicle markers that match id.
        for (var i = map.vehicles.length-1; i >= 0; i--) {
            if (map.vehicles[i].vehicleId != id) continue;
            map.removeMapItem(map.vehicles[i]);
            map.vehicles.splice(i, 1);
        }
    }

    function sendBBox() {
        // Send coordinates of the visible area to the Python backend.
        if (map.width <= 0 || map.height <= 0) return;
        var nw = map.toCoordinate(Qt.point(0, 0));
        var se = map.toCoordinate(Qt.point(map.width, map.height));
        var bbox = [nw.longitude, se.longitude, se.latitude, nw.latitude];
        py.call_sync("htl.app.set_bbox", bbox);
    }

    function start() {
        // Start periodic vehicle and GPS updates.
        if (!py.ready) return;
        py.call_sync("htl.app.start", []);
        map.gps.start();
    }

    function stop() {
        // Stop periodic vehicle and GPS updates.
        if (!py.ready) return;
        py.call_sync("htl.app.stop", []);
        map.gps.stop();
    }

    function updateVehicle(id, x, y, bearing, line) {
        // Update location markers of vehicles that match id.
        for (var i = 0; i < map.vehicles.length; i++) {
            if (map.vehicles[i].vehicleId != id) continue;
            map.vehicles[i].coordinate.longitude = x;
            map.vehicles[i].coordinate.latitude = y;
            map.vehicles[i].bearing = bearing;
            map.vehicles[i].line = line;
        }
    }
}
