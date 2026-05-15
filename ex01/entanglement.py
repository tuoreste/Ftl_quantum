from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

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