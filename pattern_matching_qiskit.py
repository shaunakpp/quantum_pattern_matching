from qiskit import ClassicalRegister
from qiskit import QuantumRegister
from qiskit import QuantumCircuit
from math import *
import random

N = 8                           # Reference Genome size
w = "22013213"                  # Reference Genome
p = "22"                        # Short Read
M = len(p)                     # Short Read size
s = ceil(log2(N-M))
total_qubits = s * M + 1
ancilla_bit_index = s * M

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
            nc = []
            for k in range(inverted_control_bit, (i + 1) * s):
                nc.append(k)
            # Apply multi-controlled CNOT
            for k in range((i + 2) * s - 1, s + inverted_control_bit - 1, -1):
                multi_controlled_c_not(nc, k, ancilla_bit_index)
            # Flip the control bit
            qc.x(qr[inverted_control_bit])
    return

def oracle_function(f, s, q):
    for i in range(0, len(f)):
        if f[i] == '1':
            # hack to get binary representation of 'i' as a string
            fis = format(i, '0'+str(s)+'b')
            for j in range(0, s):
                if fis[j] == '0':
                    qc.x(qr[q*s + j])
            qc.h(qr[(q+1) * s - 1])

            control_bits = []
            for j in range(q * s,(q+1) * s - 1):
                control_bits.append(j)

            multi_controlled_c_not(control_bits, (q + 1)  * s - 1, ancilla_bit_index)
            qc.h(qr[(q + 1)  * s - 1])

            for j in range(0, s):
                if fis[j] == '0':
                    qc.x(qr[q * s + j])
    
# Grover's amplitude amplification function
def amplitude_amplification(s, M):
    for i in range(0, s * M):
        qc.h(qr[i])
        qc.x(qr[i])

    qc.h(qr[s * M - 1])
    control_bits = []
    for j in range(0, s * M - 1):
        control_bits.append(j)
    multi_controlled_c_not(control_bits, s * M - 1, s * M)
    qc.h(qr[s * M - 1])

    for i in range(0, s * M):
        qc.x(qr[i])
        qc.h(qr[i])

# Multicontrolled CNOT gate
# For on control bit it is a CNOT gate
# For two control bits, this is essentially a Toffoli gate
# For multiple control bits, we split the control bits into two halves
# then the left half is connected to an ancilla bit and the right half
# is connected the to the target bit
def multi_controlled_c_not(control_bits, target_bit, ancilla_bit):
    len_c = len(control_bits)
    if len_c == 1:
        qc.cx(qr[control_bits[0]], qr[target_bit])
    elif len_c == 2:
        qc.toffoli(qr[control_bits[0]],qr[control_bits[1]],qr[target_bit])
    else:
        len_c_half = ceil(len_c/2)
        c_right = control_bits[:len_c_half]
        c_left = control_bits[len_c_half:]
        multi_controlled_c_not(c_right, ancilla_bit, len_c_half + 1)
        multi_controlled_c_not(c_left, target_bit, len_c_half - 1)
        multi_controlled_c_not(c_right, ancilla_bit, len_c_half + 1)
        multi_controlled_c_not(c_left, target_bit, len_c_half - 1)
    return



bfa = ''.join('1' if w[i] == '0' else '0' for i in range(len(w)))
bfc = ''.join('1' if w[i] == '1' else '0' for i in range(len(w)))
bfg = ''.join('1' if w[i] == '2' else '0' for i in range(len(w)))
bft = ''.join('1' if w[i] == '3' else '0' for i in range(len(w)))

init(qc, s, M)

for _i in range(0, int(sqrt(N + M - 1))):
    for i in range(0, M):
        if p[i] == '0':
            oracle_function(bfa, s, i)
        elif p[i] == '1':
            oracle_function(bfc, s, i)
        elif p[i] == '2':
            oracle_function(bfg, s, i)
        else:
            oracle_function(bft, s, i)
        amplitude_amplification(s, M)


for i in range(0, s):
    qc.measure(qr[i], cr[i])

#Illustrating the quantum circuit
from qiskit.visualization import plot_histogram
# qc.draw(output='mpl', filename='pm_8_bit.pdf')
qc.draw(output='mpl', filename='pm_8_bit.png')
# print(qc.qasm())

#for running circuit on simulator or QPU
from qiskit import execute

#To run the quantum program on a local simulator 
from qiskit import Aer
simulator = Aer.get_backend('qasm_simulator')

#running the circuit on the localsimulator  
job = execute(qc, simulator, shots=1000)

#Fetching results from the job
result = job.result()

#Demonstrating resultss
counts = result.get_counts(qc)
#counts is a dictionary: states|number of times that the state has been observed
print('Running on local simulator')
print('State', '\tOccurance') 
for quantum_state in counts:
    print(quantum_state, '\t\t', counts[quantum_state])


