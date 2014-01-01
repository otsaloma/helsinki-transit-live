# -*- coding: us-ascii-unix -*-

name       = harbour-helsinki-transit-live
version    = 0.0
manifest   = `cat MANIFEST`
DESTDIR    =
PREFIX     = /usr/local
bindir     = $(DESTDIR)$(PREFIX)/bin
datadir    = $(DESTDIR)$(PREFIX)/share/$(name)
desktopdir = $(DESTDIR)$(PREFIX)/share/applications
icondir    = $(DESTDIR)$(PREFIX)/share/icons/hicolor/86x86/apps

.PHONY: clean dist install rpm

clean:
	rm -rf dist
	rm -f rpm/*.rpm

dist:
	$(MAKE) clean
	mkdir -p dist/$(name)-$(version)
	cp -r $(manifest) dist/$(name)-$(version)
	tar -C dist -cvJf dist/$(name)-$(version).tar.xz $(name)-$(version)

install:
	@echo "Installing scripts..."
	mkdir -p $(bindir)
	cp bin/helsinki-transit-live $(bindir)/$(name)
	@echo "Installing Python files..."
	mkdir -p $(datadir)
	cp *.py $(datadir)
	@echo "Installing QML files..."
	mkdir -p $(datadir)/qml
	cp qml/helsinki-transit-live.qml $(datadir)/qml/$(name).qml
	cp qml/[ABCDEFGHIJKLMNOPQRSTUVXYZ]*.qml $(datadir)/qml
	@echo "Installing desktop file..."
	mkdir -p $(desktopdir)
	cp data/helsinki-transit-live.desktop $(desktopdir)/$(name).desktop
	@echo "Installing icon..."
	mkdir -p $(icondir)
	cp data/helsinki-transit-live.png $(icondir)/$(name).png

rpm:
	$(MAKE) dist
	mkdir -p $$HOME/rpmbuild/SOURCES
	cp dist/$(name)-$(version).tar.xz $$HOME/rpmbuild/SOURCES
	rpmbuild -ba rpm/$(name).spec
	cp $$HOME/rpmbuild/RPMS/noarch/$(name)-$(version)-*.rpm rpm
	cp $$HOME/rpmbuild/SRPMS/$(name)-$(version)-*.rpm rpm
