.PHONY: default
default: help

.PHONY: help
help:
	@echo "make help         - show this help"
	@echo "make lint         - run all linting"
	@echo "make format       - run all formatting"
	@echo "make lint-isort   - run isort linting"
	@echo "make format-isort - run isort formatting"
	@echo "make lint-black   - run black linting"
	@echo "make format-black - run black formatting"
	@echo "make lint-flake8  - run flake8 linting"
	@echo "make lint-pyright - run pyright linting"
	@echo "make test         - run all tests"
	@echo "make test-v       - run all tests with verbose output"
	@echo "make test-vv      - run all tests with very verbose output"

.PHONY: lint
lint: lint-isort lint-black lint-flake8 lint-pyright

.PHONY: format
format: format-isort format-black

.PHONY: lint-isort
lint-isort:
	isort --check-only --diff --force-sort-within-sections --profile=black .

.PHONY: format-isort
format-isort:
	isort --force-sort-within-sections --profile=black .

.PHONY: lint-black
lint-black:
	black -l 100 --check .

.PHONY: format-black
format-black:
	black -l 100 .

.PHONY: lint-flake8
lint-flake8:
	flake8 .

.PHONY: lint-pyright
lint-pyright:
	pyright

.PHONY: test
test:
	pytest

.PHONY: test-v
test-v:
	pytest -v

.PHONY: test-vv
test-vv:
	pytest -vv
