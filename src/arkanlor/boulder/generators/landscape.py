from arkanlor.boulder.map import Map, MapSync, SHAPE_X, SHAPE_Y, BLOCK_SHAPE
from arkanlor.misc.geology import MidpointDisplacementNoise, PerlinNoise, \
    CombineNeighbours, Voronoi, WhiteNoise
from arkanlor.boulder.generators import biomes
import numpy
from arkanlor.boulder.generators.biomes import Continent

class BiomeMapSync(MapSync):
    def load_block(self, mapblock):
        # we get the combined neighbours
        east, north, south, west = mapblock.parent.get_neighbours(mapblock)
        if east or north or south or west:
            if east:
                east = east.height_map
            if north:
                north = north.height_map
            if south:
                south = south.height_map
            if west:
                west = west.height_map
            z = numpy.zeros(BLOCK_SHAPE)
            z = CombineNeighbours(z, east, north, south, west)
            mapblock.height_map = numpy.square(self.parent.height_noise(BLOCK_SHAPE, z=z).smooth4().normalize().z)
        else:
            mapblock.height_map = numpy.square(self.parent.height_noise(BLOCK_SHAPE).smooth4().normalize().z)
        mapblock.tile_map = self.parent.tile_noise(BLOCK_SHAPE).smooth().z

        # get my biome.
        self.parent.get_biome(mapblock).apply(mapblock)

class BiomeMap(Map):
    def __init__(self, parent,
                 size=None,
                 sync=None,
                 height_noise=MidpointDisplacementNoise,
                 tile_noise=WhiteNoise,
                 sea_level=0.2,
                 ):
        self.height_noise = height_noise
        self.tile_noise = tile_noise
        self.sea_level = sea_level
        self.biomes = {}
        self.continents = {}
        if not sync:
            sync = BiomeMapSync(self)
        super(BiomeMap, self).__init__(parent, size, sync)

    def get_continent(self, bbx, bby):
        cx = int(numpy.floor(bbx / 8.0))
        cy = int(numpy.floor(bby / 8.0))
        c = self.continents.get((cx, cy), None)
        if c is None:
            c = Continent()
            self.continents[cx, cy] = c
        return c

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
            biomemap = self.get_continent(bbx, bby).build_biome_map(bbx, bby)
            self.biomes[bbx, bby] = biomemap
        return biomemap[brx][bry]


