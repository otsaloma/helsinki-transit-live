# Prevent brp-python-bytecompile from running.
%define __os_install_post %{___build_post}

Name: harbour-helsinki-transit-live
Version: 0.9
Release: 1
Summary: Real-time locations of HSL public transportation vehicles
License: GPLv3+
URL: http://github.com/otsaloma/helsinki-transit-live
Source: %{name}-%{version}.tar.xz
BuildArch: noarch
BuildRequires: make
Requires: libsailfishapp-launcher
Requires: pyotherside-qml-plugin-python3-qt5 >= 1.2
Requires: python3-base
Requires: qt5-plugin-geoservices-nokia
Requires: qt5-qtdeclarative-import-location
Requires: qt5-qtdeclarative-import-positioning >= 5.2
Requires: sailfishsilica-qt5

%description
Real-time locations of Helsinki Region Transport (HSL) public transportation
vehicles.

%prep
%setup -q

%install
make DESTDIR=%{buildroot} PREFIX=/usr install

%files
%doc AUTHORS.md COPYING NEWS.md README.md TODO.md
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
