

# ─── Imports ──────────────────────────────────────────────────────────────────
import math
import os

from qiskit import QuantumCircuit, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

os.makedirs("results", exist_ok=True)


# ─── Oracle ───────────────────────────────────────────────────────────────────

def make_oracle(n_qubits, target_state):
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
    qc = QuantumCircuit(n_qubits)

    # Step 1: map target → |11...1⟩
    # reversed() because Qiskit qubit 0 = rightmost bit of the string
    for i, bit in enumerate(reversed(target_state)):
        if bit == '0':
            qc.x(i)

    # Step 2: multi-controlled Z via H + mcx + H
    # H transforms |1⟩ → (|0⟩-|1⟩)/√2 so that mcx acts as a phase flip
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    qc.h(n_qubits - 1)

    # Step 3: uncompute — restore qubits we flipped in step 1
    for i, bit in enumerate(reversed(target_state)):
        if bit == '0':
            qc.x(i)

    gate = qc.to_gate()
    gate.name = f"Oracle\n({target_state})"
    return gate


# ─── Diffuser ─────────────────────────────────────────────────────────────────

def make_diffuser(n_qubits):
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
    qc = QuantumCircuit(n_qubits)

    # Transform to computational basis where |00...0⟩ is the "mirror"
    for q in range(n_qubits):
        qc.h(q)
    for q in range(n_qubits):
        qc.x(q)

    # Phase flip on |00...0⟩ only
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    qc.h(n_qubits - 1)

    # Undo the basis transformation
    for q in range(n_qubits):
        qc.x(q)
    for q in range(n_qubits):
        qc.h(q)

    gate = qc.to_gate()
    gate.name = "Diffuser"
    return gate


# ─── Grover's Algorithm ───────────────────────────────────────────────────────

def grover(n_qubits, target_state):
    """
    Builds the full Grover search circuit.

    Parameters:
      n_qubits     : int, number of qubits (>= 2)
      target_state : str, binary string of length n_qubits
                     e.g. '111' to search for state 7 in 3-qubit space

    Returns:
      The complete QuantumCircuit ready to run.
    """
    assert n_qubits >= 2, \
        "Need at least 2 qubits"
    assert len(target_state) == n_qubits, \
        f"target_state '{target_state}' must have exactly {n_qubits} bits"
    assert all(b in '01' for b in target_state), \
        "target_state must contain only '0' and '1'"

    N            = 2 ** n_qubits
    n_iterations = max(1, math.floor(math.pi / 4 * math.sqrt(N)))

    print(f"\nGrover search:")
    print(f"  Qubits     : {n_qubits}")
    print(f"  N states   : {N}")
    print(f"  Target     : |{target_state}⟩  (decimal {int(target_state, 2)})")
    print(f"  Iterations : {n_iterations}  (optimal ≈ π/4 × √{N} = {math.pi/4*math.sqrt(N):.2f})")

    cr = ClassicalRegister(n_qubits, name='result')
    qc = QuantumCircuit(n_qubits)
    qc.add_register(cr)

    # ── 1. Initialization: equal superposition ────────────────────────────────
    for q in range(n_qubits):
        qc.h(q)
    qc.barrier()

    # ── 2+3. Grover iterations: oracle then diffuser ──────────────────────────
    oracle   = make_oracle(n_qubits, target_state)
    diffuser = make_diffuser(n_qubits)

    for iteration in range(n_iterations):
        # Oracle marks the target (phase flip)
        qc.append(oracle, list(range(n_qubits)))
        qc.barrier()

        # Diffuser amplifies the marked state
        qc.append(diffuser, list(range(n_qubits)))
        qc.barrier()

    # ── 4. Measure all qubits ────────────────────────────────────────────────
    for q in range(n_qubits):
        qc.measure(q, cr[q])

    return qc, n_iterations


# ─── Run helper ───────────────────────────────────────────────────────────────

def run_grover(n_qubits, target_state, shots=1000):
    """
    Builds, runs, and interprets a Grover search.
    """
    circuit, n_iter = grover(n_qubits, target_state)

    # Display circuit
    print("\nCircuit:")
    print(circuit)
    circuit.draw('mpl')
    plt.title(f"Grover Search — target={target_state}, {n_iter} iteration(s)")
    plt.savefig(f"results/ex04_circuit_{target_state}.png")
    plt.show()

    # Run on simulator
    simulator = AerSimulator()
    compiled  = transpile(circuit, simulator)
    counts    = simulator.run(compiled, shots=shots).result().get_counts()

    print(f"\nResults ({shots} shots):")
    print(f"  Raw counts : {counts}")

    # Find most likely result
    top_result = max(counts, key=counts.get)
    top_prob   = counts[top_result] / shots * 100
    print(f"  Top result : |{top_result}⟩  ({top_prob:.1f}% of shots)")
    print(f"  Target was : |{target_state}⟩")

    if top_result == target_state:
        print(f"  Verdict    : FOUND ✓")
    else:
        print(f"  Verdict    : check iteration count or oracle")

    # Histogram
    plot_histogram(counts)
    plt.title(f"Grover — target |{target_state}⟩, {n_iter} iteration(s)")
    plt.savefig(f"results/ex04_histogram_{target_state}.png")
    plt.show()

    return counts


# ─── Main: test with multiple cases ──────────────────────────────────────────

if __name__ == "__main__":

    # ── Test 1: 3 qubits, target = '111' (matches the subject's example) ─────
    run_grover(n_qubits=3, target_state='111')

    # ── Test 2: 3 qubits, different target ───────────────────────────────────
    run_grover(n_qubits=3, target_state='101')

    # ── Test 3: 2 qubits (minimum) ───────────────────────────────────────────
    run_grover(n_qubits=2, target_state='10')

    # ── Test 4: 4 qubits ─────────────────────────────────────────────────────
    run_grover(n_qubits=4, target_state='1010')