.PHONY: install test lint clean

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v

lint:
	ruff check src/ tests/

clean:
	rm -rf build/ dist/ *.egg-info src/*.egg-info
