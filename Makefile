# -*- coding: us-ascii-unix -*-

name       = harbour-helsinki-transit-live
version    = 1.0.1
DESTDIR    =
PREFIX     = /usr
datadir    = $(DESTDIR)$(PREFIX)/share/$(name)
desktopdir = $(DESTDIR)$(PREFIX)/share/applications
icondir    = $(DESTDIR)$(PREFIX)/share/icons/hicolor/86x86/apps

.PHONY: clean dist install rpm

clean:
	rm -rf dist
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -f rpm/*.rpm

dist:
	$(MAKE) clean
	mkdir -p dist/$(name)-$(version)
	cp -r `cat MANIFEST` dist/$(name)-$(version)
	tar -C dist -cJf dist/$(name)-$(version).tar.xz $(name)-$(version)

install:
	@echo "Installing Python files..."
	mkdir -p $(datadir)/htl
	cp htl/*.py $(datadir)/htl
	@echo "Installing QML files..."
	mkdir -p $(datadir)/qml/icons
	cp qml/helsinki-transit-live.qml $(datadir)/qml/$(name).qml
	cp qml/[ABCDEFGHIJKLMNOPQRSTUVXYZ]*.qml $(datadir)/qml
	cp qml/icons/*.png $(datadir)/qml/icons
	@echo "Installing desktop file..."
	mkdir -p $(desktopdir)
	cp data/$(name).desktop $(desktopdir)
	@echo "Installing icon..."
	mkdir -p $(icondir)
	cp data/helsinki-transit-live.png $(icondir)/$(name).png

rpm:
	mkdir -p $$HOME/rpmbuild/SOURCES
	cp dist/$(name)-$(version).tar.xz $$HOME/rpmbuild/SOURCES
	rm -rf $$HOME/rpmbuild/BUILD/$(name)-$(version)
	rpmbuild -ba rpm/$(name).spec
	cp $$HOME/rpmbuild/RPMS/noarch/$(name)-$(version)-*.rpm rpm
	cp $$HOME/rpmbuild/SRPMS/$(name)-$(version)-*.rpm rpm
