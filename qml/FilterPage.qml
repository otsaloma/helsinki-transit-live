/* -*- coding: utf-8-unix -*-
 *
 * Copyright (C) 2016 Osmo Salomaa
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

Page {
    id: page
    allowedOrientations: app.defaultAllowedOrientations
    property var lines: []
    property bool loading: false
    property string query: ""
    SilicaGridView {
        id: view
        anchors.fill: parent
        anchors.leftMargin: Theme.paddingLarge/2
        cellWidth: (page.width - 1.5*Theme.paddingLarge) / 3
        // Prevent list items from stealing focus.
        currentIndex: -1
        delegate: ListItem {
            id: listItem
            clip: true
            contentHeight: lineSwitch.height
            width: view.cellWidth
            TextSwitch {
                id: lineSwitch
                checked: model.selected
                description: "%1<br>%2".arg(model.type).arg(model.area)
                text: model.line
                // Avoid wrapping description.
                width: 3*page.width
                Component.onCompleted: view.cellHeight = lineSwitch.height;
                onCheckedChanged: {
                    if (lineSwitch.checked === model.selected) return;
                    for (var i = 0; i < page.lines.length; i++)
                        if (page.lines[i].code === model.code)
                            page.lines[i].selected = lineSwitch.checked;
                    view.model.setProperty(model.index, "selected", lineSwitch.checked);
                    lineSwitch.checked ?
                        py.call("htl.app.filters.add_line", [model.code], null) :
                        py.call("htl.app.filters.remove_line", [model.code], null);
                }
            }
        }
        header: Column {
            height: header.height + searchField.height
            width: parent.width
            PageHeader {
                id: header
                title: "Lines"
            }
            SearchField {
                id: searchField
                inputMethodHints: Qt.ImhNoPredictiveText | Qt.ImhNoAutoUppercase
                placeholderText: "Line or vehicle type"
                visible: !page.loading
                width: parent.width
                onTextChanged: {
                    page.query = searchField.text;
                    page.filterLines();
                }
            }
            Component.onCompleted: view.searchField = searchField;
        }
        model: ListModel {}
        property var searchField: undefined
        PullDownMenu {
            MenuItem {
                text: "About"
                onClicked: app.pageStack.push("AboutPage.qml");
            }
        }
        ViewPlaceholder {
            id: viewPlaceholder
            enabled: false
            text: "No lines selected"
        }
        VerticalScrollDecorator {}
    }
    BusyModal {
        id: busy
        running: page.loading
    }
    onStatusChanged: {
        if (page.status === PageStatus.Activating) {
            view.model.clear();
            viewPlaceholder.enabled = false;
            page.loading = true;
            busy.text = "Loading";
        } else if (page.status === PageStatus.Active) {
            page.loadLines();
        } else if (page.status === PageStatus.Deactivating) {
            // Update data downloading and map display.
            py.call("htl.app.update_filters", [], function(changed) {
                changed && py.call("htl.app.bootstrap", [], null);
            });
        }
    }
    function filterLines() {
        // Filter lines for current search field text.
        view.model.clear();
        viewPlaceholder.enabled = false;
        for (var i = 0; i < page.lines.length; i++) {
            page.lines[i].line = page.lines[i].linePlain
            page.lines[i].type = page.lines[i].typePlain
        }
        var query = view.searchField.text.toLowerCase();
        if (query === "")
            return filterLinesSelected();
        var n = 0;
        for (var i = 0; i < page.lines.length; i++) {
            // Look for lines matching search query.
            // Only allow matches at the start of the line.
            var item = page.lines[i].line.toLowerCase();
            if (item.indexOf(query) !== 0) continue;
            page.lines[i].line = Theme.highlightText(
                page.lines[i].line, query, Theme.highlightColor);
            view.model.insert(n++, page.lines[i]);
        }
        if (n > 0) return;
        for (var i = 0; i < page.lines.length; i++) {
            // Look for types matching search query.
            // Only allow matches at the start of the type.
            var item = page.lines[i].type.toLowerCase();
            if (item.indexOf(query) !== 0) continue;
            page.lines[i].type = Theme.highlightText(
                page.lines[i].type, query, Theme.highlightColor);
            view.model.insert(n++, page.lines[i]);
        }
    }
    function filterLinesSelected() {
        // Filter view to show selected lines.
        for (var i = 0; i < page.lines.length; i++)
            if (page.lines[i].selected)
                view.model.append(page.lines[i]);
        if (view.model.count === 0)
            viewPlaceholder.enabled = true;
    }
    function loadLines() {
        // Load list of lines from the Python backend.
        var selected = py.call_sync("htl.app.filters.get_lines", []);
        py.call("htl.app.list_lines", [], function(lines) {
            if (lines.length === 0) {
                busy.error = "No lines found";
                page.loading = false;
            } else {
                for (var i = 0; i < lines.length; i++) {
                    lines[i].type = lines[i].type.charAt(0).toUpperCase() + lines[i].type.slice(1);
                    lines[i].selected = selected.indexOf(lines[i].code) > -1;
                    lines[i].linePlain = lines[i].line
                    lines[i].typePlain = lines[i].type
                }
                page.lines = lines;
                page.loading = false;
                page.filterLines();
            }
        });
    }
}
