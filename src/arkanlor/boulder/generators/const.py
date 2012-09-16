# -*- coding: utf-8 -*-

class UOTiles:
    water = [0xa8 + x for x in xrange(4)]
    water_deep = [0x136, 0x137]
    grass = [0x3 + x for x in xrange(3)]
    rock = [0x22c + x for x in xrange(3)]
    sand = [0x16 + x for x in xrange(4)]
    dirt = [0x75 + x for x in xrange(4)]
    dirt_stones = [0x71 + x for x in xrange(4)]
    grass_murky = [x for x in range(0x9c4, 0x9eb)]
    snow = [x for x in range(0x11a, 0x11d)]

