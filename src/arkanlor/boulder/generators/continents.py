# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    Continents
    
    Continents allow an arbitrary sized Matrix to be created, building
    islands and base displacement of natural phenomena.
    
    Continents work in mapblock coordinates, that is, they assume every
    dot on a continent is 8x8 size.

@author: g4b

LICENSE AND COPYRIGHT NOTICE:

Copyright (C) 2012 by  Gabor Guzmics, <gab(at)g4b(dot)org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""
from arkanlor.boulder.generators import biomes
from arkanlor.misc.geology import MidpointDisplacementNoise, Voronoi
from arkanlor.boulder.generators.biomes import select_tile, DeepSea, \
    ShallowSea, Coastal, GrassLand, MurkyGrassLand, Rocks, Mountains, \
    HighLands
from arkanlor.boulder.map import uomap
import numpy

class ContinentManager:
    def __init__(self, DefaultContinent=None):
        if DefaultContinent is None:
            # take Blackness as default continent
            DefaultContinent = DefaultBlackness
        if isinstance(DefaultContinent, Continent):
            self.default = DefaultContinent
        else:
            self.default = DefaultContinent((0, 0))
        self.continents = []

    def get(self, bx, by):
        # get the continent responsible for bx, by
        for continent in self.continents:
            if continent.feel_responsible(bx, by):
                return continent
        return self.default

    def get_biome(self, mapblock):
        return self.get(mapblock.bx, mapblock.by).get_biome(mapblock)

    def register_continent(self, continent, x=0, y=0):
        self.continents += [continent]

class Continent:
    def __init__(self, shape, offset_x=0, offset_y=0, **kwargs):
        self.shape = shape
        self.width, self.height = shape
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.max_x = self.offset_x + self.width
        self.max_y = self.offset_y + self.height
        self.biomes = {} # biome cache.
        self.noise = None # free to use.
        self.initialize(**kwargs)

    def initialize(self, **kwargs):
        """ your chance to prepopulate the continent, create global
            noisemaps etc. """
        pass

    def feel_responsible(self, bx, by):
        return (bx >= self.offset_x) and (by >= self.offset_y) and\
               (bx < self.max_x) and (by < self.max_y)

    def get_biome(self, mapblock):
        # get a biome.
        bx, by = mapblock.bx, mapblock.by
        brx, bry = bx - self.offset_x, by - self.offset_y
        try:
            return self.biomes[brx, bry]
        except KeyError:
            return self.resolve_biome(brx, bry)

    def resolve_biome(self, brx, bry):
        """ local block coordinates generate your biome here.
            if you dont save it to your local cache, this will be called
            every time.
        """
        biome = biomes.Blackness()
        self.biomes[brx, bry] = biome
        return biome


class Blackness(Continent):
    """ returns blackness """
    pass

class DefaultBlackness(Blackness):
    """ this continent feels always responsible and returns blackness """
    def feel_responsible(self, bx, by):
        return True

class TiledContinents(Continent):
    """ this continent tiles 8x8 continents        
    """
    pass

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
        return select_tile([
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
        # rocky lands
        [   (0.0, 0.4, GrassLand()),
            (0.4, 1.1, Rocks()),
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

    def build_biome_map(self, brx, bry):
        noise = Voronoi((8, 8)).normalize()
        start_x, start_y = (brx - (brx % 8)), (bry - (bry % 8))
        for x in xrange(8):
            for y in xrange(8):
                self.biomes[start_x + x,
                            start_y + y] = biomes.get_biome_by_range(noise.z[x, y], self.layout_type(brx, bry))
        return self.biomes[brx, bry]

    def resolve_biome(self, brx, bry):
        """ builds another 8x8 voronoi block.
        """
        return self.build_biome_map(brx, bry)

class UOBiome(biomes.Biome):
    ___slots__ = ['mapmul', 'bx', 'by']
    def __init__(self, mapmul=None, bx=0, by=0):
        self.mapmul = mapmul
        self.bx = bx
        self.by = by
    def apply(self, mapblock, height_map=None, tile_map=None):
        uoblock = self.mapmul.get_block(self.bx, self.by)
        for x in xrange(8):
            for y in xrange(8):
                c = uoblock.get_cell(x, y)
                mapblock.tiles[x, y] = c[0]
                mapblock.heights[x, y] = c[1]

class UOContinent(Continent):
    def initialize(self, **kwargs):
        self.uo_map_offset_x = kwargs.get('map_offset_bx', 0)
        self.uo_map_offset_y = kwargs.get('map_offset_by', 0)
        self.noise = uomap.MapCacheSingular(kwargs.get('mapmul'))

    def resolve_biome(self, brx, bry):
        brx += self.uo_map_offset_x
        bry += self.uo_map_offset_y
        return UOBiome(self.noise, brx, bry)

