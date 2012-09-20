# -*- coding: utf-8 -*-

"""
    Lets create an endless grassland with flowers n stuff.
"""
from arkanlor.boulder.generators.continents import Continent
from arkanlor.boulder.generators.biomes import Biome
from arkanlor.boulder.generators.utils import select_tile
from arkanlor.boulder.generators.const import UOTiles

class Grassy(Biome):
    def apply_cell(self, mapblock, rx, ry, hf, tf):
        # grass!
        mapblock.tiles[rx, ry] = select_tile(UOTiles.grass, tf)
        mapblock.heights[rx, ry] = int(hf * 6)
        # now we place statics?

class EndlessGrass(Continent):
    def resolve_biome(self, brx, bry):
        return Grassy()
