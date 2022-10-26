#!/bin/bash

# Eleven energy levels corresponds to full spectrum of 512 eigenstates due to multiplicity.
# You can play with --states and other parameters to see changes in resulting approximation.
# (for e.g. try states=1, states=2 or states=3)
# You also can try to continue previous calculation by specifying --start key
# (for e.g. --start triangular3x3.xy.coefficients.h5) to get even more accurate approximation.
# Alternatively, you can specify more steps. 

states=11
steps=100
gamma=10

echo "Calculate approximation for in-plane Neel state..."

# Calculation for in-plate Neel state
python3 ./minimize_overlap.py --root /hamiltonian --gamma ${gamma} --steps ${steps} --states ${states} triangular3x3.xy.classic_spins.h5 triangular3x3.eigenvectors.full.h5
mv coefficients.h5 triangular3x3.xy.coefficients.h5
mv statevector_approximation.h5 triangular3x3.xy.approximation.h5

# Measure <Sx>, <Sy> and <Sz> to reconstruct classical magnetic moments of approximate statevector
python3 ./reconstruct_classic.py triangular3x3.xy.approximation.h5 triangular3x3.coordinates.h5

# print error function evolution in XY file format
python3 ./print_error_function.py triangular3x3.xy.coefficients.h5 > triangular3x3.xy.error_function.dat

echo "Calculate approximation for another Neel ordering..."

# Calculation for another Neel ordering
python3 ./minimize_overlap.py --root /hamiltonian --gamma ${gamma} --steps ${steps} --states ${states} triangular3x3.classic_spins.h5 triangular3x3.eigenvectors.full.h5
mv coefficients.h5 triangular3x3.coefficients.h5
mv statevector_approximation.h5 triangular3x3.approximation.h5

# Measure <Sx>, <Sy> and <Sz> to reconstruct classical magnetic moments of approximate statevector
python3 ./reconstruct_classic.py triangular3x3.approximation.h5 triangular3x3.coordinates.h5

# print error function evolution in XY file format
python3 ./print_error_function.py triangular3x3.coefficients.h5 > triangular3x3.error_function.dat

# draw approximated classical magnetic moments in pdf format 
python3 ./draw_spins.py --radius 0.498 --edge 0.7 --zoom 0.98 *.reconstructed_spins.h5 --z-limits -1 1 --save pdf --transparent
