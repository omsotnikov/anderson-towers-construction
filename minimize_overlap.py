from argparse import ArgumentParser
from h5py import File
from pathlib import Path
from overlap_optimizer import OverlapOptimizer
from overlap_functions import get_coherent_state, read_statevectors
import numpy as np

    
def get_parameters():

    p = ArgumentParser()
    p.add_argument('spins', help='Path to hdf5 file with classical magnetic spins configuration to make target coherent state.')
    p.add_argument('eigenvectors', help='Path to file with dense eigenvectors.')
    p.add_argument('--states', type=int, default=2, help='Total states with different energy involved in simulation (each state could be degenerate).')
    p.add_argument('--steps', type=int, default=100, help='Total number of gradient descent steps.')
    p.add_argument('--gamma', default=0.1, type=float, help='Gradient descent step value.')
    p.add_argument('--delta', default=0.001, type=float, help='Finite difference approximation step for derivetive.')
    p.add_argument('--start', default='', help='Path to hdf5 file with starting coefficients (e.g. from previous run).')
    p.add_argument('--tolerance', default=1e-9, type=float, help='Tolerance for floating point comparison.')
    p.add_argument('--root', default='', help='Root of data in hdf5 file containing eigenvectors.')
    p = p.parse_args()

    if not p.root.endswith('/'):
        p.root += '/'
    
    return p


def main():

    p = get_parameters()

    if not p.steps:
        return

    # inspect multiplicity of vectors and read corresponding number of states
    vecs = read_statevectors(p.eigenvectors, p.root, p.states, p.tolerance)
    total_vecs = vecs.shape[0]
    print('Total vectors involved: {0}'.format(total_vecs))

    # target statevector is constructed from classic spins
    with File(p.spins, 'r') as f:
        spins = f['spins'][:]
        coordinates = f['coordinates'][:]
        target = get_coherent_state(spins, p.tolerance)

    # read initial coefficients if given
    coeff = None
    if p.start:
        with File(p.start, 'r') as f:
            coeff = f['coefficients'][:]
            odelta = f['/parameters/delta'][()]
            ogamma = f['/parameters/gamma'][()]
        if np.abs(ogamma - p.gamma) > p.tolerance:
            print('Warning! Gamma was changed! (old: {0}, new: {1})'.format(ogamma, p.gamma))
        if np.abs(odelta - p.delta) > p.tolerance:
            print('Warning! Delta was changed! (old: {0}, new: {1})'.format(odelta, p.delta))

    # initialize optimizer
    optimizer = OverlapOptimizer(vecs, p.gamma, p.delta, target, coeff)
    coeff = optimizer.coefficients()

    # save entire evolution
    coeff_evolution = np.ndarray((p.steps+1, total_vecs), complex)
    coeff_evolution[0,:] = coeff.copy()
    error_evolution = np.ndarray((p.steps+1,), float)
    error_evolution[0] = optimizer.overlap()
    
    print('Error value:')
    print(0, error_evolution[0])

    # gradient descent loop (use OverlapOptimizer.run() if you do not need to keep track on evolution)
    for n in range(1,p.steps+1):
        optimizer.step()
        error_evolution[n] = optimizer.overlap()
        coeff_evolution[n] = optimizer.coefficients()
        print(n, error_evolution[n])

    # write results
    with File('coefficients.h5', 'w') as f:
        f['k'] = total_vecs
        f['coefficients_evolution'] = coeff_evolution
        f['error_evolution'] = error_evolution
        f['coefficients'] = coeff_evolution[-1]
        f['error'] = error_evolution[-1]
        f['/parameters/delta'] = p.delta
        f['/parameters/gamma'] = p.gamma
        f['/parameters/steps'] = p.steps
        f['/parameters/eigenvectors_file'] = p.eigenvectors
        f['/parameters/spins'] = spins
        f['/parameters/coordinates'] = coordinates

    with File('statevector_approximation.h5', 'w') as f:
        f['eigenvectors'] = [optimizer.get_approximation()]


if __name__ == '__main__':
    main()
