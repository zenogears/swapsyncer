all: stamp

stamp:
	touch $(CURDIR)/stamp

clean:
	rm -f $(CURDIR)/stamp

install:
	install -d $(DESTDIR)/usr/sbin
	cp -r $(CURDIR)/usr/share $(DESTDIR)/usr/share
	cp -r $(CURDIR)/usr/sbin/swapsyncer $(DESTDIR)/usr/sbin

uninstall:
	rm $(DESTDIR)/usr/sbin/swapsyncer
	rm -rf $(DESTDIR)/usr/share/swapsyncer