/* -*- coding: utf-8-unix -*-
 *
 * Copyright (C) 2014 Osmo Salomaa
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

PositionSource {
    id: gps
    active: app.running
    property var coordPrev: QtPositioning.coordinate(0, 0)
    property var initialCenter: QtPositioning.coordinate(60.169, 24.941)
    property var initTime: Date.now()
    onPositionChanged: {
        // Do initial centering on big hops before positioning stabilises.
        var coord = gps.position.coordinate;
        if (!coord.longitude || !coord.latitude) return;
        if (Date.now() - gps.initTime < 10000 &&
            gps.coordPrev.distanceTo(coord) > 250)
            gps.initialCenter = QtPositioning.coordinate(
                coord.latitude, coord.longitude);
        gps.coordPrev.longitude = coord.longitude;
        gps.coordPrev.latitude = coord.latitude;
    }
}
