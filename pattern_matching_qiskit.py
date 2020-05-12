from qiskit import ClassicalRegister
from qiskit import QuantumRegister
from qiskit import QuantumCircuit

from math import *
import random
import operator

shots = 1000
N = 6                           # Reference Genome size
# w = "21013213"                  # Reference Genome
w = "gcatta"
M = 2                           # Short Read size
# p = "13"                        # Short Read
p = "gc"
print("Given String: ", w)
print("Search: ", p)
s = ceil(log2(N-M))
total_qubits = s * M + 1
ancilla_bit= s * M

qr = QuantumRegister(total_qubits, 'q')
cr = ClassicalRegister(s, 'c')
qc = QuantumCircuit(qr, cr)

def init(qc, s, M):
    # Initialize the qubits to uniform superposition
    for i in range(0, s):
        qc.h(qr[i])
    
    for i in range(0, M-1):
        # Add CNOT gates to copy positional encoding to the next set
        for j in range(0, s):
            qc.cx(qr[i * s + j], qr[i * s + s + j])
        # Increment the positional encoding
        for j in range(0, s):
            inverted_control_bit = (i + 1) * s - (j + 1)
            # Flip the control bit
            qc.x(qr[inverted_control_bit])
            control_bits = list(range(inverted_control_bit, (i + 1) * s))
            # Apply multi-controlled CX
            for k in range((i + 2) * s - 1, s + inverted_control_bit - 1, -1):
                qc.mcx(control_bits, k)
            # Uncomputation of Flip the control bit
            qc.x(qr[inverted_control_bit])
    return

def oracle_function(f, s, q):

    target_bit = (q + 1) * s - 1
    for i in range(0, len(f)):
        if f[i] == '1':
            # hack to get binary representation of 'i' as a string
            binary_i = format(i, '0'+str(s)+'b')
            # Convert Binary representation 0, 1 to -1, 1 using Phase gate
            for j in range(0, s):
                if binary_i[j] == '0':
                    qc.x(qr[q * s + j])


            # Apply H gate for Phase to CX gate conversion
            qc.h(qr[target_bit])
            # Select the control bits

            control_bits = list(range(q * s, target_bit))
            # Apply multi controlled CX
            qc.mcx(control_bits, target_bit)

            # Uncomputation of Phase to CX
            qc.h(qr[(q + 1)  * s - 1])

            # Uncomputation of Phase gate
            for j in range(0, s):
                if binary_i[j] == '0':
                    qc.x(qr[q * s + j])

# Grover's amplitude amplification function
def amplitude_amplification(s, M):
    target_bit = s * M - 1
    ancilla_bit = s * M

    for i in range(0, ancilla_bit):
        qc.h(qr[i])
        qc.x(qr[i])

    # Apply H gate for Phase to CX gate conversion
    qc.h(qr[target_bit])

    control_bits = list(range(0, target_bit))
    qc.mcx(control_bits, target_bit)

    # Uncomputation of Phase to CX
    qc.h(qr[target_bit])

    for i in range(0, ancilla_bit):
        qc.x(qr[i])
        qc.h(qr[i])

adenine = ''.join('1' if w[i] == 'a' else '0' for i in range(len(w)))
cyctosine = ''.join('1' if w[i] == 'c' else '0' for i in range(len(w)))
guanine = ''.join('1' if w[i] == 'g' else '0' for i in range(len(w)))
thyamine = ''.join('1' if w[i] == 't' else '0' for i in range(len(w)))

init(qc, s, M)

for _i in range(0, int(sqrt(N + M - 1))):
    for i in range(0, M):
        if p[i] == 'a':
            oracle_function(adenine, s, i)
        elif p[i] == 'c':
            oracle_function(cyctosine, s, i)
        elif p[i] == 'g':
            oracle_function(guanine, s, i)
        else:
            oracle_function(thyamine, s, i)
        amplitude_amplification(s, M)


for i in range(0, s):
    qc.measure(qr[i], cr[i])

#Illustrating the quantum circuit
from qiskit.visualization import plot_histogram
# qc.draw(output='mpl', filename='pm_8_bit.pdf')
# qc.draw(output='mpl', filename='pm_8_bit.png')
# print(qc.qasm())

#for running circuit on simulator or QPU
from qiskit import execute

#To run the quantum program on a local simulator 
from qiskit import Aer

simulator = Aer.get_backend('qasm_simulator')

#running the circuit on the localsimulator  
job = execute(qc, simulator, shots=shots)

#Fetching results from the job
result = job.result()

#Demonstrating resultss
counts = result.get_counts(qc)
#counts is a dictionary: states|number of times that the state has been observed
print('Running on local simulator')
print('State', '\t\tOccurance')

sorted_counts = dict(sorted(counts.items(), key=operator.itemgetter(1), reverse=True))

for quantum_state in sorted_counts:
    print(quantum_state, '\t\t', sorted_counts[quantum_state])
