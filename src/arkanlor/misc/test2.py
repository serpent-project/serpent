import numpy, random
from geology import *

def set_seed(something):
    a = [ord(i) for i in something]
    numpy.random.seed(a)
    random.seed(something)

SEED = 'weltenfall'
R = 64
SHAPE = (64, 64) # required to be powers of 2 when wrapping
CLEVEL = 0.25

set_seed(SEED)


Noise = MidpointDisplacementNoise
examples = image(

        numpy.square(Noise(SHAPE).normalize().z),
                #numpy.concatenate(
                #            (
                #            Noise(SHAPE).normalize().z,
                #            Noise(SHAPE).normalize().z,
                #            
                #            ),
                #            axis=1#

#                                  ),
   #numpy.concatenate(
   #                  (x.z,
   #                   x.copy().smooth().z,
   #                   x.copy().thermally_erode(0.02, 0.5, True).z,
   #                   Terrain(data=x.slope_map()).normalize().z,
   #                   numpy.square(x.copy().normalize().z),
   #                   x.copy().distort_fractally().z),
   #                  axis=1)
   geographic_palette())

#examples.save("%s.png" % (SEED.lower(),))
examples.show()
