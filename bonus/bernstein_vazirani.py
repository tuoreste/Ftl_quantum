"""
There is a secret bit string s hidden inside an oracle.
The oracle computes f(x) = x · s (mod 2)
which is the dot product of input x and secret s, result is 0 or 1.

CLASSICAL: need n queries to find n-bit secret (one query per bit)
QUANTUM:   need exactly 1 query always

HOW IT WORKS:
Same structure as Deutsch-Jozsa:
  1. Ancilla in |-⟩ for phase kickback
  2. H on all input qubits → superposition
  3. Oracle → phase kickback encodes secret into phases
  4. H on all input qubits → phases become amplitudes
  5. Measure → result IS the secret string directly

WHY IT WORKS:
The oracle flips the phase of input x by (-1)^(x·s)
After the final H gates, the only state with nonzero
amplitude is exactly |s⟩ — the secret string itself.
One measurement gives you the entire secret instantly.

"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import os

os.makedirs("results", exist_ok=True)

def make_oracle(secret):
    n = len(secret)

    input_qubits = QuantumRegister(n, name='input')
    ancilla      = QuantumRegister(1, name='ancilla')
    qc           = QuantumCircuit(input_qubits, ancilla)

    for i, bit in enumerate(reversed(secret)):
        if bit == '1':
            qc.cx(input_qubits[i], ancilla[0])

    gate      = qc.to_gate()
    gate.name = f"BV Oracle\n(s={secret})"
    return gate

def bernstein_vazirani(secret):
    n = len(secret)

    input_qubits = QuantumRegister(n, name='input')
    ancilla      = QuantumRegister(1, name='ancilla')
    cr           = ClassicalRegister(n, name='result')
    circuit      = QuantumCircuit(input_qubits, ancilla, cr)

    circuit.x(ancilla[0])
    circuit.h(ancilla[0])

    circuit.barrier()

    for q in range(n):
        circuit.h(input_qubits[q])

    circuit.barrier()

    oracle = make_oracle(secret)
    circuit.append(oracle, list(input_qubits) + list(ancilla))

    circuit.barrier()

    for q in range(n):
        circuit.h(input_qubits[q])

    circuit.barrier()

    for q in range(n):
        circuit.measure(input_qubits[q], cr[q])

    return circuit

def run_bv(secret, shots=500):
    print(f"\n{'='*40}")
    print(f"Secret string : '{secret}'")
    print(f"Length        : {len(secret)} bits")
    print(f"Classical cost: {len(secret)} queries (one per bit)")
    print(f"Quantum cost  : 1 query always")

    circuit = bernstein_vazirani(secret)

    print(f"\nCircuit:")
    print(circuit)
    circuit.draw('mpl')
    plt.title(f"Bernstein-Vazirani — secret='{secret}'")
    plt.savefig(f"results/bv_circuit_{secret}.png")
    plt.show()

    simulator = AerSimulator()
    compiled  = transpile(circuit, simulator)
    counts    = simulator.run(compiled, shots=shots).result().get_counts()

    print(f"\nResults ({shots} shots):")
    print(f"  Raw counts : {counts}")

    top_result  = max(counts, key=counts.get)
    top_prob    = counts[top_result] / shots * 100

    result_readable = top_result[::-1]

    print(f"  Top result : '{top_result}' → readable: '{result_readable}'")
    print(f"  Confidence : {top_prob:.1f}%")
    print(f"  Secret was : '{secret}'")

    if result_readable == secret:
        print(f"  Verdict    : SECRET FOUND ✓")
    else:
        print(f"  Verdict    : check bit ordering")

    plot_histogram(counts)
    plt.title(f"BV Results — secret='{secret}'")
    plt.savefig(f"results/bv_histogram_{secret}.png")
    plt.show()

    return counts

if __name__ == "__main__":

    run_bv('101')
    run_bv('111')
    run_bv('000')
    run_bv('10110')
    run_bv('1')