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
    #qr_i = quantum register input
    #qr_a = quantum register ancila
    #cr = classical register->storage
    #qc = quantum circuit
    qr_i = QuantumRegister(3, name='input')
    qr_a = QuantumRegister(1, name='ancilla')
    cr = ClassicalRegister(3, name='result')
    qc = QuantumCircuit(qr_i, qr_a, cr)

    qc.x(qr_a)
    qc.h(qr_a) #phase kickback here
    qc.h(qr_i) #all the inputs superpositioned here

    qc.barrier()
    oracle_fn(qc, qr_i, qr_a) #marks the phases here(+1, -1)

    qc.barrier()
    qc.h(qr_i) #interference reveal |000> if constant and sth else if balanced(they cancel out)
    qc.measure(qr_i, cr) #only input qubits are measured. ancila was only for phasekickback

    return qc


def run_and_interpret(circuit, label):
    simulator = AerSimulator()
    counts    = simulator.run(transpile(circuit, simulator), shots=500).result().get_counts()

    measured = max(counts, key=counts.get)
    answer = 0 if measured == "000" else 1
    verdict = "CONSTANT" if answer == 0 else "BALANCED"

    print(f"\n{'='*40}")
    print(f"Oracle: {label}")
    print(f"Raw counts: {counts}")
    print(f"Verdict: {verdict}")
    print(f"Assignment output bit: {answer}")

    return counts

def save_circuit_diagram(circuit, label):
    print(f"\n=== {label.upper()} ORACLE CIRCUIT ===")
    print(circuit)

    circuit.draw("mpl")
    plt.title(f"DJ - {label} Oracle")
    plt.savefig(f"results/ex03_circuit_{label.lower()}.png")
    plt.show()

oracles = {
    "Constant": oracle_constant,
    "Balanced": oracle_balanced,
}

counts = {}

for label, oracle in oracles.items():
    circuit = deutsch_jozsa(oracle, label)

    save_circuit_diagram(circuit, label)
    counts[label] = run_and_interpret(circuit, label)


fig, axes = plt.subplots(1, 2, figsize=(12, 4))

plot_histogram(counts["Constant"], ax=axes[0], title="Constant Oracle")
plot_histogram(counts["Balanced"], ax=axes[1], title="Balanced Oracle")

plt.suptitle("Exercise 03 - Deutsch-Jozsa Results", fontsize=14)
plt.tight_layout()
plt.savefig("results/ex03_histogram.png")
plt.show()
