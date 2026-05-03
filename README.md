# README.md — Ftl_quantum

## What is this project?

An introduction to quantum programming using Python and Qiskit.
Each exercise builds on the previous one, starting from a single qubit
all the way to a quantum search algorithm.

---

## Requirements
Note: For less headache with installations, one may refer to the Makefile in root folder

```bash
pip install qiskit qiskit-aer qiskit-ibm-runtime matplotlib pylatexenc
```
---

## Exercises

### ex00 — Superposition
**Concept:** A single qubit can exist in two states simultaneously until measured.

**What it does:**
- Creates a 1-qubit circuit
- Applies a Hadamard gate to produce `(1/√2)(|0⟩ + |1⟩)`
- Runs 500 shots on a local simulator
- Displays a histogram showing ~50% chance of 0 and ~50% chance of 1

**Key idea:** The Hadamard gate puts the qubit into equal superposition.
Measurement collapses it to either 0 or 1 randomly.

```bash
python ex00_superposition.py
```

---

### ex01 — Entanglement
**Concept:** Two qubits can be linked so that measuring one instantly
determines the other no matter how far apart they are.

**What it does:**
- Creates a 2-qubit circuit
- Applies Hadamard then CNOT to produce `(1/√2)(|00⟩ + |11⟩)`
- Runs 500 shots on a local simulator
- Histogram shows only 00 and 11 — never 01 or 10

**Key idea:** H on the control qubit creates superposition.
CNOT entangles the two qubits. The result is a Bell state.

```bash
python ex01_entanglement.py
```

---

### ex02 — Quantum Noise
**Concept:** Real quantum hardware is imperfect. Physical qubits
are fragile and introduce errors that a simulator never has.

**What it does:**
- Runs the identical Bell state circuit from ex01
- Sends it to a real IBM quantum computer instead of the simulator
- Compares results side by side
- Shows the noise floor: small percentages of 01 and 10 appearing

**Four sources of noise:**

Gate errors    → imperfect microwave pulses rotate qubits by wrong angles
Decoherence    → qubits lose their state over time (T1 and T2 times)
Readout errors → measurement hardware misreads qubit values
Crosstalk      → neighboring qubits interfere with each other

**Key idea:** The circuit is correct. The noise is physical, not mathematical.
The simulator confirms this — it produces zero 01 and 10 results.

```bash
python ex02_noise_real_backend.py
```

**Note:** Requires an IBM Quantum account. Save your token once:
```bash
python -c "
from qiskit_ibm_runtime import QiskitRuntimeService
QiskitRuntimeService.save_account(channel='ibm_quantum_platform', token='YOUR_TOKEN')
"
```
Never put your token in the source code or commit it to Git.

---

### ex03 — Deutsch-Jozsa Algorithm
**Concept:** Determine whether a black-box function is constant
(same output for all inputs) or balanced (half 0, half 1)
using a single quantum query instead of many classical ones.

**What it does:**
- Implements the Deutsch-Jozsa algorithm with 3 input qubits + 1 ancilla
- Tests a constant oracle and a balanced oracle
- Measures only the input qubits
- Displays results for both oracles side by side

**Circuit structure:**

ancilla:  X → H → Oracle → (not measured)
inputs:   H → Oracle → H → Measure

**Reading results:**

000           → oracle is CONSTANT
anything else → oracle is BALANCED

**Key idea:** Phase kickback via the ancilla in |-⟩ encodes the oracle
type into qubit phases. Final H gates convert phases into amplitudes
via interference. One query gives a certain answer.

**Classical cost:** 2^(n-1) + 1 = 5 queries for n=3
**Quantum cost:** 1 query always

```bash
python ex03_deutsch_jozsa.py
```

---

### ex04 — Grover's Search Algorithm
**Concept:** Find a marked item among N unsorted items faster
than any classical computer can.

**What it does:**
- Implements Grover's algorithm for any number of qubits (minimum 2)
- Searches for a target state encoded in the oracle
- Repeats oracle + diffuser for optimal √N iterations
- Measures all qubits — target appears with high probability

**Three parts:**

Initialization → H on all qubits → equal superposition of all N states
Oracle         → flips phase of target from +1 to -1 (marks it)
Diffuser       → reflects all amplitudes around their average
target flies above average, wrong states sink to zero

**Optimal iterations:**

n=2 qubits (N=4)  → 1 iteration  → ~100% probability
n=3 qubits (N=8)  → 2 iterations → ~97%  probability
n=4 qubits (N=16) → 3 iterations → ~96%  probability
formula: floor(π/4 × √N)

**Classical cost:** O(N) — check items one by one
**Quantum cost:** O(√N) — amplitude amplification

```bash
python ex04_grover_search.py
```

---

### bonus — Bernstein-Vazirani Algorithm
**Concept:** Find a secret bit string hidden inside an oracle
using a single quantum query instead of n classical queries.

**What it does:**
- Implements Bernstein-Vazirani for any length secret string
- Oracle computes f(x) = x · s (mod 2) where s is the secret
- Single query reveals the entire secret string directly
- Measurement result IS the secret

**Circuit structure:**

ancilla: X → H → Oracle → (not measured)
inputs:  H → Oracle → H → Measure

**Key idea:** CNOT gates wired wherever secret bit = 1.
Phase kickback writes secret into qubit phases.
Final H gates decode phases into bit values.
Measurement reads the secret directly.

**Classical cost:** O(n) — one query per bit
**Quantum cost:** O(1) — one query always, regardless of length

```bash
python ex_bonus_bernstein_vazirani.py
```

---

## Project Structure

Ftl_quantum/
│
├── ex00/
    superposition.py
├── ex01/
    entanglement.py
├── ex02/
    noise_real_backend.py
├── ex03/
    deutsch_jozsa.py
├── ex04/
    grover_search.py
├── bonus/
    bernstein_vazirani.py
└── results/

---

## Core Concepts Learned

Qubit          → quantum bit, exists in superposition until measured
Amplitude      → complex number describing how much of each state exists
Probability    → amplitude squared, always sums to 1
Superposition  → qubit exists as combination of 0 and 1 simultaneously
Entanglement   → qubits linked so measuring one determines the other
Interference   → amplitudes add or cancel like waves
Phase kickback → oracle answer transferred into input qubit phases
Measurement    → collapses superposition to a definite classical value

---

## Gates Used

X gate → flips |0⟩ to |1⟩ and vice versa (quantum NOT)
H gate → creates equal superposition from |0⟩ or |1⟩
CNOT   → flips target qubit if control qubit is |1⟩
MCX    → flips target if ALL control qubits are |1⟩

---

## Credentials

create a token or API keys from available quantum computers e.g IBM
Store them locally using QiskitRuntimeService.save_account().(Notice: make sure you will not push the credential)
Add it into *.json and .env to your .gitignore.

---
