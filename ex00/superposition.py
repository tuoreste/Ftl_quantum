import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

qr = QuantumRegister(1, name='q')
cr = ClassicalRegister(1, name='c')
circuit = QuantumCircuit(qr, cr)

#print(circuit)
circuit.h(qr[0])
#print(circuit)

circuit.measure(qr[0], cr[0])

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