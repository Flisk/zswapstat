.PHONY: all
all:
	nfpm pkg --packager deb --target .
