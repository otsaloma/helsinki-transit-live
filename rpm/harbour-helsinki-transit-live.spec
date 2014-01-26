# Prevent brp-python-bytecompile from running.
%define __os_install_post %{___build_post}

Name: harbour-helsinki-transit-live
Version: 0.2.4
Release: 1
Summary: Real-time locations of HSL public transportation vehicles
License: GPLv3+
URL: https://github.com/otsaloma/helsinki-transit-live
Source: %{name}-%{version}.tar.xz
BuildArch: noarch
Requires: libsailfishapp-launcher
Requires: pyotherside-qml-plugin-python3-qt5
Requires: python3-base
Requires: qt5-plugin-geoservices-nokia
Requires: qt5-plugin-geoservices-osm
Requires: qt5-qtdeclarative-import-location
Requires: qt5-qtdeclarative-import-positioning
Requires: sailfishsilica-qt5

%description
Helsinki Transit Live shows real-time locations of Helsinki Region
Transport (HSL) public transportation vehicles.

%prep
%setup -q

%install
make DESTDIR=%{buildroot} PREFIX=/usr install

%files
%doc AUTHORS COPYING NEWS README TODO
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
