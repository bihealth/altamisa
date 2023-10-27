.PHONY: default black flake8 test test-v test-vv

default: black flake8

black:
	black -l 100 --exclude "versioneer.py|_version.py" .

black-check:
	black -l 100 --exclude "versioneer.py|_version.py" --check .

flake8:
	flake8 .

test:
	pytest

test-v:
	pytest -v

test-vv:
	pytest -vv
