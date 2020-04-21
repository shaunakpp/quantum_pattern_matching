from qiskit import ClassicalRegister
from qiskit import QuantumRegister
from qiskit import QuantumCircuit

n = 2
#Creating quantum and classical registers 
qr = QuantumRegister(2,"q")
cr = ClassicalRegister(2,"c")

#Creating a quantum circuit, acting on "q" and "c" 
qc = QuantumCircuit(qr, cr)

## Searches for 11

for i in range(n):
    qc.h(qr[i])

# for 11 don't apply any S gate
# for 01 apply S gate to 1st bit
# for 10 apply S gate to 2nd bit
# for 00 apply S gate to all bits
# qc.s(qr[0])
# qc.s(qr[1])
# qc.s(qr[0])
# qc.s(qr[1])

# for z in range(0,10):
#Oracle
qc.h(qr[1]) #Hadamard to second register
qc.cx(qr[0],qr[1]) #Control function for both qubits
qc.h(qr[1]) #Hadamard to second register

for i in range(n): #Hadamard on both qubits
    qc.h(qr[i])

#Reflection of Oracle function
for i in range(n): #X gates/ bit flips on both qubits
    qc.x(qr[i])

qc.h(qr[1]) #Hadamard to second register
qc.cx(qr[0],qr[1]) #Control function for both qubits
qc.h(qr[1])  #Hadamard to second register

for i in range(n):  #X gates/ bit flips on both qubits
    qc.x(qr[i])
for i in range(n): #Hadamard on both qubits
    qc.h(qr[i])

#Measurements of qubits along Z-axis
qc.measure(qr[0], cr[0])
qc.measure(qr[1], cr[1])


#Illustrating the quantum circuit
from qiskit.visualization import plot_histogram
qc.draw(output='mpl', filename='grovers_2_bit.pdf')
qc.draw(output='mpl', filename='grovers_2_bit.png')


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
