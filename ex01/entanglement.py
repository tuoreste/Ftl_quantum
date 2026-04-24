import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
import matplotlib.pyplot as plt
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram

qr = QuantumRegister(2, name='q')
cr = ClassicalRegister(2, name='c')

circuit = QuantumCircuit(qr, cr)
#print(circuit)

circuit.h(qr[0])
#print(circuit)

circuit.cx(qr[0], qr[1])
print(circuit)

circuit.measure(qr[0], cr[0])
circuit.measure(qr[1], cr[1])

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
