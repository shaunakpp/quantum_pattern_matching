# Quantum Pattern Matching algorithm
# Code for CMSC 691 Project
# by Shaunak Pagnis, Atharva Muley and Mohit Nayak
# The code is based on the following paper:
# "Quantum Pattern Matching"  by P. Mateus and Y.Omar
# DOI: https://arxiv.org/pdf/quant-ph/0508237.pdf

from qiskit import ClassicalRegister
from qiskit import QuantumRegister
from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram
from qiskit import Aer
from qiskit import execute

from math import *
import random
import operator

# Limits for actual QPU, change these in case you want to test larger strings on simulator

DNA_STRING_LIMIT = 8
SEARCH_STRING_LIMIT = 4

# Pattern matcher that accepts DNA string and search string as input.
# Runs on QPU/simulator to give a closest match index location  of the search string
class QuantumPatternMatcher():
    def __init__(self, dna_string, search_string, shots=100):
        if len(dna_string) > DNA_STRING_LIMIT:
            raise ValueError("Given dna string exceeds limit")

        if len(search_string) > SEARCH_STRING_LIMIT:
            raise ValueError("Given search string exceeds limit")

        # Attributes of input pattern
        self.dna_string = dna_string
        self.search_string = search_string
        self.N = len(dna_string)
        self.M = len(search_string)
        self.index_qubits = ceil(log2(self.N - self.M))
        self.total_qubits = self.index_qubits * self.M + 1
        self.ancilla_bit_id = self.index_qubits * self.M

        # Quantum Configuration
        self.qr = QuantumRegister(self.total_qubits, "q")
        self.cr = ClassicalRegister(self.index_qubits, "c")
        self.qc = QuantumCircuit(self.qr, self.cr)
        self.shots = shots
        self.simulator = Aer.get_backend('qasm_simulator')


        # Base strings
        self.adenine = ''.join('1' if self.dna_string[i] == 'a' else '0' for i in range(self.N))
        self.cyctosine = ''.join('1' if self.dna_string[i] == 'c' else '0' for i in range(self.N))
        self.guanine = ''.join('1' if self.dna_string[i] == 'g' else '0' for i in range(self.N))
        self.thyamine = ''.join('1' if self.dna_string[i] == 't' else '0' for i in range(self.N))


    def initialize_input_set(self):
        s = self.index_qubits
        # Initialize the qubits to uniform superposition
        for i in range(0, self.index_qubits):
            self.qc.h(self.qr[i])

        for i in range(0, self.M-1):
            # Add CNOT gates to copy positional encoding to the next set
            for j in range(0, s):
                self.qc.cx(self.qr[i * s + j], self.qr[i * s + s + j])
            # Increment the positional encoding
            for j in range(0, s):
                inverted_control_bit = (i + 1) * s - (j + 1)
                # Flip the control bit
                self.qc.x(self.qr[inverted_control_bit])
                control_bits = list(range(inverted_control_bit, (i + 1) * s))
                # Apply multi-controlled CX
                for k in range((i + 2) * s - 1, s + inverted_control_bit - 1, -1):
                    self.qc.mcx(control_bits, k)
                # Uncomputation of Flip the control bit
                self.qc.x(self.qr[inverted_control_bit])
        return

    def oracle_function(self, base_string, start_index):
        s = self.index_qubits
        target_bit = (start_index + 1) * s - 1
        for i in range(0, len(base_string)):
            if base_string[i] == '1':
                # hack to get binary representation of 'i' as a string
                binary_i = format(i, '0'+str(s)+'b')
                # Convert Binary representation 0, 1 to -1, 1 using Phase gate
                for j in range(0, s):
                    if binary_i[j] == '0':
                        self.qc.x(self.qr[start_index * s + j])

                control_bits = list(range(start_index * s, target_bit))
                # Apply multi controlled CX
                self.qc.mcx(control_bits, target_bit)

                # Uncomputation of Phase gate
                for j in range(0, start_index):
                    if binary_i[j] == '0':
                        self.qc.x(self.qr[start_index * s + j])
        return

    # Grover's amplitude amplification function
    def amplitude_amplification(self):
        target_bit = self.ancilla_bit_id - 1

        for i in range(0, self.ancilla_bit_id):
            self.qc.h(self.qr[i])
            self.qc.x(self.qr[i])

        control_bits = list(range(0, target_bit))
        self.qc.mcx(control_bits, target_bit)

        for i in range(0, self.ancilla_bit_id):
            self.qc.x(self.qr[i])
            self.qc.h(self.qr[i])
        return

    # Driver function
    def execute(self):
        self.initialize_input_set()

        grovers_iterations = int(sqrt(self.N + self.M - 1))
        for _i in range(0, grovers_iterations):
            for i in range(0, self.M):
                if self.search_string[i] == 'a':
                    self.oracle_function(self.adenine, i)
                elif self.search_string[i] == 'c':
                    self.oracle_function(self.cyctosine, i)
                elif self.search_string[i] == 'g':
                    self.oracle_function(self.guanine, i)
                else:
                    self.oracle_function(self.thyamine, i)
                self.amplitude_amplification()

        for i in range(0, self.index_qubits):
            self.qc.measure(self.qr[i], self.cr[i])

        # qc.draw(output='mpl', filename='pm_8_bit.png')
        # print(qc.qasm())


        #running the circuit on the local simulator
        job = execute(self.qc, self.simulator, shots=self.shots)

        result = job.result()

        counts = result.get_counts(self.qc)

        print('Running on local simulator')
        print('State', '\t\tOccurance')

        sorted_counts = dict(sorted(counts.items(), key=operator.itemgetter(1), reverse=True))

        for quantum_state in sorted_counts:
            print(quantum_state, '\t\t', sorted_counts[quantum_state])
        return

if __name__ == '__main__':
    qpm = QuantumPatternMatcher("cgattgac", "ga", 100)
    qpm.execute()