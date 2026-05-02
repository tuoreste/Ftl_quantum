"""
The algorithm needs only one query because quantum superposition allows all 2³ = 8 inputs to be processed simultaneously in a single oracle call.

step by step:
First, H gates are applied to all three input qubits, creating an equal superposition of all 8 possible inputs at once.
The ancilla is prepared in |-⟩ by applying X then H.

Second, the oracle is called once. Because the input register contains all 8 states simultaneously,
the oracle effectively evaluates f(x) for all 8 inputs in a single query.
Phase kickback transfers the oracle's answer into the phases of the input register — f(x)=0 leaves the phase as +1, f(x)=1 flips the phase to -1.
The ancilla |-⟩ enables this kickback and remains unchanged.
After the oracle the two cases look like this:
Constant: all 8 terms have identical phases
Balanced: exactly 4 terms have +1, exactly 4 have -1

Third, H gates are applied to all input qubits again.
These convert phase differences into measurable amplitudes through interference:
Constant → all phases identical → constructive interference at |000⟩
           → measures 000 with 100% certainty

Balanced → phases mixed +1 and -1 → destructive interference at |000⟩
           → |000⟩ amplitude cancels to zero → measures anything except 000

A classical computer cannot do this because it can only query the oracle with one input at a time.
It has no superposition. It has no phase. It cannot process all inputs simultaneously. 
It needs at least 2^(n-1)+1 = 5 queries to be certain. The quantum computer needs exactly 1."

The three things your answer had that are essential:
✓ Superposition processes all inputs simultaneously
✓ Phase kickback transfers oracle answer into phases
✓ 000 = constant, anything else = balanced
The two important things:
+ The interference mechanism (constructive vs destructive)
+ The classical comparison with exact numbers

Concept 8: The Two Oracle Implementations Now let's look at the actual circuits.

Constant Oracle — f(x)=0 for all inputs:
Do nothing. Literally an empty circuit.
No gates at all on the input qubits.
All phases stay +1 → measures 000.
Constant Oracle — f(x)=1 for all inputs:
Apply X to ancilla only.
Every input gets phase -1 → global phase → still measures 000.
Balanced Oracle — CNOT from each input qubit to ancilla:
input q0 ──●──
           │
input q1 ──●──
           │
input q2 ──●──
           │
ancilla  ──⊕──
Each input qubit controls a flip of the ancilla.
Through phase kickback, each input qubit picks up a phase of -1 when it is |1⟩.
This produces exactly the mixed +1/-1 pattern of a balanced function.

"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import os

os.makedirs("results", exist_ok=True)

"""
Constant oracle: f(x) = 0 for all inputs.
Does nothing — no gates at all. All input qubits return to |0⟩ → measures 000.
"""
def oracle_constant(circuit, input_qubits, ancilla_qubit):
    pass

"""
Balanced oracle: CNOT from each input qubit to the ancilla.
The ancilla gets flipped for exactly half of all possible input states.
Phase kickback transfers this information to the input qubit phases.
After the final H gates, the input qubits cannot all be |0⟩ → non-zero result.

|000⟩ → zero 1s  → even → phase +1
|001⟩ → one 1    → odd  → phase -1
|010⟩ → one 1    → odd  → phase -1
|011⟩ → two 1s   → even → phase +1
|100⟩ → one 1    → odd  → phase -1
|101⟩ → two 1s   → even → phase +1
|110⟩ → two 1s   → even → phase +1
|111⟩ → three 1s → odd  → phase -1
"""
def oracle_balanced(circuit, input_qubits, ancilla_qubit):
    circuit.cx(input_qubits[0], ancilla_qubit[0])
    circuit.cx(input_qubits[1], ancilla_qubit[0])
    circuit.cx(input_qubits[2], ancilla_qubit[0])


"""
Builds and returns the full Deutsch-Jozsa circuit for a given oracle.
Works for any oracle that follows the (circuit, input_qubits, ancilla) signature.
"""
def deutsch_jozsa(oracle_fn, oracle_name="unknown"):
    input_qubits  = QuantumRegister(3, name='input')
    ancilla_qubit = QuantumRegister(1, name='ancilla')
    cr            = ClassicalRegister(3, name='result')
    circuit       = QuantumCircuit(input_qubits, ancilla_qubit, cr)

    circuit.x(ancilla_qubit[0])
    circuit.h(ancilla_qubit[0]) #phase kickback here

    circuit.h(input_qubits[0])
    circuit.h(input_qubits[1])
    circuit.h(input_qubits[2]) #all the inputs superpositioned here

    circuit.barrier()

    oracle_fn(circuit, input_qubits, ancilla_qubit) #marks the phases here(+1, -1)

    circuit.barrier()

    circuit.h(input_qubits[0])
    circuit.h(input_qubits[1])
    circuit.h(input_qubits[2]) #interference reveal |000> if constant and sth else if balanced(they cancel out)

    circuit.barrier()

    circuit.measure(input_qubits[0], cr[0])
    circuit.measure(input_qubits[1], cr[1])
    circuit.measure(input_qubits[2], cr[2]) #only input qubits are measured. ancila was only for phasekickback

    return circuit


def run_and_interpret(circuit, label):
    simulator = AerSimulator()
    compiled  = transpile(circuit, simulator)
    counts    = simulator.run(compiled, shots=500).result().get_counts()

    print(f"\n{'='*40}")
    print(f"Oracle: {label}")
    print(f"Raw counts: {counts}")


    is_constant = all(bit == '0' for result_str in counts for bit in result_str)
    if is_constant:
        print(f"Verdict: CONSTANT (all measurements are 000)")
    else:
        print(f"Verdict: BALANCED (non-zero measurement detected)")
    return counts

circuit_constant = deutsch_jozsa(oracle_constant, "Constant")
circuit_balanced = deutsch_jozsa(oracle_balanced, "Balanced")

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

counts_constant = run_and_interpret(circuit_constant, "Constant")
counts_balanced = run_and_interpret(circuit_balanced, "Balanced")

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
plot_histogram(counts_constant, ax=axes[0], title="Constant Oracle")
plot_histogram(counts_balanced, ax=axes[1], title="Balanced Oracle")
plt.suptitle("Exercise 03 - Deutsch-Jozsa Results", fontsize=14)
plt.tight_layout()
plt.savefig("results/ex03_histogram.png")
plt.show()
