"""

The Big Picture
Goal: find a marked item among N = 2^n items
Classical: check items one by one → O(N) steps
Quantum:   amplify the right answer → O(√N) steps

Three parts: Initialization → Oracle → Diffuser
Repeat Oracle + Diffuser √N times then measure

Part 1: Initialization
Start: all qubits in |0⟩
Apply H to every qubit
Result: equal superposition of all N states
Every state has the same amplitude: 1/√N
Nobody is special yet — the target looks identical to everyone else

Part 2: The Oracle
The oracle knows which state is the target
It does not move it or reveal it
It simply flips the target's amplitude from positive to negative
  → target gets phase -1
  → everyone else stays +1
The target is now "marked" but still invisible to measurement
  (squaring a negative still gives positive probability)

Part 3: The Diffuser
The diffuser reflects all amplitudes around their average
Before reflection:
  → target amplitude is negative (below average)
  → everyone else is positive (above average)
After reflection:
  → target gets pushed far above average (large positive amplitude)
  → everyone else gets pushed slightly below average
One oracle + one diffuser = one Grover iteration
The target's amplitude grows a little each iteration

How Many Iterations
Too few iterations → target amplitude not yet large enough
Too many iterations → overshoots, amplitude drops again
Optimal number → floor(π/4 × √N)

n=2 qubits → N=4  → 1 iteration
n=3 qubits → N=8  → 2 iterations
n=4 qubits → N=16 → 3 iterations

The Diffuser Circuit Step by Step
Step 1: H on all qubits     → change basis
Step 2: X on all qubits     → flip so |00...0⟩ becomes the target
Step 3: multi-controlled Z  → flip phase of |00...0⟩ only
Step 4: X on all qubits     → unflip (undo step 2)
Step 5: H on all qubits     → change basis back

Net effect: reflect all amplitudes around their mean

The Oracle Circuit Step by Step
Step 1: X on qubits where target bit = 0
        → maps target pattern to |11...1⟩
Step 2: multi-controlled Z
        → flips phase only when all qubits are 1
        → only the target state satisfies this
Step 3: X on same qubits again
        → uncompute step 1, restore original state

Net effect: target gets phase -1, everyone else unchanged

Measurement
After √N iterations:
  target amplitude ≈ 1.0
  all other amplitudes ≈ 0.0

Measure all qubits
→ target state appears with high probability (~95% for n=3)
→ run 1000 shots to confirm the dominant result
→ the most frequent result is your answer

Why Faster Than Classical
Classical search:
  check item 1 → not it
  check item 2 → not it
  check item 3 → found it  ← could be anywhere, average N/2 checks

Quantum search:
  all items exist simultaneously in superposition
  oracle marks the target via phase in one query
  diffuser amplifies the target's amplitude
  repeat √N times → measure → done

For N=1,000,000:
  Classical → 500,000 checks on average
  Quantum   → ~785 iterations

"""

import math
import os

from qiskit import QuantumCircuit, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

os.makedirs("results", exist_ok=True)

"""
Marks the target state by flipping its phase from +1 to -1.

Method:
    1. X gates on qubits where target bit = '0'
        (converts target pattern → all-ones pattern |11...1⟩)
    2. Multi-controlled Z (only fires on |11...1⟩)
    3. X gates again to uncompute step 1

This way ONLY the target state gets its phase flipped.
All other states are completely unaffected.
"""
def make_oracle(n, target):
    qc = QuantumCircuit(n)

    for i, bit in enumerate(reversed(target)):
        if bit == "0":
            qc.x(i)

    qc.h(n - 1)
    qc.mcx(range(n - 1), n - 1)
    qc.h(n - 1)

    for i, bit in enumerate(reversed(target)):
        if bit == "0":
            qc.x(i)

    oracle = qc.to_gate()
    oracle.name = f"Oracle\n({target})"

    return oracle


"""
Grover diffusion operator.
Reflects all amplitudes around their current average.

Effect:
    - Amplitudes above average get pushed higher
    - Amplitudes below average (the marked state, which is negative)
    get pushed far above average

Implementation (standard):
    H on all → X on all → multi-controlled Z → X on all → H on all
"""
def make_diffuser(n):
    qc = QuantumCircuit(n)

    qc.h(range(n))
    qc.x(range(n))

    qc.h(n - 1)
    qc.mcx(range(n - 1), n - 1)
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

Returns:
    The complete QuantumCircuit ready to run.
"""
def grover(n, target):
    iterations = max(1, math.floor(math.pi / 4 * math.sqrt(2**n)))

    cr = ClassicalRegister(n, "result")
    qc = QuantumCircuit(n, cr)

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