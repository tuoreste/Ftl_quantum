import math
import os

from qiskit import QuantumCircuit, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

os.makedirs("results", exist_ok=True)

def make_oracle(n, target):
    qc = QuantumCircuit(n)

    for i, bit in enumerate(reversed(target)):
        if bit == "0":
            qc.x(i)

    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)

    for i, bit in enumerate(reversed(target)):
        if bit == "0":
            qc.x(i)

    oracle = qc.to_gate()
    oracle.name = f"Oracle\n({target})"

    return oracle

def make_diffuser(n):
    qc = QuantumCircuit(n)

    qc.h(range(n))
    qc.x(range(n))

    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)

    qc.x(range(n))
    qc.h(range(n))

    diffuser = qc.to_gate()
    diffuser.name = "Diffuser"

    return diffuser

def grover(n, target):
    iterations = max(1, math.floor(math.pi / 4 * math.sqrt(2**n)))

    cr = ClassicalRegister(n, "result")
    qc = QuantumCircuit(n)
    qc.add_register(cr)

    qc.h(range(n))
    qc.barrier()

    oracle = make_oracle(n, target)
    diffuser = make_diffuser(n)

    for _ in range(iterations):
        qc.append(oracle, range(n))
        qc.append(diffuser, range(n))
        qc.barrier()

    qc.measure(range(n), range(n))

    return qc, iterations

def run_grover(n, target, shots=1000):
    qc, iterations = grover(n, target)

    print(f"\nGrover Search")
    print(f"Target      : |{target}⟩")
    print(f"Qubits      : {n}")
    print(f"Iterations  : {iterations}")

    simulator = AerSimulator()
    counts = simulator.run(
        transpile(qc, simulator),
        shots=shots
    ).result().get_counts()

    top = max(counts, key=counts.get)
    probability = counts[top] / shots * 100

    print(f"Top result  : |{top}⟩ ({probability:.1f}%)")
    print(f"Verdict     : {'FOUND ✓' if top == target else 'FAILED'}")

    qc.draw("mpl")
    plt.title(f"Grover Circuit |{target}⟩")
    plt.savefig(f"results/grover_circuit_{target}.png")
    plt.show()

    plot_histogram(counts)
    plt.title(f"Grover Results |{target}⟩")
    plt.savefig(f"results/grover_histogram_{target}.png")
    plt.show()

    return counts

if __name__ == "__main__":

    tests = [
        (3, "111"),
        (3, "101"),
        (2, "10"),
        (4, "1010"),
    ]

    for n, target in tests:
        run_grover(n, target)