.PHONY: clean clean-test clean-pyc clean-build clean-venv check-venv help
.DEFAULT_GOAL := help

SHELL := /bin/bash
export VIRTUALENVWRAPPER_PYTHON := /usr/bin/python

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

check-venv: ## verify that the user is running in a Python virtual environment
	@if [ -z "$(VIRTUALENVWRAPPER_SCRIPT)" ]; then echo 'Python virtualenvwrapper not installed!' && exit 1; fi
	@if [ -z "$(VIRTUAL_ENV)" ]; then echo 'Not running within a virtual environment!' && exit 1; fi

clean: clean-test clean-pyc clean-build   ## remove all build, test, coverage, artifacts and wipe virtualenv

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache/

clean-venv: check-venv ## remove all packages from current virtual environment
	@pip uninstall -y swagger-client || echo "Skipping uninstall of swagger-client"
	@pip uninstall -y pytest-rpc || echo "Skipping uninstall of pytest-rpc"
	@source virtualenvwrapper.sh && wipeenv || echo "Skipping wipe of environment"

lint: ## check style with flake8
	flake8 zigzag tests

test: ## run tests quickly with the default Python
	py.test

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source zigzag -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

release: clean ## package and upload a release
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

develop: clean ## install necessary packages to setup a dev environment
	pip install -r requirements_dev.txt
