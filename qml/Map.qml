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
import QtPositioning 5.3
import Sailfish.Silica 1.0
import "."

Map {
    id: map
    anchors.fill: parent
    center: QtPositioning.coordinate(60.169, 24.941)
    focus: true
    gesture.enabled: true
    minimumZoomLevel: 6
    plugin: MapPlugin {}

    property bool ready: false
    property bool showMenuButton: true
    property var  vehicles: []
    property real zoomLevelPrev: 8

    Behavior on center {
        CoordinateAnimation {
            duration: 500
            easing.type: Easing.InOutQuad
        }
    }

    MenuButton {}
    PositionMarker {}

    Timer {
        // XXX: For some reason we need to do something to trigger
        // a redraw to avoid only a part of tiles being displayed
        // right at start before any user panning or zooming.
        id: patchTimer
        interval: 1000
        repeat: true
        running: map.ready && app.running
        triggeredOnStart: true
        property int timesRun: 0
        onTriggered: {
            map.pan(+2, -2);
            map.pan(-2, +2);
            patchTimer.running = timesRun++ < 5;
        }
    }

    MouseArea {
        anchors.fill: parent
        onDoubleClicked: map.centerOnPosition();
    }

    Component.onCompleted: {
        // Use a daytime gray street map if available.
        for (var i = 0; i < map.supportedMapTypes.length; i++) {
            var type = map.supportedMapTypes[i];
            if (type.style  === MapType.GrayStreetMap &&
                type.mobile === true &&
                type.night  === false)
                map.activeMapType = type;
        }
        map.center = QtPositioning.coordinate(60.169, 24.941);
        map.centerOnPosition();
        gps.onInitialCenterChanged.connect(map.centerOnPosition);
        // XXX: Must set zoomLevel in onCompleted.
        // http://bugreports.qt-project.org/browse/QTBUG-40779
        map.setZoomLevel(Screen.sizeCategory >= Screen.Large ? 14 : 13);
        map.ready = true;
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
        (event.key === Qt.Key_Plus)  && map.setZoomLevel(map.zoomLevel+1);
        (event.key === Qt.Key_Minus) && map.setZoomLevel(map.zoomLevel-1);
    }

    function addVehicle(props) {
        // Add a marker to the map for a new vehicle.
        var component = Qt.createComponent("Vehicle.qml");
        var item = component.createObject(map);
        item.uid = props.id;
        item.coordinate = QtPositioning.coordinate(props.y, props.x);
        item.bearing = props.bearing || 0;
        item.type = props.type;
        item.line = props.line;
        item.color = props.color;
        map.vehicles.push(item);
        map.addMapItem(item);
    }

    function centerOnPosition() {
        // Center map on current position.
        map.center = QtPositioning.coordinate(
            gps.position.coordinate.latitude,
            gps.position.coordinate.longitude);

    }

    function removeAllVehicles() {
        // Remove all vehicle markers.
        while (map.vehicles.length > 0) {
            map.removeMapItem(map.vehicles[0]);
            map.vehicles[0].destroy();
            map.vehicles.shift();
        }
    }

    function removeVehicle(id) {
        // Remove vehicle marker that matches id.
        for (var i = map.vehicles.length-1; i >= 0; i--) {
            if (map.vehicles[i].uid !== id) continue;
            map.removeMapItem(map.vehicles[i]);
            map.vehicles[i].destroy();
            map.vehicles.splice(i, 1);
            return;
        }
    }

    function setZoomLevel(zoom) {
        // Set the current zoom level.
        map.zoomLevel = zoom;
        map.zoomLevelPrev = zoom;
    }

    function updateVehicle(props) {
        // Update vehicle marker that matches id.
        for (var i = 0; i < map.vehicles.length; i++) {
            if (map.vehicles[i].uid !== props.id) continue;
            var coord = QtPositioning.coordinate(props.y, props.x);
            // If bearing missing, calculate based on coordinates.
            props.bearing = props.bearing ||
                map.vehicles[i].coordinate.azimuthTo(coord);
            map.vehicles[i].coordinate = coord;
            map.vehicles[i].bearing = props.bearing;
            map.vehicles[i].line = props.line;
            return;
        }
        // Add missing vehicle.
        map.addVehicle(props);
    }
}
