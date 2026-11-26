.PHONY: default
default: help

.PHONY: help
help:
	@echo "make help         - show this help"
	@echo "make lint         - run all linting (ruff check, ruff format --check, pyright)"
	@echo "make format       - run ruff import sorting and formatting"
	@echo "make lint-ruff    - run ruff linting and format check"
	@echo "make lint-pyright - run pyright type checking"
	@echo "make test         - run all tests"
	@echo "make test-v       - run all tests with verbose output"
	@echo "make test-vv      - run all tests with very verbose output"
	@echo "make coverage     - run tests with coverage report"
	@echo "make docs         - build the Sphinx HTML documentation"

.PHONY: lint
lint: lint-ruff lint-pyright

.PHONY: format
format:
	uv run ruff check --fix .
	uv run ruff format .

.PHONY: lint-ruff
lint-ruff:
	uv run ruff check .
	uv run ruff format --check .

.PHONY: lint-pyright
lint-pyright:
	uv run pyright

.PHONY: test
test:
	uv run pytest

.PHONY: test-v
test-v:
	uv run pytest -v

.PHONY: test-vv
test-vv:
	uv run pytest -vv

.PHONY: coverage
coverage:
	uv run pytest --cov=altamisa --cov=tests --cov-report=term-missing --cov-report=html

.PHONY: docs
docs:
	uv run $(MAKE) -C docs html
