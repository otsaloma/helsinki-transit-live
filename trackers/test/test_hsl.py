# -*- coding: utf-8 -*-

# Copyright (C) 2016 Osmo Salomaa
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
import importlib.machinery
import os


class TestTracker(htl.test.TestCase):

    def setup_method(self, method):
        path = os.path.join(os.path.dirname(__file__), "..", "hsl.py")
        loader = importlib.machinery.SourceFileLoader("tracker", path)
        self.tracker = loader.load_module("tracker").Tracker()

    def test_list_lines(self):
        lines = self.tracker.list_lines()
        assert isinstance(lines, list)
        assert len(lines) > 100
