"""

0 & 1 classical computer bits
A qubit: the quantum version of a bit. 2 outcomes when measured, 0 or 1
a qubit however does not need to be in a definate state, it can be in a combination of both 0 and 1 simultaneously
called superposition.
this is a definate situation of both existing at the same time. |ψ⟩ = α|0⟩ + β|1⟩
where α and β are the probability amplitudes(complex numbers on circle) which should always satisfy |α|² + |β|² = 1

from superposition we measure which collapses to 0 or 1. the qubit choose 0 or 1 after measurement
this is called wavefunction collapse. One  can not measure a qubit without disturbing the system that holds it.

the consequence of this is, one can never get to observe directly the amplitudes α and β. To estimate the probabilities
one has to run the circuit hundred of times, closer to the true probability.

quantum gates are rotations of the sphere where H gate rotates the north pole to the equator
which is exactly why it creates a superposition from |0⟩. Measurements colapses this to noth or south.
A quantum gate tranforms the qubit's state. It is an equivalent of logical operation

quantum gates 3 properties:
1. reversible
2. preserve normalization, the gate does not break the probability rule
3. linear gates act on amplitudes mathematically as matrix multiplication

X-gate is a quantum NOT, flips |0⟩ to |1⟩ and vice versa
H-gate takes a definate state and puts it into equal superposition where
    H|0⟩ = (1/√2)|0⟩ + (1/√2)|1⟩
    H|1⟩ = (1/√2)|0⟩ - (1/√2)|1⟩

Quantum circuits: sequence of gates applied to qubits to some measurements

simulator: runs on CPU, perfectly simulating quantum behavior using matrix math. no noise, no errors
"""

import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# qr = QuantumRegister(1, name='q')
# cr = ClassicalRegister(1, name='c')
# circuit = QuantumCircuit(qr, cr)
circuit = QuantumCircuit(1)

#print(circuit)
# circuit.h(qr[0])
circuit.h(0)
#print(circuit)

# circuit.measure(qr[0], cr[0])
# circuit.measure(0, 0)
circuit.measure_all()

print("Circuit diagram:")
print(circuit)

print("\ndrawing the graphical representation of the circuit...")
circuit.draw(output='mpl')

plt.title("Superposition Circuit")
plt.savefig("results/superposition_circuit.png")
plt.show()

#______________________aer local simulator______________________
simulator = AerSimulator()
compiled_circuit = transpile(circuit, simulator)

job = simulator.run(compiled_circuit, shots=500)
result = job.result()
counts = result.get_counts()

print("\nMeasurement results (raw counts):")
print(counts)

print("\n Displaying the histogram")
plot_histogram(counts)
plt.title("Ex00 - Measurement Results - 500 shots")
plt.savefig("results/superposition_histogram.png")
plt.show()