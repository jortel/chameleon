PKG = chameleon
SPEC = $(PKG).spec
SETUP = setup.py
FEDORAPEOPLE = jortel@fedorapeople.org

all : rpm

egg : clean
	python $(SETUP) bdist_egg
	rm -rf *.egg-info

dist : clean
	mkdir -p dist
	./sdist

rpm : dist
	cp dist/$(PKG)*.gz /usr/src/redhat/SOURCES
	rpmbuild -ba $(SPEC)
	cp /usr/src/redhat/RPMS/noarch/$(PKG)*.rpm dist
	cp /usr/src/redhat/SRPMS/$(PKG)*.rpm dist
	rpmlint -i dist/$(PKG)*.rpm

release : rpm
	scp dist/$(PKG)*.tar.gz $(FEDORAPEOPLE):
	scp dist/$(PKG)*.rpm $(FEDORAPEOPLE):

clean : 
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -rf /usr/src/redhat/BUILD/$(PKG)*
	rm -rf /usr/src/redhat/RPMS/noarch/$(PKG)*
	rm -rf /usr/src/redhat/SOURCES/$(PKG)*
	rm -rf /usr/src/redhat/SRPMS/$(PKG)*
	find . -name "*.pyc" -exec rm -f {} \;
	find . -name "*~" -exec rm -f {} \;
	find . -name "lextab.*" -exec rm -f {} \;
	find . -name "parsetab.*" -exec rm -f {} \;
	find . -name "*.out" -exec rm -f {} \;

.PHONY : clean 
