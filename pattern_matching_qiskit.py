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
anc_id = s * M


qr = QuantumRegister(total_qubits, 'q')
cr = ClassicalRegister(s, 'c')
qc = QuantumCircuit(qr, cr)

def init(qc, s, M):
    for i in range(0, s):
        qc.h(qr[i])
    
    for i in range(0, M-1):
        for j in range(0, s):
            qc.cx(qr[i * s + j], qr[i * s + s + j])
        for j in range(0, s):
            ic = (i + 1) * s - (j + 1)
            qc.x(qr[ic])
            nc = []
            for k in range(ic, (i + 1) * s):
                nc.append(k)
            for k in range((i + 2) * s - 1,s + ic - 1, -1):
                nCX(nc, k, anc_id)        
            qc.x(qr[ic])
    return

def oracle_function(f, s, q):
    for i in range(0, len(f)):
        if f[i] == '1':
            fis = format(i, '0'+str(s)+'b')
            for j in range(0, s):
                if fis[j] == '0':
                    qc.x(qr[q*s + j])
            qc.h(qr[(q+1) * s - 1])
            nc = []

            for j in range(q * s,(q+1) * s - 1):
                nc.append(j)

            nCX(nc, (q + 1)  * s - 1, anc_id)
            qc.h(qr[(q + 1)  * s - 1])

            for j in range(0, s):
                if fis[j] == '0':
                    qc.x(qr[q * s + j])
    

def amplitude_amplification(s, M):
    for i in range(0, s * M):
        qc.h(qr[i])
        qc.x(qr[i])

    qc.h(qr[s * M - 1])
    nc = []
    for j in range(0, s * M - 1):
        nc.append(j)
    nCX(nc, s * M - 1, s * M)
    qc.h(qr[s * M - 1])

    for i in range(0, s * M):
        qc.x(qr[i])
        qc.h(qr[i])

def nCX(c, t, b):
    nc = len(c)
    if nc == 1:
        qc.cx(qr[c[0]], qr[t])
    elif nc == 2:
        qc.toffoli(qr[c[0]],qr[c[1]],qr[t])
    else:
        nch = ceil(nc/2)
        c1 = c[:nch]
        c2 = c[nch:]
        nCX(c1, b, nch + 1)
        nCX(c2, t, nch - 1)
        nCX(c1, b, nch + 1)
        nCX(c2, t, nch - 1)
    return



bfa = ''.join('1' if w[i] == '0' else '0' for i in range(len(w)))
bfc = ''.join('1' if w[i] == '1' else '0' for i in range(len(w)))
bfg = ''.join('1' if w[i] == '2' else '0' for i in range(len(w)))
bft = ''.join('1' if w[i] == '3' else '0' for i in range(len(w)))

init(qc, s, M)

for _i in range(0, int(sqrt(N - M + 1))):
# for _i in range(0, M):
    i = random.randint(0, M - 1)
    # i = _i
    if p[i] == '0':
        oracle_function(bfa, s, i)
    elif p[i] == '1':
        oracle_function(bfc, s, i)
    elif p[i] == '2':
        oracle_function(bfg, s, i)
    else:
        oracle_function(bft, s, i)
    amplitude_amplification(s, M)


# x = 0
for i in range(0, s):
    qc.measure(qr[i], cr[i])
    # x = x + 1

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


