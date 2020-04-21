from qiskit import ClassicalRegister
from qiskit import QuantumRegister
from qiskit import QuantumCircuit
from math import *

N = 8                           # Reference Genome size
w = "22013220"                  # Reference Genome
p = "32"                        # Short Read
M = len(p)                      # Short Read size
s = ceil(log2(N-M))
total_qubits = 2*s*M-2

qr = QuantumRegister(total_qubits, 'q')
cr = ClassicalRegister(s + 1, 'c')
qc = QuantumCircuit(qr, cr)

def init(qc, s, M):
    for i in range(0, s):
        qc.h(qr[i])
    
    for i in range(0, M-1):
        for j in range(0, s):
            qc.cx(qr[i * s + j], qr[i * s + s + j])
        for j in range(0, s):
            qc.x(qr[i * s + s - 1 - j])
            nc = []
            for k in range(i * s + s - 1, i * s + s - 1 - j - 1, -1):
                nc.insert(0,k)
            for k in range(i * s + s + s - 1, i * s + s + s - 1 - j - 1, - 1):
                nCX(nc, k, s * M)        
            qc.x(qr[i * s + s - 1 - j])


def oracle_function(f, s, q, anc):
    for i in range(0, len(f)):
        if f[i]:
            for j in range(0, s):
                if not f[j]:
                    qc.x(qr[q + j])
            qc.h(qr[q + s - 1])
            nc = []

            for j in range(q, q + s - 1):
                nc.append(j)

            nCX(nc, q + s - 1, anc)
            qc.h(qr[q + s - 1])

            for j in range(0, s):
                if not f[j]:
                    qc.x(qr[q + j])
    

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

def nCX(c, t, anc):
    nc = len(c)
    if nc == 1:
        qc.cx(qr[c[0]], qr[t])
    elif nc == 2:
        qc.toffoli(qr[c[0]],qr[c[1]],qr[t])
    else:
        qc.toffoli(qr[c[0]],qr[c[1]],qr[anc])
        for i in range(2, nc):
            qc.toffoli(qr[c[i]],qr[anc + i - 2],qr[anc + i - 1])

        qc.cx(qr[anc + nc - 2], qr[t])

        for i in range(nc - 1, 1, -1):
            qc.toffoli(qr[c[i]], anc + i - 2, anc + i - 1)
        qc.toffoli(qr[c[0]], qr[c[1]], anc) 




init(qc, s, M)

fa = []
fc = []
fg = []
ft = []

for wi in range(0,N):
    if w[wi] == '0':
        fa.append(True)
        fc.append(False)
        fg.append(False)
        ft.append(False)
    elif w[wi] == '1':
        fa.append(False)
        fc.append(True)
        fg.append(False)
        ft.append(False)
    elif w[wi] == '2':
        fa.append(False)
        fc.append(False)
        fg.append(True)
        ft.append(False)
    else:
        fa.append(False)
        fc.append(False)
        fg.append(False)
        ft.append(True)

for i in range(0,M):
    if p[i] == '0':
        oracle_function(fa, s, i * s, s * M)
    elif p[i] == '1':
        oracle_function(fc, s, i * s, s * M)
    elif p[i] == '2':
        oracle_function(fg, s, i * s, s * M)
    else:
        oracle_function(ft, s, i * s, s * M)
    
    amplitude_amplification(s, M)

x = 0
for i in range(total_qubits - s - 1, total_qubits):
    qc.measure(qr[i], cr[x])
    x = x + 1

#Illustrating the quantum circuit
from qiskit.visualization import plot_histogram
# qc.draw(output='mpl', filename='pm_8_bit.pdf')
qc.draw(output='mpl', filename='pm_8_bit.png')
print(qc.qasm())

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


