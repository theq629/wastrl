PYTHON:=python3.6
PIP:=pip3
VIRTUALENV:=virtualenv3

all: run

setup:
	VIRTUALENV=$(VIRTUALENV) PIP=$(PIP) ./setup.sh

run:
	$(PYTHON) -m wastrl.client

install:
	pip install .

.DUMMY: run setup

clean:
	rm -rf wastrl.egg-info build dist
	find wastrl -name __pycache__ -exec rm -rf {} \;
	cd distribute && make clean
