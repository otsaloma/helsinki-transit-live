# -*- coding: utf-8 -*-

# Copyright (C) 2014 Osmo Salomaa
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

"""Miscellaneous helper functions."""

import contextlib
import functools
import json
import sys


def locked_method(function):
    """
    Decorator for methods to be run thread-safe.

    Requires class to have an instance variable '_lock'.
    """
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        with args[0]._lock:
            return function(*args, **kwargs)
    return wrapper

def read_json(path):
    """Read data from JSON file at `path`."""
    try:
        with open(path, "r", encoding="utf_8") as f:
            return json.load(f)
    except Exception as error:
        print("Failed to read file {}: {}"
              .format(repr(path), str(error)),
              file=sys.stderr)
        raise # Exception

@contextlib.contextmanager
def silent(*exceptions):
    """Try to execute body, ignoring `exceptions`."""
    try:
        yield
    except exceptions:
        pass

def type_to_color(type):
    """Return hexadecimal color for type."""
    # XXX: This should really be up to trackers to define differently,
    # but must match colors of PNG icons shown in the QML map.
    if type == "train":
        return "#8c4799"
    if type == "metro":
        return "#ff6319"
    if type == "tram":
        return "#00985f"
    return "#007ac9"
