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
import QtPositioning 5.3
import Sailfish.Silica 1.0
import "."

ApplicationWindow {
    id: app
    allowedOrientations: defaultAllowedOrientations
    cover: Cover { id: cover }
    initialPage: Page {
        id: page
        allowedOrientations: app.defaultAllowedOrientations
        Map { id: map }
    }
    property bool running: applicationActive || cover.active
    PositionSource { id: gps }
    Python { id: py }
    Component.onCompleted: {
        py.setHandler("remove-all-vehicles", map.removeAllVehicles);
        py.setHandler("update-vehicle", map.updateVehicle);
    }
    Component.onDestruction: {
        py.ready && py.call_sync("htl.app.quit", []);
    }
    onRunningChanged: {
        if (!py.ready) return;
        app.running ?
            py.call("htl.app.start", [], null) :
            py.call("htl.app.stop", [], null);
    }
}
