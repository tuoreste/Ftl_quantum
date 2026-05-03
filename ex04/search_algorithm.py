"""

Setup
n = 2 qubits
N = 2² = 4 states: |00⟩, |01⟩, |10⟩, |11⟩
target = |11⟩
optimal iterations = floor(π/4 × √4) = floor(π/4 × 2) = floor(1.57) = 1

Stage 1: Initialization
Start with both qubits in |0⟩:
|ψ₀⟩ = |00⟩
Apply H to qubit 0:
H|0⟩ = (1/√2)(|0⟩ + |1⟩)

|ψ⟩ = (1/√2)(|0⟩ + |1⟩) ⊗ |0⟩
     = (1/√2)(|00⟩ + |10⟩)
Apply H to qubit 1:
H|0⟩ = (1/√2)(|0⟩ + |1⟩)

|ψ₁⟩ = (1/√2)(|0⟩ + |1⟩) ⊗ (1/√2)(|0⟩ + |1⟩)
      = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)
All four states have equal amplitude:
amplitude of each state = 1/2 = 0.5
probability of each state = (1/2)² = 1/4 = 25%

|ψ₁⟩ = 0.5|00⟩ + 0.5|01⟩ + 0.5|10⟩ + 0.5|11⟩
Verify normalization:
(0.5)² + (0.5)² + (0.5)² + (0.5)² = 0.25 + 0.25 + 0.25 + 0.25 = 1 ✓

Stage 2: Oracle
Target is |11⟩. Oracle flips its phase from +0.5 to -0.5:
Before oracle:
  |00⟩  amplitude = +0.5
  |01⟩  amplitude = +0.5
  |10⟩  amplitude = +0.5
  |11⟩  amplitude = +0.5  ← target

After oracle:
  |00⟩  amplitude = +0.5
  |01⟩  amplitude = +0.5
  |10⟩  amplitude = +0.5
  |11⟩  amplitude = -0.5  ← flipped
State after oracle:
|ψ₂⟩ = 0.5|00⟩ + 0.5|01⟩ + 0.5|10⟩ - 0.5|11⟩

Check probabilities — still all equal:
P(|00⟩) = (0.5)²  = 25%
P(|01⟩) = (0.5)²  = 25%
P(|10⟩) = (0.5)²  = 25%
P(|11⟩) = (-0.5)² = 25%  ← negative but probability unchanged
Target is marked but still invisible. We need the diffuser.

Stage 3: Diffuser
Step 3a: Calculate the average amplitude
average = (0.5 + 0.5 + 0.5 + (-0.5)) / 4
        = 1.0 / 4
        = 0.25
Step 3b: Apply reflection formula to each state
new amplitude = 2 × average - old amplitude
For |00⟩:
new = 2 × 0.25 - 0.5 = 0.5 - 0.5 = 0.0
For |01⟩:
new = 2 × 0.25 - 0.5 = 0.5 - 0.5 = 0.0
For |10⟩:
new = 2 × 0.25 - 0.5 = 0.5 - 0.5 = 0.0
For |11⟩ (target):
new = 2 × 0.25 - (-0.5) = 0.5 + 0.5 = 1.0
State after diffuser:
|ψ₃⟩ = 0.0|00⟩ + 0.0|01⟩ + 0.0|10⟩ + 1.0|11⟩
Step 3c: Calculate final probabilities
P(|00⟩) = (0.0)² = 0%
P(|01⟩) = (0.0)² = 0%
P(|10⟩) = (0.0)² = 0%
P(|11⟩) = (1.0)² = 100%  ← target found with certainty
Verify normalization:
0 + 0 + 0 + 1 = 1 ✓

Stage 4: Measurement
Measure both qubits → get |11⟩ with 100% probability
For n=2 qubits with 1 iteration, Grover finds the target with perfect certainty. For larger N the probability is ~96% not 100%, but one iteration is exact for N=4.

Full Summary in One Table
Stage          | |00⟩  | |01⟩  | |10⟩  | |11⟩  | Note
───────────────|--------|--------|--------|--------|──────────────
Start          | 0.000  | 0.000  | 0.000  | 0.000  | all in |00⟩
After H gates  | +0.500 | +0.500 | +0.500 | +0.500 | equal superposition
After oracle   | +0.500 | +0.500 | +0.500 | -0.500 | target flipped
average        |        |        |        | =0.250 |
After diffuser | 0.000  | 0.000  | 0.000  | +1.000 | target amplified
───────────────|--------|--------|--------|--------|──────────────
Probability    |   0%   |   0%   |   0%   |  100%  | found

"""

import math
import os

from qiskit import QuantumCircuit, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

os.makedirs("results", exist_ok=True)

def make_oracle(n, target):
    qc = QuantumCircuit(n)

    for i, bit in enumerate(reversed(target)):
        if bit == "0":
            qc.x(i)

    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)

    for i, bit in enumerate(reversed(target)):
        if bit == "0":
            qc.x(i)

    oracle = qc.to_gate()
    oracle.name = f"Oracle\n({target})"

    return oracle


"""
Reflect all amplitudes around their average
→ pushes the target amplitude higher each iteration

new amplitude = 2 × average - old amplitude

formula on a qc
Phase 1: Change basis     (H + X)
Phase 2: Phase flip       (H + MCX + H)
Phase 3: Change back      (X + H)
"""
def make_diffuser(n):
    qc = QuantumCircuit(n)

    qc.h(range(n))
    qc.x(range(n))

    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)

    qc.x(range(n))
    qc.h(range(n))

    diffuser = qc.to_gate()
    diffuser.name = "Diffuser"

    return diffuser

"""
Builds the full Grover search circuit.

Parameters:
    n_qubits     : int, number of qubits (>= 2)
    target_state : str, binary string of length n_qubits
                    e.g. '111' to search for state 7 in 3-qubit space
"""
def grover(n, target):
    iterations = max(1, math.floor(math.pi / 4 * math.sqrt(2**n)))

    cr = ClassicalRegister(n, "result")
    # qc = QuantumCircuit(n, cr)
    qc = QuantumCircuit(n)
    qc.add_register(cr)

    qc.h(range(n))
    qc.barrier()

    oracle = make_oracle(n, target)
    diffuser = make_diffuser(n)

    for _ in range(iterations):
        qc.append(oracle, range(n))
        qc.append(diffuser, range(n))
        qc.barrier()

    qc.measure(range(n), range(n))

    return qc, iterations

def run_grover(n, target, shots=1000):
    qc, iterations = grover(n, target)

    print(f"\nGrover Search")
    print(f"Target      : |{target}⟩")
    print(f"Qubits      : {n}")
    print(f"Iterations  : {iterations}")

    simulator = AerSimulator()
    counts = simulator.run(
        transpile(qc, simulator),
        shots=shots
    ).result().get_counts()

    top = max(counts, key=counts.get)
    probability = counts[top] / shots * 100

    print(f"Top result  : |{top}⟩ ({probability:.1f}%)")
    print(f"Verdict     : {'FOUND ✓' if top == target else 'FAILED'}")

    qc.draw("mpl")
    plt.title(f"Grover Circuit |{target}⟩")
    plt.savefig(f"results/grover_circuit_{target}.png")
    plt.show()

    plot_histogram(counts)
    plt.title(f"Grover Results |{target}⟩")
    plt.savefig(f"results/grover_histogram_{target}.png")
    plt.show()

    return counts

if __name__ == "__main__":

    tests = [
        (3, "111"),
        (3, "101"),
        (2, "10"),
        (4, "1010"),
    ]

    for n, target in tests:
        run_grover(n, target)