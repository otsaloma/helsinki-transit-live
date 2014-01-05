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

MapQuickItem {
    id: item
    property double bearing: 0
    property string color: "#0C5D9E"
    property string line: ""
    property string type: "bus"
    property string vehicleId
    sourceItem: Item {
        Image {
            id: image
            anchors.horizontalCenter: text.horizontalCenter
            anchors.verticalCenter: text.verticalCenter
            rotation: item.bearing
            source: "icons/" + item.type + ".png"
            transformOrigin: Item.Center
        }
        Rectangle {
            id: rectangle
            anchors.horizontalCenter: text.horizontalCenter
            anchors.verticalCenter: text.verticalCenter
            color: item.color
            height: text.height
            width: text.width
        }
        Text {
            id: text
            color: "white"
            font.bold: true
            font.family: "sans"
            font.pixelSize: 16
            text: item.line
            textFormat: Text.PlainText
        }
    }
}
