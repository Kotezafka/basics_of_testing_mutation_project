PYTHON ?= /usr/bin/python3
VENV ?= .venv
VENV_PYTHON ?= $(shell pwd)/$(VENV)/bin/python
VENV_PIP ?= $(VENV_PYTHON) -m pip

.PHONY: venv install test mutate mutate_fast htmlcov results clean

venv:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip

install: venv
	$(VENV_PIP) install -r requirements.txt

test: install
	$(VENV_PYTHON) -m pytest -q

mutate: install
	PYTHONPATH=. MUTMUT_RUNNER="$(VENV_PYTHON) -m pytest" $(VENV_PYTHON) -m mutmut run --paths-to-mutate billing --runner "$(VENV_PYTHON) -m pytest" || true

mutate_fast: install
	PYTHONPATH=. MUTMUT_RUNNER="$(VENV_PYTHON) -m pytest" $(VENV_PYTHON) -m mutmut run --paths-to-mutate $$(git diff --name-only $(shell git merge-base main HEAD) | grep -E '^billing/' | tr '\n' ' ') --runner "$(VENV_PYTHON) -m pytest" || true

htmlcov: install
	$(VENV_PYTHON) -m pytest --cov=billing --cov-report=html

results: install
	$(VENV_PYTHON) -m mutmut results

clean:
	rm -rf .mutmut_cache htmlcov .coverage $(VENV)