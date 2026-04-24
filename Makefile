# Makefile for FTL Quantum Project

.PHONY: setup ex00 ex01 ex02 clean

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install qiskit qiskit-aer matplotlib pylatexenc
	mkdir -p results

ex00:
	mkdir -p results
	$(PYTHON) ex00/superposition.py

ex01:
	mkdir -p results
	$(PYTHON) ex01/entanglement.py

ex02:
	mkdir -p results
	$(PYTHON) ex02/quantum_noise.py

clean:
	rm -rf results/*