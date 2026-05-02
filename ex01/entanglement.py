"""

with 2qubits now the possible outcomes are 2pow2(00,01,10,11)
2qubits have 2 different situations:
    - separable situation: each qubit has its own independent state. Can
    describe qubit0 on it's own and qubit1 on it's own all independently
    nothing to do with each other
    - entangled stated: the moment you measure one, you instantly dermine the other

meaning: for an entangled state on in Berlin and the other in Paris, the moment you measure
one in Berlin, you automatically measure the other one in Paris giving same results

@Einstein doubted this and called it "spooky action at a distance" arguing there must be some hidden
information carried inside each qubit from the beginning.

experiments prove Einstein otherwise. Qubits have genuinely no definive value before measurement
the correlation is real and instant. This can not be used to send info faster than light. The person
in paris gets a random result 0 or 1 and cannot control which one. They cannot encode message in randmness.

to create an entanglement we need one gate that acts on 2qubits at same time. It is called CNOT
rule:   If control = |0⟩  →  target is unchanged
        If control = |1⟩  →  target is flipped (X applied)
        Control | Target | Output Control | Output Target
        0    |   0    |       0        |       0
        0    |   1    |       0        |       1
        1    |   0    |       1        |       1   ← target flipped
        1    |   1    |       1        |       0   ← target flipped


"""

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt


# Create Bell state |Φ⁺⟩ = (|00⟩ + |11⟩) / √2
qc = QuantumCircuit(2, 2)

qc.h(0)
qc.cx(0, 1)

qc.measure([0, 1], [0, 1])

print(qc)

qc.draw("mpl")
plt.title("Bell State Entanglement Circuit")
plt.show()

simulator = AerSimulator()
compiled = transpile(qc, simulator)

result = simulator.run(compiled, shots=500).result()
counts = result.get_counts()

print("\nMeasurement Results:")
print(counts)

print("\nExpected:")
print("Only 00 and 11 should appear")

plot_histogram(counts)
plt.title("Bell State Measurement Results")
plt.show()