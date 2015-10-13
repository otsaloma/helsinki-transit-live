# -*- coding: utf-8 -*-

# Copyright (C) 2015 Osmo Salomaa
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import htl.test


class TestApplication(htl.test.TestCase):

    def setup_method(self, method):
        self.app = htl.Application(3)
        self.app.bbox = htl.BBox(24.927, 24.956, 60.165, 60.176)

    def test__update_locations(self):
        # Data from the API will be blank at night time,
        # so we can only test that the server doesn't respond
        # with an error and request_url raise an exception.
        text = htl.http.request_url(self.app._url, "utf_8")
        assert isinstance(text, str)
