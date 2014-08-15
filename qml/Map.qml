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
        map.setZoomLevel(15);
        map.zoomLevelPrev = map.zoomLevel;
        map.gps.start();
    }

    gesture.onPinchFinished: {
        // Round piched zoom level to avoid fuzziness.
        if (map.zoomLevel < map.zoomLevelPrev) {
            map.zoomLevel % 1 < 0.75 ?
                map.setZoomLevel(Math.floor(map.zoomLevel)):
                map.setZoomLevel(Math.ceil(map.zoomLevel));
        } else if (map.zoomLevel > map.zoomLevelPrev) {
            map.zoomLevel % 1 > 0.25 ?
                map.setZoomLevel(Math.ceil(map.zoomLevel)):
                map.setZoomLevel(Math.floor(map.zoomLevel));
        }
    }

    Keys.onPressed: {
        // Allow zooming with plus and minus keys on the emulator.
        (event.key == Qt.Key_Plus) && map.setZoomLevel(map.zoomLevel+1);
        (event.key == Qt.Key_Minus) && map.setZoomLevel(map.zoomLevel-1);
    }

    onPositionChanged: {
        // Do initial centering on big hops before positioning stabilises.
        if (!map.position.coordinate.longitude) return;
        if (!map.position.coordinate.latitude) return;
        if (Date.now() - map.gps.initTime < 10000) {
            if (gps.coordinatePrev.distanceTo(gps.position.coordinate) > 250) {
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

    function setZoomLevel(zoom) {
        // Set the current zoom level.
        map.zoomLevelPrev = map.zoomLevel;
        map.zoomLevel = zoom;
    }

    function start() {
        // Start periodic vehicle and GPS updates.
        if (py.ready)
            py.call("htl.app.start", [], null);
        map.gps.start();
        // For some reason we need to do something to trigger a redraw
        // to avoid only a part of tiles being displayed at start.
        map.pan(1, -1);
        map.pan(-1, 1);
    }

    function stop() {
        // Stop periodic vehicle and GPS updates.
        if (py.ready)
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
