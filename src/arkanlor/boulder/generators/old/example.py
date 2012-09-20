"""
    The "Example" Generator, or "8x8x8-method"
"""
import numpy
from arkanlor.boulder.generators.biomes import Biome
from arkanlor.boulder.generators.utils import select_tile, select_tile_linear
from arkanlor.boulder.generators.const import UOTiles
from arkanlor.boulder.generators.continents import Continent
from arkanlor.misc.geology import MidpointDisplacementNoise, Voronoi

class DeepSea(Biome):
    def apply_cell(self, mapblock, rx, ry, hf, tf):
        if hf < 0.1:
            mapblock.tiles[rx, ry] = select_tile(UOTiles.water_deep, tf)
            mapblock.heights[rx, ry] = self.height
        else:
            # water normal.
            mapblock.tiles[rx, ry] = select_tile(UOTiles.water, tf)
            mapblock.heights[rx, ry] = self.height

class ShallowSea(Biome):
    def apply_cell(self, mapblock, rx, ry, hf, tf):
        if hf < 0.1:
            mapblock.tiles[rx, ry] = select_tile(UOTiles.water_deep, tf)
            mapblock.heights[rx, ry] = self.height
        elif hf < 0.94:
            # water normal.
            mapblock.tiles[rx, ry] = select_tile(UOTiles.water, tf)
            mapblock.heights[rx, ry] = self.height
        else:
            mapblock.tiles[rx, ry] = select_tile(UOTiles.sand, tf)
            mapblock.heights[rx, ry] = self.height + int(hf * 2)

class Coastal(Biome):
    def apply_cell(self, mapblock, rx, ry, hf, tf):
        if hf < 0.2:
            # water normal.
            mapblock.tiles[rx, ry] = select_tile(UOTiles.water, tf)
            mapblock.heights[rx, ry] = self.height
        elif hf < 0.4:
            # sandcoast
            mapblock.tiles[rx, ry] = select_tile(UOTiles.sand, tf)
            mapblock.heights[rx, ry] = self.height + int(hf * 8)
        else:
            # grass or dirt or smth
            mapblock.tiles[rx, ry] = select_tile(UOTiles.grass, tf)
            mapblock.heights[rx, ry] = self.height + int(hf * 8)

class GrassLand(Biome):
    def apply_cell(self, mapblock, rx, ry, hf, tf):
        # grass or dirt or smth
        mapblock.tiles[rx, ry] = select_tile(UOTiles.grass, tf)
        mapblock.heights[rx, ry] = self.height + int(hf * 8)

class MurkyGrassLand(Biome):
    def apply_cell(self, mapblock, rx, ry, hf, tf):
        # grass or dirt or smth
        if hf < 0.4:
            mapblock.tiles[rx, ry] = select_tile(UOTiles.grass_murky, tf)
            mapblock.heights[rx, ry] = self.height + int(hf * 8)
        else:
            mapblock.tiles[rx, ry] = select_tile(UOTiles.grass, tf)
            mapblock.heights[rx, ry] = self.height + int(hf * 8)

class Forest(Biome):
    def apply_cell(self, mapblock, rx, ry, hf, tf):
        # grass or dirt or smth
        if hf < 0.8:
            mapblock.tiles[rx, ry] = select_tile(UOTiles.forest, tf)
            mapblock.heights[rx, ry] = self.height + int(hf * 8)
        else:
            mapblock.tiles[rx, ry] = select_tile(UOTiles.grass, tf)
            mapblock.heights[rx, ry] = self.height + int(hf * 8)

class Rocks(Biome):
    def apply_cell(self, mapblock, rx, ry, hf, tf):
        if hf < 0.05:
            mapblock.tiles[rx, ry] = select_tile(UOTiles.grass, tf)
            mapblock.heights[rx, ry] = self.height + int(hf * 8)
        elif hf < 0.25:
            # dirt
            mapblock.tiles[rx, ry] = select_tile(UOTiles.dirt, tf)
            mapblock.heights[rx, ry] = self.height + int(hf * 8)
        elif hf < 0.4:
            # rocksides
            mapblock.tiles[rx, ry] = select_tile(UOTiles.dirt_stones, tf)
            mapblock.heights[rx, ry] = self.height + int(hf * 8) + 2
        else:
            mapblock.tiles[rx, ry] = select_tile(UOTiles.rock, tf)
            mapblock.heights[rx, ry] = self.height + int(hf * 16) + 6

