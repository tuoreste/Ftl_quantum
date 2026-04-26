
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import os

os.makedirs("results", exist_ok=True)

# ─── Oracle definitions ───────────────────────────────────────────────────────

def oracle_constant(circuit, input_qubits, ancilla_qubit):
    """
    Constant oracle: f(x) = 0 for all inputs.
    Does nothing — the input qubits are completely unaffected.
    After the final H gates, all input qubits return to |0⟩ → measures 000.
    """
    pass


def oracle_balanced(circuit, input_qubits, ancilla_qubit):
    """
    Balanced oracle: CNOT from each input qubit to the ancilla.
    The ancilla gets flipped for exactly half of all possible input states.
    Phase kickback transfers this information to the input qubit phases.
    After the final H gates, the input qubits cannot all be |0⟩ → non-zero result.
    """
    circuit.cx(input_qubits[0], ancilla_qubit[0])
    circuit.cx(input_qubits[1], ancilla_qubit[0])
    circuit.cx(input_qubits[2], ancilla_qubit[0])


# ─── Algorithm ────────────────────────────────────────────────────────────────

def deutsch_jozsa(oracle_fn, oracle_name="unknown"):
    """
    Builds and returns the full Deutsch-Jozsa circuit for a given oracle.
    Works for any oracle that follows the (circuit, input_qubits, ancilla) signature.
    """
    input_qubits  = QuantumRegister(3, name='input')
    ancilla_qubit = QuantumRegister(1, name='ancilla')
    cr            = ClassicalRegister(3, name='result')
    circuit       = QuantumCircuit(input_qubits, ancilla_qubit, cr)

    # ── Step 1: Initialization ────────────────────────────────────────────────
    # Ancilla: |0⟩ → X → |1⟩ → H → (1/√2)(|0⟩ - |1⟩)
    # This state is required for phase kickback to work
    circuit.x(ancilla_qubit[0])
    circuit.h(ancilla_qubit[0])

    # Input qubits: all |0⟩ → H → equal superposition of all 8 states
    # The oracle will evaluate all 8 inputs simultaneously
    circuit.h(input_qubits[0])
    circuit.h(input_qubits[1])
    circuit.h(input_qubits[2])

    circuit.barrier()

    # ── Step 2: Oracle ────────────────────────────────────────────────────────
    # The oracle marks its answer in the phases of the input qubits
    # We never look inside the oracle — we just plug it in and run
    oracle_fn(circuit, input_qubits, ancilla_qubit)

    circuit.barrier()

    # ── Step 3: Final Hadamard on input qubits ────────────────────────────────
    # Converts phase information back into amplitude (measurable) information
    # Constant oracle  → phases all equal     → amplitudes add up at |000⟩
    # Balanced oracle  → phases cancel at 000 → amplitudes appear elsewhere
    circuit.h(input_qubits[0])
    circuit.h(input_qubits[1])
    circuit.h(input_qubits[2])

    circuit.barrier()

    # ── Step 4: Measure input qubits only ────────────────────────────────────
    # Ancilla is not measured — it served its purpose during the oracle phase
    circuit.measure(input_qubits[0], cr[0])
    circuit.measure(input_qubits[1], cr[1])
    circuit.measure(input_qubits[2], cr[2])

    return circuit


# ─── Run and interpret ────────────────────────────────────────────────────────

def run_and_interpret(circuit, label):
    simulator = AerSimulator()
    compiled  = transpile(circuit, simulator)
    counts    = simulator.run(compiled, shots=500).result().get_counts()

    print(f"\n{'='*40}")
    print(f"Oracle: {label}")
    print(f"Raw counts: {counts}")

    # All results should be identical in a noise-free simulator
    # (one outcome with 500 counts)
    # Check if every result string is all zeros
    is_constant = all(bit == '0' for result_str in counts for bit in result_str)

    if is_constant:
        print(f"Verdict: CONSTANT (all measurements are 000)")
    else:
        print(f"Verdict: BALANCED (non-zero measurement detected)")

    return counts


# ─── Main ─────────────────────────────────────────────────────────────────────

# Build circuits for both oracle types
circuit_constant = deutsch_jozsa(oracle_constant, "Constant")
circuit_balanced = deutsch_jozsa(oracle_balanced, "Balanced")

# Display circuits
print("=== CONSTANT ORACLE CIRCUIT ===")
print(circuit_constant)
circuit_constant.draw('mpl')
plt.title("DJ - Constant Oracle")
plt.savefig("results/ex03_circuit_constant.png")
plt.show()

print("\n=== BALANCED ORACLE CIRCUIT ===")
print(circuit_balanced)
circuit_balanced.draw('mpl')
plt.title("DJ - Balanced Oracle")
plt.savefig("results/ex03_circuit_balanced.png")
plt.show()

# Run both
counts_constant = run_and_interpret(circuit_constant, "Constant")
counts_balanced = run_and_interpret(circuit_balanced, "Balanced")

# Side-by-side histogram
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
plot_histogram(counts_constant, ax=axes[0], title="Constant Oracle")
plot_histogram(counts_balanced, ax=axes[1], title="Balanced Oracle")
plt.suptitle("Exercise 03 - Deutsch-Jozsa Results", fontsize=14)
plt.tight_layout()
plt.savefig("results/ex03_histogram.png")
plt.show()