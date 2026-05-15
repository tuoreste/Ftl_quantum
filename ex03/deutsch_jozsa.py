from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import os

os.makedirs("results", exist_ok=True)

def oracle_constant(circuit, input_qubits, ancilla_qubit):
    pass

def oracle_balanced(circuit, input_qubits, ancilla_qubit):
    circuit.cx(input_qubits[0], ancilla_qubit[0])
    circuit.cx(input_qubits[1], ancilla_qubit[0])
    circuit.cx(input_qubits[2], ancilla_qubit[0])

def deutsch_jozsa(oracle_fn, oracle_name="unknown"):
    qr_i = QuantumRegister(3, name="input")
    qr_a = QuantumRegister(1, name="ancilla")
    cr   = ClassicalRegister(3, name="result")

    qc = QuantumCircuit(qr_i, qr_a, cr)

    qc.x(qr_a)
    qc.h(qr_a)

    qc.h(qr_i)

    qc.barrier()
    oracle_fn(qc, qr_i, qr_a)

    qc.barrier()
    qc.h(qr_i)

    qc.barrier()
    qc.measure(qr_i, cr)

    return qc

def run_and_interpret(circuit, label):
    simulator = AerSimulator()
    counts = simulator.run(transpile(circuit, simulator), shots=500).result().get_counts()

    measured = max(counts, key=counts.get)

    answer = "0" if measured == "000" else "1"
    verdict = "CONSTANT" if answer == "0" else "BALANCED"

    assignment_counts = {answer: counts[measured]}

    print(f"\n{'='*40}")
    print(f"Oracle: {label}")
    print(f"Raw counts: {counts}")
    print(f"Measured input qubits: {measured}")
    print(f"Verdict: {verdict}")
    print(f"Assignment output bit: {answer}")

    return assignment_counts

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
