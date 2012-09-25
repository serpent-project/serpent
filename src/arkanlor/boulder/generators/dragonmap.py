# -*- coding: utf-8 -*-
"""
    A Map using height noise to identify the item via dragon.maptrans
    And the tile noise to select items from it.
    
"""
from arkanlor.boulder.generators.biomes import Biome
from django.conf import settings
from arkanlor.dragons.dragon import DragonScripts
from arkanlor.boulder.generators.continents import Continent
from arkanlor.boulder.generators.utils import select_tile, select_tile_linear
from arkanlor.dragons.default import dragon_scripts

class SimpleDragonBiome(Biome):
    """ a simple biome that interpretes everything as dragon map bytes """
    def apply_cell(self, mapblock, rx, ry, hf, tf):
        # convert our hf to a hex.
        # dragon_scripts.groups.get_group_list() # funny
        group = select_tile_linear([2, 5] + [ 0, ] * 15 + [1, 1, 0xa, 0xa], hf)
        alt = int(hf * 10) # grass + forest
        tileg = dragon_scripts.groups.get_by_groupalt(group, alt)
        if tileg is None:
            mapblock.tiles[rx, ry] = 0x2
            mapblock.heights[rx, ry] = 0
        else:
            mapblock.tiles[rx, ry] = select_tile(tileg.tiles, tf)
            mapblock.heights[rx, ry] = tileg.alt

class SimpleDragonContinent(Continent):
    def get_biome(self, mapblock):
        try:
            biome = self.biomes[None]
        except KeyError:
            # create a new biome map.
            biome = SimpleDragonBiome()
            self.biomes[None] = biome
        return biome
