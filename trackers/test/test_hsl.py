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
        self.bbox = dict(xmin=24.91, ymin=60.11, xmax=25.01, ymax=60.19)

    def test__guess_type(self):
        assert self.tracker._guess_type("M") == "metro"
        assert self.tracker._guess_type("A") == "train"
        assert self.tracker._guess_type("4") == "tram"
        assert self.tracker._guess_type("7A") == "tram"
        assert self.tracker._guess_type("10") == "tram"
        assert self.tracker._guess_type("58") == "bus"
        assert self.tracker._guess_type("58B") == "bus"
        assert self.tracker._guess_type("506") == "bus"
