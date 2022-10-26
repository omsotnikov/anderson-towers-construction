from qiskit import Aer, execute
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from cmath import phase
from functools import reduce
from h5py import File
import numpy as np


def level_multiplicity(idx: int, eigenvalues: np.ndarray, tolerance: float):

    mult = 0
    total_elements = eigenvalues.shape[0]
    for i in range(idx, total_elements):
        if np.abs(eigenvalues[idx] - eigenvalues[i]) > tolerance:
            return i, mult
        mult += 1

    return total_elements-1, mult


def multiplicity(eigenvalues: np.ndarray, tolerance: float):

    total_eigenvalues = eigenvalues.shape[0]
    i, mult = level_multiplicity(0, eigenvalues, tolerance)
    mults = []
    while i != total_eigenvalues-1:
        mults.append(mult)
        i, mult = level_multiplicity(i, eigenvalues, tolerance)

    mults.append(mult)
        
    return mults


def read_statevectors(fn: str, root: str, states: int, tolerance: float):

    with File(fn, 'r') as f:

        vals = f[root + 'eigenvalues'][:]

        mults = multiplicity(vals, tolerance)
        total_vecs = reduce(lambda x, y: x+y, mults[:states])

        vecs = f[root + 'eigenvectors'][:total_vecs,:]

    return vecs


def get_coherent_state(spins: np.ndarray, tolerance: float):

    num_qbits = spins.shape[0]
    
    thetas = np.ndarray((num_qbits,))
    phis = np.ndarray((num_qbits,))

    for i in range(num_qbits):
        thetas[i] = np.arccos(spins[i,2])
        if thetas[i] > tolerance:
            phis[i] = np.arctan2(spins[i,1],spins[i,0])
        else:
            phis[i] = 0

    circ = QuantumCircuit(num_qbits)

    for i in range(num_qbits):
        circ.u(thetas[i], phis[i], 0.0, i)

    simulator = Aer.get_backend('statevector_simulator')

    job = execute([circ], simulator)
    result = job.result()

    vec = result.get_statevector(circ)

    # Qiskit treats |0> as spin-up and |1> as spin-down
    # Here we swap ones and zeros in basis to store statevector in conventional way
    # and keep the matrices of spin operators consistent
    res = np.ndarray(vec.shape,complex)
    for n, c in enumerate(vec):
        bit = 0
        for i in range(num_qbits):
            pos = 1<<i
            if not (n & pos):
                bit += pos
        res[bit] = vec[n]
    
    return res
    

def sz(i: int, vec: np.ndarray):

    res = 0
    bit = 1<<i
    for n, c in enumerate(vec):
        res += np.conj(c)*c*(0.5 if n & bit else -0.5)

    return res


def sx(i: int, vec: np.ndarray):

    res = 0
    bit = 1<<i
    for n, c in enumerate(vec):
        nbit = n ^ bit
        res += np.conj(vec[nbit])*c*0.5

    return res


def sy(i: int, vec: np.ndarray):

    res = 0
    bit = 1<<i
    for n, c in enumerate(vec):
        nbit = n ^ bit
        res += np.conj(vec[nbit])*c*(0.5j if n & bit else -0.5j)

    return res
    
