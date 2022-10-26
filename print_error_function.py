from argparse import ArgumentParser
from h5py import File
import numpy as np


def get_parameters():

    p = ArgumentParser()
    p.add_argument('results', help='Path to hdf5 file with results of minimization.')
    p = p.parse_args()

    return p


def main():

    p = get_parameters()

    with File(p.results, 'r') as f:
        error = f['error_evolution'][:]

    for i, e in enumerate(error):
        print(i, e)


if __name__ == '__main__':
    main()
