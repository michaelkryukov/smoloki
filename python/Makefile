.PHONY: all

all: format lint test

format:
	python3 -m black --line-length=127 .

lint:
	python3 -m black --line-length=127 . --check
	python3 -m flake8 . --inline-quotes '"' --max-complexity=10 --max-line-length=127

test:
	python3 -m pytest tests/
