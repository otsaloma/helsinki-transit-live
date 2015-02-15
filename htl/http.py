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

"""Managed persistent HTTP connections."""

import htl
import http.client
import queue
import sys
import threading
import urllib.parse

HEADERS = {"Connection": "Keep-Alive",
           "User-Agent": "helsinki-transit-live/{}".format(htl.__version__)}


class ConnectionPool:

    """A managed pool of persistent per-host HTTP connections."""

    def __init__(self, threads):
        """Initialize a :class:`ConnectionPool` instance."""
        self._lock = threading.Lock()
        self._queue = {}
        self._threads = threads

    @htl.util.locked_method
    def _allocate(self, url):
        """Initialize a queue of HTTP connections to `url`."""
        key = self._get_key(url)
        if key in self._queue: return
        self._queue[key] = queue.Queue()
        for i in range(self._threads):
            self._queue[key].put(None)

    def get(self, url):
        """Return an HTTP connection to `url`."""
        key = self._get_key(url)
        if not key in self._queue:
            self._allocate(url)
        connection = self._queue[key].get()
        if connection is None:
            connection = self._new(url)
        return connection

    def _get_key(self, url):
        """Return a dictionary key for the host of `url`."""
        components = urllib.parse.urlparse(url)
        return "{}://{}".format(components.scheme, components.netloc)

    def _new(self, url):
        """Initialize and return a new HTTP connection to `url`."""
        components = urllib.parse.urlparse(url)
        print("Establishing connection to {}".format(components.netloc))
        cls = {
            "http":  http.client.HTTPConnection,
            "https": http.client.HTTPSConnection,
        }[components.scheme]
        return cls(components.netloc, timeout=10)

    def put(self, url, connection):
        """Return `connection` to the pool of connections."""
        key = self._get_key(url)
        self._queue[key].task_done()
        self._queue[key].put(connection)

    def reset(self, url):
        """Close and re-establish HTTP connection to `url`."""
        connection = self.get(url)
        with htl.util.silent(Exception):
            connection.close()
        self.put(None)


pool = ConnectionPool(1)


def request_url(url, encoding=None, retry=1):
    """
    Request and return data at `url`.

    If `encoding` is ``None``, return bytes, otherwise decode data
    to text using `encoding`. Try again `retry` times in some particular
    cases that imply a connection error.
    """
    try:
        connection = pool.get(url)
        connection.request("GET", url, headers=HEADERS)
        response = connection.getresponse()
        # Always read response to avoid
        # http.client.ResponseNotReady: Request-sent.
        blob = response.read()
        if response.status != 200:
            raise Exception("Server responded {}: {}"
                            .format(repr(response.status),
                                    repr(response.reason)))

        if encoding is None: return blob
        return blob.decode(encoding, errors="replace")
    except Exception as error:
        connection.close()
        connection = None
        # These probably mean that the connection was broken.
        broken = (BrokenPipeError, http.client.BadStatusLine)
        if not isinstance(error, broken) or retry == 0:
            print("Failed to download data: {}: {}"
                  .format(error.__class__.__name__, str(error)),
                  file=sys.stderr)
            raise # Exception
    finally:
        pool.put(url, connection)
    assert retry > 0
    return request_url(url, encoding, retry-1)
