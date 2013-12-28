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

Map {
    id: map
    anchors.fill: parent
    center: QtPositioning.coordinate(60.169, 24.941)
    gesture.enabled: true
    plugin: MapPlugin {}

    Component.onCompleted: map.zoomLevel = 15;

    // Add type and route markers to the map for a new vehicle.
    function addVehicle(id, x, y, typeIcon, routeIcon) {
        var item = createVehicle(id, x, y, typeIcon, 55, 55)
        map.addMapItem(item);
        if (routeIcon) {
            item = createVehicle(id, x, y, routeIcon, 55, 67)
            map.addMapItem(item);
        }
    }

    // Create a new QML MapQuickItem as a child of map.
    function createVehicle(id, x, y, icon, width, height) {
        var component = Qt.createComponent("Vehicle.qml");
        var item = component.createObject(map);
        item.anchorPoint.x = width/2;
        item.anchorPoint.y = height/2;
        item.coordinate = QtPositioning.coordinate(y, x);
        item.sourceItem.source = icon;
        item.vehicleId = id;
        return item;
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

    // Update the location markers of vehicle that match id.
    function updateVehicle(id, x, y) {
        for (var i = 0; i < map.mapItems.length; i++) {
            if (map.mapItems[i].vehicleId == id) {
                map.mapItems[i].coordinate.longitude = x;
                map.mapItems[i].coordinate.latitude = y;
            }
        }
    }
}
