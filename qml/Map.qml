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

Map {
    id: map
    anchors.fill: parent
    center: QtPositioning.coordinate(60.169, 24.941)
    focus: true
    gesture.enabled: true
    plugin: MapPlugin {}

    Component.onCompleted: map.zoomLevel = 15;

    // Allow zooming with plus and minus keys on the emulator.
    Keys.onPressed: {
        if (event.key == Qt.Key_Plus)
            map.zoomLevel++;
        if (event.key == Qt.Key_Minus)
            map.zoomLevel--;
    }

    // Add a marker to the map for a new vehicle.
    function addVehicle(id, x, y, bearing, type, line, color) {
        var component = Qt.createComponent("Vehicle.qml");
        var item = component.createObject(map);
        item.vehicleId = id;
        item.coordinate = QtPositioning.coordinate(y, x);
        item.bearing = bearing;
        item.type = type;
        item.line = line;
        item.color = color;
        item.anchorPoint.x = item.width/2;
        item.anchorPoint.y = item.height/2;
        map.addMapItem(item);
    }

    // Send coordinates of the visible area to the Python backend.
    function queryBBox() {
        if (map.width <= 0 || map.height <= 0) return;
        var nw = map.toCoordinate(Qt.point(0, 0));
        var se = map.toCoordinate(Qt.point(map.width, map.height));
        var bbox = [nw.longitude, se.longitude, se.latitude, nw.latitude];
        py.call("main.app.set_bbox", bbox, null);
    }

    // Remove vehicle markers that match id.
    function removeVehicle(id) {
        for (var i = map.mapItems.length-1; i >= 0; i--) {
            if (map.mapItems[i].vehicleId == id)
                map.removeMapItem(map.mapItems[i]);
        }
    }

    // Update location markers of vehicles that match id.
    function updateVehicle(id, x, y, bearing, line) {
        for (var i = 0; i < map.mapItems.length; i++) {
            if (map.mapItems[i].vehicleId == id) {
                map.mapItems[i].coordinate.longitude = x;
                map.mapItems[i].coordinate.latitude = y;
                map.mapItems[i].bearing = bearing;
                map.mapItems[i].line = line;
            }
        }
    }
}
