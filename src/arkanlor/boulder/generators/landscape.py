from arkanlor.boulder.map import Map, MapSync, SHAPE_X, SHAPE_Y, BLOCK_SHAPE
from arkanlor.misc.geology import MidpointDisplacementNoise, PerlinNoise, \
    CombineNeighbours
from arkanlor.boulder.generators import biomes
import numpy

class BiomeMapSync(MapSync):
    def load_block(self, mapblock):
        # we get the combined neighbours
        east, north, south, west = mapblock.parent.get_neighbours(mapblock)
        if east or north or south or west:
            if east:
                east = east.heights
            if north:
                north = north.heights
            if south:
                south = south.heights
            if west:
                west = west.heights
            z = numpy.zeros(BLOCK_SHAPE)
            z = CombineNeighbours(z, east, north, south, west)
            height_map = numpy.square(self.parent.height_noise(BLOCK_SHAPE, z=z).smooth4().normalize().z)
        else:
            height_map = numpy.square(self.parent.height_noise(BLOCK_SHAPE).smooth4().normalize().z)
        tile_map = MidpointDisplacementNoise(BLOCK_SHAPE).normalize().z
        # get my biome.
        self.parent.get_biome(mapblock).apply(mapblock, height_map, tile_map)

class BiomeMap(Map):
    def __init__(self, parent,
                 size=None,
                 sync=None,
                 height_noise=MidpointDisplacementNoise,
                 tile_noise=None,
                 sea_level=0.2,
                 ):
        self.height_noise = height_noise
        self.tile_noise = tile_noise
        self.sea_level = sea_level
        self.biomes = {}
        if not sync:
            sync = BiomeMapSync(self)
        super(BiomeMap, self).__init__(parent, size, sync)

    def get_biome(self, block):
        # heh.
        bbx = int(numpy.floor(block.bx / 8.0))
        bby = int(numpy.floor(block.by / 8.0))
        brx = block.bx % 8
        bry = block.by % 8
        try:
            biomemap = self.biomes[bbx, bby]
        except KeyError:
            # create a new biome map.
            biomemap = []
            noise = MidpointDisplacementNoise((8, 8)).normalize()
            for x in xrange(8):
                row = []
                for y in xrange(8):
                    row += [ biomes.get_biome(noise.z[x, y]) ]
                biomemap += [row]
            self.biomes[bbx, bby] = biomemap
        return biomemap[brx][bry]


