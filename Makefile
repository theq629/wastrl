PYTHON:=python3.6
PIP:=pip3
VIRTUALENV:=virtualenv3

all: run

setup:
	VIRTUALENV=$(VIRTUALENV) PIP=$(PIP) ./setup.sh

run:
	$(PYTHON) -m wastrl.client

.DUMMY: run setup
