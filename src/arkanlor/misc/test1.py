import numpy, random
from brownian import brownian
numpy.random.seed([1, 2, 3, ])
random.seed([1, 2, 3, ])

# The Wiener process parameter.
delta = 0.2
# Total time.
T = 10.0
# Number of steps.
N = 500
# Time step size
dt = T / N
# Initial values of x.
#x = numpy.empty((2, N + 1))
x = numpy.zeros((8, N + 1))

x[:, 0] = 0.0
d = brownian(x[:, 0], N, dt, delta, out=x[:, 1:])
