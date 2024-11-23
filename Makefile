.PHONY: clean clean-build clean-pyc clean-test coverage lint test run build
.DEFAULT_GOAL := build

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -rf .mypy_cache

lint:
	flake8 optimus tests setup.py
	isort -c optimus tests setup.py
	black optimus --line-length 120 --check
	mypy --ignore-missing-imports --show-error-codes optimus tests

test: lint
	python -m unittest -v

coverage:
	coverage run --source optimus -m unittest
	coverage report -m

build:
	pip install .

run:
	./boot.sh -r
