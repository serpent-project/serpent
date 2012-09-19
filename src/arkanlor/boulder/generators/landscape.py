from arkanlor.boulder.map import Map, MapSync, SHAPE_X, SHAPE_Y, BLOCK_SHAPE
from arkanlor.misc.geology import MidpointDisplacementNoise, PerlinNoise, \
    CombineNeighbours, Voronoi, WhiteNoise
from arkanlor.boulder.generators import biomes
import numpy
from arkanlor.boulder.generators.continents import ContinentManager, \
    ExampleContinent
from arkanlor.boulder.generators.dragonmap import SimpleDragonContinent, \
    dragon_scripts

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
        self.continents = ContinentManager()
        self.continents.register_continent(ExampleContinent((1024, 16), 10, 1))
        self.continents.register_continent(SimpleDragonContinent((8, 8), 1, 1))
        if not sync:
            sync = BiomeMapSync(self)
        super(BiomeMap, self).__init__(parent, size, sync)

    def get_biome(self, block):
        return self.continents.get_biome(block)

    def block_postprocess(self, block):
        """
            we wake up our neighbours.
            we apply dragon filters automagically.
            note: this should be a continental thing
        """
        if not block.processed:
            self.get_all_neighbours(block, wake_up=True)
            dragon_scripts.apply(block, levels=[0, 1, 2, 3, 4])
            block.processed = True
