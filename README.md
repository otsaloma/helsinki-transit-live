Helsinki Transit Live
=====================

![Not Maintained](https://img.shields.io/maintenance/no/2018.svg)

Helsinki Transit Live is an application for Sailfish OS to view
real-time locations of Helsinki Region Transport (HSL) public transport
vehicles. It uses the [Digitransit HSL MQTT API][1] and should display
data matching the [official web interface][2].

[1]: https://digitransit.fi/en/developers/apis/4-realtime-api/vehicle-positions/
[2]: https://dev.hsl.fi/live/

Helsinki Transit Live is free software released under the GNU General
Public License (GPL), see the file [`COPYING`](COPYING) for details.

For testing purposes you can just run `/usr/lib/qt5/bin/qmlscene
qml/helsinki-transit-live.qml`. For installation, you probably want an
RPM-package; for instructions on building that, see relevant parts from
the file [`RELEASING.md`](RELEASING.md).
