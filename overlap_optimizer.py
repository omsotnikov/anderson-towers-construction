import numpy as np

class OverlapOptimizer:

    # one must specify target for current overlap function
    def __init__(self, vectors: np.ndarray, gamma: float, delta: float, target: np.ndarray = None, coefficients: np.ndarray = None):

        self._target = target
        self._vectors = vectors
        self._vector_size = vectors.shape[1]
        self._total_vectors = vectors.shape[0]
        self._buffer = np.zeros((self._vector_size,), complex)
        self._norm = None
        self._delta = delta
        self._gamma = gamma

        # initialize coefficients
        if coefficients is None:
            self._initialize_random_coefficients()
        else:
            self._validate_coefficients(coefficients)
            self._coeff = coefficients.copy()

        # initialize first approximation
        self._update_superposition()

    def overlap(self):
        return 1 - np.abs(np.vdot(self._target, self._buffer/self._norm))

    def coefficients(self):
        return self._coeff.copy()

    def step(self):
        self._coeff -= self._gamma*self._gradient()
        self._update_superposition()
    
    def run(self, steps):
        for n in range(steps):
            self.step()

    def get_approximation(self):
        return self._buffer.copy()/self._norm
        
    # internal 'private' functions
    def _update_superposition(self, idx: int = None, delta: complex = None):

        if idx is None and delta is None:

            self._buffer.fill(0+0j)

            for c, vec in zip(self._coeff, self._vectors):
                self._buffer += c*vec

        elif not (idx is None) and not (delta is None):

            self._buffer += self._vectors[idx,:]*delta
            self._coeff[idx] += delta

        else:

            raise ValueError('One should specify both \'idx\' and \'delta\' arguments.')
            
        self._norm = np.linalg.norm(self._buffer)
        
        
    def _initialize_random_coefficients(self):

        gen = np.random.default_rng()
        self._coeff = np.ndarray((self._total_vectors,), complex)
        self._coeff.real = gen.random((self._total_vectors,))
        self._coeff.imag = gen.random((self._total_vectors,))

    def _validate_coefficients(self, coefficients):

        if self._total_vectors != coefficients.shape[0]:
            raise ValueError('Length of coefficients array does not correspond to number of used vectors. Check the input data consistency.')

    def _gradient(self):

        result = np.zeros((self._total_vectors,), complex)

        e0 = self.overlap()

        for idx, vec in enumerate(self._vectors):

            self._update_superposition(idx, self._delta)
            e1 = self.overlap()

            result[idx] = (e1-e0)/self._delta

            self._update_superposition(idx, -self._delta + self._delta*1j)
            e1 = self.overlap()

            result[idx] += 1j*(e1-e0)/self._delta

            self._update_superposition(idx, -self._delta*1j)

        return result
