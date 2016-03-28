Helsinki Transit Live 1.3
=========================

* [ ] Use the new [Digitransit HSL MQTT API][1.3a] (compared to the
      previous HSL Live API, this adds buses and trains)
    - Trams keep changing lines (IDs not unique?)
    - Use a queue to avoid sending updates to QML too often?
    - Clean obsolete vehicles periodically?

[1.3a]: http://digitransit.fi/en/developers/service-catalogue/internal-components/navigator-server/
