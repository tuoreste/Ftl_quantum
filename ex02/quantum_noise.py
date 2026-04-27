"""

sources of quantum noises, engineering imperfection

1. Gate errors:
    Every quantum gate on real hardware is implemented by firing a precisely timed microwave pulse at a superconducting qubit.
    The pulse is supposed to rotate the qubit's state by an exact angle on the Bloch sphere. But pulses are never perfectly calibrated:
        Intended rotation:  exactly 90°
        Actual rotation:    90.3°
    That tiny angle error means the output state is slightly wrong.
    After several gates the errors accumulate.
    Small wrong amplitudes appear on states that should have zero probability — like |01⟩ and |10⟩.

2. Decoherence
    - The hardware can not hold the state perfectly
    - A qubit in superposition is extraordinarily fragile.
    Any interaction with the environment — stray electromagnetic fields, heat, vibration — causes the qubit to lose its quantum state and collapse randomly.
        ==> T1  →  relaxation time: how long before |1⟩ spontaneously decays to |0⟩ typically 50-200 microseconds
        ==> T2  →  coherence time: how long superposition survives before becoming random typically 50-150 microseconds

3. Readouts errors
    - When you measure a qubit, the hardware has to distinguish between two very similar physical signals.

4. Cross talks
    - Gate on qubit0  →  accidentally nudges qubit1 slightly
                   qubit1's state shifts by a tiny unwanted amount

A simulator is just math matrix maultiplication
Numbers are exact. No physical pulses. No temperature. No neighboring qubits interfering. No time passing. 

"""


import os
import sys

import qiskit_ibm_runtime
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
import matplotlib.pyplot as plt

os.makedirs("results", exist_ok=True) 


qr = QuantumRegister(2, name='q')
cr = ClassicalRegister(2, name='c')
circuit = QuantumCircuit(qr, cr)

circuit.h(qr[0])
circuit.cx(qr[0], qr[1])
circuit.measure(qr[0], cr[0])
circuit.measure(qr[1], cr[1])

print("Circuit (identical to ex01):")
print(circuit)


simulator = AerSimulator()
compiled_circuit = transpile(circuit, simulator)
ideal_counts = simulator.run(compiled_circuit, shots=500).result().get_counts()
print("\nIdeal simulator results:", ideal_counts)


try:
    service = QiskitRuntimeService(channel='ibm_quantum_platform')
except Exception as e:
    print(f"\nFailed to load IBM Quantum account: {e}")
    print("Run save_account first. See setup instructions at the top of this file.")
    sys.exit(1)


backend = service.least_busy(
    operational=True,
    simulator=False,
    min_num_qubits=2
)
print(f"\nUsing real backend: {backend.name}")


real_circuit = transpile(circuit, backend)

try:
    sampler = Sampler(backend)
    job = sampler.run([real_circuit], shots=500)
    print("\nJob submitted. Waiting for results (may take several minutes)...")

    real_result = job.result()
    real_counts = real_result[0].data.c.get_counts()
    print("\nReal hardware results:", real_counts)

except Exception as e:
    print(f"\nJob failed: {e}")
    print("This can happen due to queue timeouts or backend maintenance.")
    sys.exit(1)


fig, axes = plt.subplots(1, 2, figsize=(12, 4))

plot_histogram(ideal_counts, ax=axes[0], title="Ideal Simulator")
plot_histogram(real_counts,  ax=axes[1], title=f"Real Hardware: {backend.name}")

plt.suptitle("Ex02 - Simulator vs Real Quantum Computer", fontsize=14)
plt.tight_layout()
plt.savefig("results/ex02_comparison.png") 
plt.show()

# ─── 6. Noise analysis ──────────────────────────────────────────────────


total_shots = sum(real_counts.values())
noise_counts = real_counts.get('01', 0) + real_counts.get('10', 0)
noise_rate   = noise_counts / total_shots * 100
clean_rate   = 100 - noise_rate

print(f"\nNoise analysis:")
print(f"  Total shots      : {total_shots}")
print(f"  Noisy outcomes   : {noise_counts}  ('01' + '10')")
print(f"  Noise rate       : {noise_rate:.1f}%")
print(f"  Clean outcomes   : {total_shots - noise_counts}  ('00' + '11')")
print(f"  Fidelity approx  : {clean_rate:.1f}%")