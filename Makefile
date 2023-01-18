.PHONY: all

all: format lint test

format:
	python3 -m black .

lint:
	python3 -m black . --check
	python3 -m flake8 . --inline-quotes '"' --max-complexity=10 --max-line-length=127

test:
	python3 -m pytest tests/
