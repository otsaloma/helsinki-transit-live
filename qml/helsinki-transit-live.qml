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
import Sailfish.Silica 1.0
import "."

ApplicationWindow {
    id: app
    allowedOrientations: Orientation.All
    cover: undefined
    initialPage: Page {
        id: page
        // XXX: Map gestures don't work right in landscape.
        // http://bugreports.qt-project.org/browse/QTBUG-40799
        allowedOrientations: Orientation.Portrait
        Map { id: map }
    }
    // TODO: Add cover.status when we have a cover.
    property bool running: applicationActive
    PositionSource { id: gps }
    Python { id: py }
    Component.onCompleted: {
        py.setHandler("add-vehicle", map.addVehicle);
        py.setHandler("remove-vehicle", map.removeVehicle);
        py.setHandler("send-bbox", map.sendBBox);
        py.setHandler("update-vehicle", map.updateVehicle);
    }
    onRunningChanged: {
        if (app.running && py.ready) {
            py.call("htl.app.start", [], null);
        } else if (!app.running && py.ready) {
            py.call("htl.app.stop", [], null);
        }
    }
}
