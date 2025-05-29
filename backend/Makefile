.PHONY: setup test run clean deploy

# Variables
PYTHON = python
VENV = venv
PIP = $(VENV)/bin/pip
FLASK = $(VENV)/bin/flask
PYTEST = $(VENV)/bin/pytest
GUNICORN = $(VENV)/bin/gunicorn

setup:
	$(PYTHON) deploy.py --setup

test:
	$(PYTEST) -v --cov=app tests/

run:
	$(FLASK) run --host=0.0.0.0 --port=5000

run-prod:
	$(GUNICORN) -c gunicorn.conf.py run:app

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -f *.pyc
	rm -f *.pyo
	rm -f *.pyd

install:
	$(PIP) install -r requirements.txt

update:
	$(PIP) install --upgrade -r requirements.txt

deploy: clean setup
	$(MAKE) run-prod