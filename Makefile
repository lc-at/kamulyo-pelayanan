PYTHON=python

.PHONY: setup compile-req install-req

setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install pip-tools

compile-req:
	pip-compile --output-file=requirements.txt requirements.in

install-req:
	$(PYTHON) -m pip install -r requirements.txt