class HighLands(Biome):
    def apply_cell(self, mapblock, rx, ry, hf, tf):
        if hf < 0.15:
            # dirt
            mapblock.tiles[rx, ry] = select_tile(UOTiles.dirt, tf)
            mapblock.heights[rx, ry] = self.height + int(hf * 8) + 5
        elif hf < 0.3:
            # rocksides
            mapblock.tiles[rx, ry] = select_tile(UOTiles.dirt_stones, tf)
            mapblock.heights[rx, ry] = self.height + int(hf * 8) + 6
        else:
            mapblock.tiles[rx, ry] = select_tile(UOTiles.rock, tf)
            mapblock.heights[rx, ry] = self.height + int(hf * 16) + 12

class Mountains(Biome):
    def apply_cell(self, mapblock, rx, ry, hf, tf):
        if hf < 0.5:
            mapblock.tiles[rx, ry] = select_tile(UOTiles.rock, tf)
            mapblock.heights[rx, ry] = self.height + int(hf * 16) + 12
        else:
            mapblock.tiles[rx, ry] = select_tile(UOTiles.snow, tf)
            mapblock.heights[rx, ry] = self.height + int(hf * 16) + 13


# used to scatter biomes themselves.
default_biomes = [
        # range, biomeclass
        (0.0, 0.1, DeepSea()),
        (0.1, 0.25, Coastal()),
        (0.25, 0.7, GrassLand()),
        (0.7, 1.1, Rocks()),
          ]

def get_biome_by_range(f, biomes=default_biomes):
    for biome in biomes:
        lo, hi, b = biome
        if f >= lo and (f < hi):
            return b
    return Biome()


class ExampleContinent(Continent):
    """
        defining a global midpoint noisemap for 8x8 continent blocks,
        this continent returns voronoi based subcontinent types.
        you can use this continent up to 8x8x8 width / height (4096x4096)
    """
    def initialize(self, **kwargs):
        # we use this noise to populate our layout types.
        self.noise = MidpointDisplacementNoise((int(numpy.ceil(self.width / 8)),
                                                int(numpy.ceil(self.height / 8)))
                                               ).normalize().z

    def layout_type(self, brx, bry):
        # this generates our layout types.
        cx, cy = int(brx / 8), int(bry / 8)
        return select_tile_linear([
        # waterland
        [   (0.0, 0.9, DeepSea()),
            (0.9, 0.95, ShallowSea()),
            (0.95, 1.1, Coastal()),
        ],
        # green lands
        [   (0.0, 0.02, DeepSea()),
            (0.02, 0.05, ShallowSea()),
            (0.05, 0.15, Coastal()),
            (0.15, 1.1, GrassLand()),
        ],
        # murky green lands
        [
            (0.00, 0.02, ShallowSea()),
            (0.02, 0.04, Coastal()),
            (0.04, 0.7, MurkyGrassLand()),
            (0.7, 1.1, GrassLand()),
        ],
        [   (0.0, 0.4, GrassLand()),
            (0.4, 1.1, Forest()),
        ],
        [   (0.0, 0.4, GrassLand()),
            (0.4, 1.1, Forest()),
        ],
        # rocky lands
        [   (0.0, 0.4, GrassLand(10)),
            (0.4, 0.9, Rocks(10)),
            (0.9, 0.95, Mountains(10)),
            (0.95, 1.1, Mountains(20)),
        ],
        # highlands
        [   (0.0, 0.3, Rocks(10)),
            (0.3, 0.4, HighLands(10)),
            (0.4, 0.6, Mountains(35)),
            (0.6, 0.9, Mountains(40)),
            (0.9, 1.1, Mountains(50)),
        ], ],
        self.noise[cx, cy])

    def resolve_biome(self, brx, bry):
        """ builds another 8x8 voronoi block.
        """
        noise = Voronoi((8, 8)).normalize()
        start_x, start_y = (brx - (brx % 8)), (bry - (bry % 8))
        for x in xrange(8):
            for y in xrange(8):
                self.biomes[start_x + x,
                            start_y + y] = get_biome_by_range(noise.z[x, y], self.layout_type(brx, bry))
        return self.biomes[brx, bry]
