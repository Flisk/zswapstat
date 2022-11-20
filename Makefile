.PHONY: all
all: test deb

.PHONY: test
test:
	python3 -m mypy zswapstat.py

.PHONY: deb
deb:
	nfpm pkg --packager deb --target .
