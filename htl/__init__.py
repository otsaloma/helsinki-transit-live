# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Osmo Salomaa
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

"""
Show real-time locations of HSL public transportation vehicles.

http://developer.reittiopas.fi/pages/en/other-apis.php
http://transport.wspgroup.fi/hklkartta/
"""

__version__ = "0.4"

import collections
states = collections.namedtuple("State", "OK ADD REMOVE UPDATE")(1,2,3,4)

from htl.bbox import *
from htl.vehicle import *
from htl.application import *

def main():
    """Initialize application."""
    global app
    app = Application(interval=3)
    app.start()
