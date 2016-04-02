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
import copy
import functools
import json
import os
import random
import shutil
import socket
import stat
import sys
import traceback


def api_query(fallback):
    """Decorator for API requests with graceful error handling."""
    def outer_wrapper(function):
        @functools.wraps(function)
        def inner_wrapper(*args, **kwargs):
            try:
                # function can fail due to connection errors or errors
                # in parsing the received data. Notify the user of some
                # common errors by returning a dictionary with the error
                # message to be displayed. With unexpected errors, print
                # a traceback and return blank of correct type.
                return function(*args, **kwargs)
            except socket.timeout:
                return dict(error=True, message="Connection timed out")
            except Exception:
                traceback.print_exc()
                return copy.deepcopy(fallback)
        return inner_wrapper
    return outer_wrapper

@contextlib.contextmanager
def atomic_open(path, mode="w", *args, **kwargs):
    """A context manager for atomically writing a file."""
    # This is a simplified version of atomic_open from gaupol.
    # https://github.com/otsaloma/gaupol/blob/master/aeidon/util.py
    path = os.path.realpath(path)
    suffix = random.randint(1, 10**9)
    temp_path = "{}.tmp{}".format(path, suffix)
    try:
        if os.path.isfile(path):
            # If the file exists, use the same permissions.
            # Note that all other file metadata, including
            # owner and group, is not preserved.
            with open(temp_path, "w") as f: pass
            st = os.stat(path)
            os.chmod(temp_path, stat.S_IMODE(st.st_mode))
        with open(temp_path, mode, *args, **kwargs) as f:
            yield f
            f.flush()
            os.fsync(f.fileno())
        try:
            # Requires Python 3.3 or later.
            # Can fail in the unlikely case that
            # paths are on different filesystems.
            os.replace(temp_path, path)
        except OSError:
            # Fall back on a non-atomic operation.
            shutil.move(temp_path, path)
    finally:
        with silent(Exception):
            os.remove(temp_path)

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

def makedirs(directory):
    """Create and return `directory` or raise :exc:`OSError`."""
    directory = os.path.abspath(directory)
    if os.path.isdir(directory):
        return directory
    try:
        os.makedirs(directory)
    except OSError as error:
        if os.path.isdir(directory):
            return directory
        print("Failed to create directory {}: {}"
              .format(repr(directory), str(error)),
              file=sys.stderr)
        raise # OSError
    return directory

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
    if type == "ferry":
        return "#00b9e4"
    return "#007ac9"

def write_json(data, path):
    """Write `data` to JSON file at `path`."""
    try:
        makedirs(os.path.dirname(path))
        with atomic_open(path, "w", encoding="utf_8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4, sort_keys=True)
    except Exception as error:
        print("Failed to write file {}: {}"
              .format(repr(path), str(error)),
              file=sys.stderr)
        raise # Exception
