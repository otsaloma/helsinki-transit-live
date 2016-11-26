2016-11-26: Helsinki Transit Live 1.4.205
=========================================

* Adapt to Nokia/HERE map plugin changes in Sailfish OS 2.0.5
  "Haapajoki"

2016-08-04: Helsinki Transit Live 1.4
=====================================

* Fix layouts, padding, spacing, icon sizes and font sizes to work
  better across different size and different pixel density screens
* Set the initial zoom level one higher on a tablet

Helsinki Transit Live 1.3.2
===========================

* Update API URLs

Helsinki Transit Live 1.3.1
===========================

* Handle errors connecting to the MQTT API without crashing
  the whole Python side of the app

Helsinki Transit Live 1.3
=========================

* Use the new [Digitransit HSL MQTT API][1.3a] (compared to the
  previous HSL Live API, this adds buses and trains)
* Add line filters
* Redraw tram shape in icon

[1.3a]: http://digitransit.fi/en/developers/service-catalogue/internal-components/navigator-server/

Helsinki Transit Live 1.2
=========================

* Add new application icon sizes for tablet and whatever else
* Default to zoom level 14 (one further out than before)

Helsinki Transit Live 1.1
=========================

* Use a mobile map, i.e. larger font in text labels

Helsinki Transit Live 1.0.1
===========================

* Allow all default orientations (all on a tablet and all except
  inverted portrait on a phone)
* Fix error resetting HTTP connection
* Ensure that blocking HTTP connection pool operations terminate
  immediately and gracefully on application exit

Helsinki Transit Live 1.0
=========================

* Allow landscape orientation (requires Sailfish OS 1.1.4
  "Äijänpäivänjärvi" to work correctly)
* Don't install `%doc` files (`COPYING`, `README`, etc.)
* Remove python3-base from RPM dependencies
* Prevent provides in RPM package

Helsinki Transit Live 0.10
==========================

* Center on position by double-tapping map
* Animate vehicle and position changes
* Animate centering of map
* Make vehicle icons slightly bigger
* Destroy dynamically created QML objects when no longer used
* Fix application icon rasterization
* Bump required QtPositioning version to 5.2 and use the 5.3 API
  (probably available since Sailfish OS 1.1.0.38 "Uitukka")

Helsinki Transit Live 0.9
=========================

* Use a grey daytime street map if available (this should work on
  Sailfish OS 1.1.0.38 "Uitukka" and just fall back on the normal
  street map in earlier versions)

Helsinki Transit Live 0.8
=========================

* Add an active mini map cover
* Download data at a buffer outside screen to avoid having
  to wait for an update after minor panning
* Fix icon shapes

Helsinki Transit Live 0.7
=========================

* Fix map tiles not being displayed or only a part being displayed
  at start, before any interaction
* Bump required PyOtherSide version to 1.2 (included in Sailfish OS
  1.0.4.20 "Ohijärvi" released 2014-03-17)

Helsinki Transit Live 0.6.1
===========================

* Fix initial centering

Helsinki Transit Live 0.6
=========================

* Use a persistent HTTP connection (this should make updating
  more regular and reliable)
* Use discrete zoom levels to avoid fuzziness

Helsinki Transit Live 0.5
=========================

* Don't crash anymore

Helsinki Transit Live 0.4
=========================

* Center initially on current position
* Show the current position with a marker
* Shorten name in the app launcher to "Transit Live" (which is
  probably better than the clipped "Helsinki Tran...")
* Redraw tram shape in icon

Helsinki Transit Live 0.3
=========================

* Increase data download timeout to ten seconds
* Set user agent for data downloading
* Allow plus and minus keys to be used for zooming (this is to ease
  testing on the emulator and hopefully doesn't break anything in
  actual device use)

Helsinki Transit Live 0.2.4
===========================

* Redraw icon using official template and change shape to match
  in-app vehicle icons

Helsinki Transit Live 0.2.3
===========================

* Be more robust guessing vehicle type

Helsinki Transit Live 0.2.2
===========================

* Fix guessing vehicle type
* Use black color for vehicles of unrecognized type
* Fix updating route label

Helsinki Transit Live 0.2.1
===========================

* Fix vehicle icon anchor points

Helsinki Transit Live 0.2
=========================

* Ship simple icons instead using ones from the web interface
* Use text labels instead of icons for route names (this should
  fix missing route names for some newer lines)
* Keep updating route label in case vehicle changes its route
* Use labels "M" and "V" for metro instead of "1" and "2"

Helsinki Transit Live 0.1
=========================

Initial release.
