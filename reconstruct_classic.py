from argparse import ArgumentParser
from h5py import File
from overlap_functions import sx, sy, sz
import numpy as np


def get_parameters():

    p = ArgumentParser()
    p.add_argument('vec', help='Path to hdf5 file with eigenvectors.')
    p.add_argument('coordinates', help='Path to hdf5 file with classical coordinates of sites.')
    p.add_argument('--state', type=int, default=0, help='Index of state to use (should be non-degenerate).')
    p.add_argument('--root', default='', help='Root of eigenvectors dataset in hdf5 file.')
    p.add_argument('--tolerance', type=float, default=1e-9, help='Tolerance for floating point comparison.')
    p = p.parse_args()

    if not p.root.endswith('/'):
        p.root += '/'
    
    return p


def main():

    p = get_parameters()

    with File(p.vec, 'r') as f:
        vec = f[p.root+'eigenvectors'][p.state,:]

    with File(p.coordinates, 'r') as f:
        coordinates = f['coordinates'][:]

    L = coordinates.shape[0]

    spins = np.ndarray((L,3))
    for i in range(L):

        s = [sx(i,vec), sy(i,vec), sz(i,vec)]

        for spin in s:
            if np.abs(spin.imag) > p.tolerance:
                print('Warning! Found imaginary part in an classical spin component!')

        # factor of 2 is due to S = 1/2 system
        spins[i,:] = 2*np.real(s)

    ofn = p.vec.strip().split('.')
    ofn.insert(-1, 'reconstructed_spins')
    ofn = '.'.join(ofn)

    if ofn == p.vec:
        raise RuntimeError('Input and output file names are the same. Exiting.')

    with File(ofn, 'w') as f:
        f['spins'] = spins
        f['coordinates'] = coordinates    
    

if __name__ == '__main__':
    main()
