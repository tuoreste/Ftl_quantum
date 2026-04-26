# Makefile for FTL Quantum Project

.PHONY: setup ex00 ex01 ex02 ex03 ex04 clean

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install qiskit qiskit-aer matplotlib pylatexenc
	$(PIP) install qiskit qiskit-aer qiskit-ibm-runtime matplotlib pylatexenc
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

ex03:
	mkdir -p results
	$(PYTHON) ex03/deutsch_jozsa.py

ex04:
	mkdir -p results
	$(PYTHON) ex04/search_algorithm.py

clean:
	rm -rf results/*
