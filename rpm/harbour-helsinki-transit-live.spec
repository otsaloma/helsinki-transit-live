# Prevent brp-python-bytecompile from running.
%define __os_install_post %{___build_post}

# "Harbour RPM packages should not provide anything".
%define __provides_exclude_from ^%{_datadir}/.*$

Name: harbour-helsinki-transit-live
Version: 1.0
Release: 1
Summary: Real-time locations of HSL public transportation vehicles
License: GPLv3+
URL: http://github.com/otsaloma/helsinki-transit-live
Source: %{name}-%{version}.tar.xz
BuildArch: noarch
BuildRequires: make
Requires: libsailfishapp-launcher
Requires: pyotherside-qml-plugin-python3-qt5 >= 1.2
Requires: qt5-plugin-geoservices-nokia
Requires: qt5-qtdeclarative-import-location
Requires: qt5-qtdeclarative-import-positioning >= 5.2
Requires: sailfishsilica-qt5

%description
View buses, trams, trains and metro moving in real-time on a map.

Included are a part of Helsinki Region Transport (HSL) public transportation
vehicles (currently trams, metro and kutsuplus). Positions of vehicles are from
the HSL Live API and based on GPS-positioning.

%prep
%setup -q

%install
make DESTDIR=%{buildroot} PREFIX=/usr install

%files
%defattr(-,root,root,-)
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
