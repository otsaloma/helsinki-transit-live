/* -*- coding: utf-8-unix -*-
 *
 * Copyright (C) 2013 Osmo Salomaa
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

    property var  coordinatePrev: QtPositioning.coordinate(0, 0)
    property var  gps: PositionSource {}
    property var  position: map.gps.position
    property var  positionMarker: PositionMarker {}
    property var  vehicles: []
    property real zoomLevelPrev: -1

    Component.onCompleted: {
        map.zoomLevel = 15;
        map.zoomLevelPrev = map.zoomLevel;
        map.gps.start();
        // For some reason we need to do something to trigger a redraw
        // to avoid only a part of tiles being displayed at start.
        map.clearMapItems();
    }

    gesture.onPinchFinished: {
        // Round piched zoom level to avoid fuzziness.
        if (map.zoomLevel < map.zoomLevelPrev) {
            map.zoomLevel % 1 < 0.75 ?
                map.zoomLevel = Math.floor(map.zoomLevel) :
                map.zoomLevel = Math.ceil(map.zoomLevel);
            map.zoomLevelPrev = map.zoomLevel;
        } else if (map.zoomLevel > map.zoomLevelPrev) {
            map.zoomLevel % 1 > 0.25 ?
                map.zoomLevel = Math.ceil(map.zoomLevel) :
                map.zoomLevel = Math.floor(map.zoomLevel);
            map.zoomLevelPrev = map.zoomLevel;
        }
    }

    Keys.onPressed: {
        // Allow zooming with plus and minus keys on the emulator.
        (event.key == Qt.Key_Plus) && map.zoomLevel++;
        (event.key == Qt.Key_Minus) && map.zoomLevel--;
        map.zoomLevelPrev = map.zoomLevel;
    }

    onPositionChanged: {
        if (!map.position.coordinate.longitude ||
            !map.position.coordinate.latitude) return;
        if (Date.now() - map.gps.initTime < 9999) {
            // Calculate approximate distance around Helsinki latitude
            // to the previous positioning value and center map if that
            // distance is above threshold.
            var x2 = map.position.coordinate.longitude;
            var y2 = map.position.coordinate.latitude;
            var xd = (x2 - map.coordinatePrev.longitude) * 56000;
            var yd = (y2 - map.coordinatePrev.latitude) * 111000;
            if (Math.sqrt(xd*xd + yd*yd) > 250) {
                map.center.longitude = map.position.coordinate.longitude;
                map.center.latitude = map.position.coordinate.latitude;
            }
        } else if (map.gps.updateInterval < 5000) {
            // Reduce GPS polling after initial centering is done.
            map.gps.updateInterval = 5000;
        }
        map.coordinatePrev.longitude = map.position.coordinate.longitude;
        map.coordinatePrev.latitude = map.position.coordinate.latitude;
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
        py.call("htl.app.set_bbox", bbox, null);
    }

    function start() {
        // Start periodic vehicle and GPS updates.
        if (!py.ready) return;
        py.call("htl.app.start", [], null);
        map.gps.start();
    }

    function stop() {
        // Stop periodic vehicle and GPS updates.
        if (!py.ready) return;
        py.call("htl.app.stop", [], null);
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
