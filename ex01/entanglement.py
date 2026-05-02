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

import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
import matplotlib.pyplot as plt
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram

# qr = QuantumRegister(2, name='q')
# cr = ClassicalRegister(2, name='c')

circuit = QuantumCircuit(2)
#print(circuit)

# circuit.h(qr[0])
circuit.h(0)
#print(circuit)

# circuit.cx(qr[0], qr[1])
circuit.cx(0, 1)
print(circuit)

# circuit.measure(qr[0], cr[0])
# circuit.measure(qr[1], cr[1])
circuit.measure_all()

circuit.draw('mpl')
plt.title("Entanglement Circuit")
plt.savefig("results/entanglement_circuit.png")
plt.show()

simulator = AerSimulator()
compiled_circuit = transpile(circuit, simulator)
job = simulator.run(compiled_circuit, shots=500)
result = job.result()
counts = result.get_counts()

print("\nMeasurement results:")
print(counts)
print("\nExpected: only '00' and '11' should appear")

plot_histogram(counts)
plt.title("Ex01 - Entangled Measurement Results (500 shots)")
plt.savefig("results/entanglement_histogram.png")
plt.show()
