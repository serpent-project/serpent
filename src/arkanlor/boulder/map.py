#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

Copyright (C) 2012 by  Gabor Guzmics, <gab(at)g4b(dot)org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''
import math, random
from uolib1 import map

N = (0, -1)
S = (0, 1)
E = (1, 0)
W = (-1, 0)

MAX_RANDOM = 500

TILE_ANY = -1
TILE_NONE = 0
TILE_VOID = 1
TILE_NODRAW = 2
TILE_DIRT = 3
TILE_GRASS = 4 # grassland default.
TILE_FOREST = 5 # forest default.
TILE_WATER = 6 # water default.
TILE_LAVA = 7
TILE_ROCK = 8

CONSOLE_MAP = {
        TILE_ANY: '*',
        TILE_NONE: '0',
        TILE_NODRAW: ' ',
        TILE_VOID: 'x',
        TILE_DIRT: 'o',
        TILE_GRASS: '.',
        TILE_FOREST: ':',
        TILE_WATER: '~',
        TILE_LAVA: '″',
        TILE_ROCK: '@',
               }

class MapLoader(object):
    def fill(self, x, y, mapcell):
        pass

class RandomLoader(MapLoader):
    def fill(self, x, y, mapcell):
        def valid_art():
            art_id = None
            while get_tile_from_art(art_id) == TILE_ANY:
                art_id = random.randint(2, MAX_RANDOM)
            return art_id
        # we dont really care.
        mapcell._art = valid_art()
        mapcell._tile = get_tile_from_art(mapcell._art)
        mapcell.z = random.randint(0, 22) / 10

class UOLoader(MapLoader):
    map = None
    def __init__(self, map):
        self.map = map

    def fill(self, x, y, mapcell):
        try:
            mapcell._art, mapcell.z = self.map.get_cell(x, y)
        except:
            mapcell._art, mapcell.z = 0, 0
        mapcell._tile = get_tile_from_art(mapcell._art)


def initiliaze_area(maploader, topleft, bottomright):
    x1, y1 = topleft
    x2, y2 = bottomright
    # we initialize the topleft area completely
    source = MapArea()
    source.empty_cells(topleft)
    print source.myzero
    # now we initialize the parent for topleft, completely.
    parent_x, parent_y = source.myzero[0] / 8, source.myzero[1] / 8
    parent = MapArea()
    print parent.myzero
    for y in xrange(8):
        for x in xrange(8):
            a = MapArea(parent)
            a.empty_cells(pos=(parent_x * x, parent_y * y))
            a.load(maploader)
            parent.children[x, y] = a
    return parent


def get_tile_from_art(art_id):
    """
        a specific map art has which kind of tile?
    """
    if art_id:
        if not art_id:
            return TILE_NONE
        elif art_id == 1:
            return TILE_VOID
        elif art_id == 2:
            return TILE_NODRAW
        elif art_id in range(9, 22):
            return TILE_DIRT
        elif art_id in range(3, 7):
            return TILE_GRASS
        elif art_id in range(168, 172) + [310, 311]:
            return TILE_WATER
        elif art_id in range(500, 505):
            return TILE_LAVA
    return TILE_ANY

class MapCell:
    _ch = '*'
    _items = None # items on this mapcell.
    _color = 0 # colored textures may be supported
    _tile = 0 # tile id - which type of mapcell is this?
    _art = 0 # art id - "map color" in uo.
    _z = 0.0
    _flags = 0

    def __init__(self, art=None, z=None):
        self._items = []
        self._color = 0
        self._art = art or 0
        self._tile = get_tile_from_art(art)
        self._z = z or 0.0

    def get_items(self):
        return self._items

    def set_items(self, items):
        self._items = items
    items = property(get_items, set_items)

    def item_count(self):
        if self._items:
            return len(self._items)
        return 0

    def get_z(self):
        return int(math.floor(self._z))

    def set_z(self, value):
        self._z = value
    z = property(get_z, set_z)
    zreal = property(lambda x: x._z, set_z)

    def get_ch(self):
        if self.item_count():
            # check if i got a specific item to display
            return '#'
        if self._tile:
            return CONSOLE_MAP.get(self._tile, self._ch)
        else:
            return self._ch
    ch = property(get_ch)

    def get_flags(self):
        return self._flags
    def set_flags(self, flags):
        self._flags = flags
    flags = property(get_flags, set_flags)
    walkable = property(lambda x: x.flags & 0x1,
                        lambda x, y: x.set_flags(x._flags | 0x01)) # basic flag.

class _NullMapCell(MapCell):
    _ch = '0'
    def set_items(self, items):
        pass
    def set_z(self, value):
        pass

NullMapCell = _NullMapCell()
NullMapArea = None

class CellReader(list):
    def __init__(self, area):
        self.area = area

    def get_rect(self, x1, y1, x2, y2):
        return []

class MapArea:
    """
        A map area governs a rectangular space of mapcells.
        It can be itself built by multiple mapareas.        
    """
    parent = None
    children = None
    _cells = None
    myzero = (0, 0)
    mymax = (8, 8)
    index = 0 # index in parents children.

    def __init__(self, parent=None):
        self.parent = parent
        self.children = {}

    def empty_cells(self, pos=None):
        # create myself as being a cellholder.
        if not self._cells:
            self._cells = {}
        for y in xrange(8):
            for x in xrange(8):
                self._cells[x, y] = MapCell()
        if pos:
            # you want be to be cellholder for a position.
            # i will always assume i am responsible for the 8*8 block containing that position.
            self.myzero = (pos[0] - pos[0] % 8,
                           pos[1] - pos[1] % 8)
            self.mymax = (pos[0] - pos[0] % 8 + 8,
                           pos[1] - pos[1] % 8 + 8)

    def load(self, maploader):
        # loads a map from a maploader
        # we assume the maploader reads absolute x, y
        for y in xrange(8):
            for x in xrange(8):
                try:
                    maploader.fill(self.myzero[0] + x, self.myzero[1] + y, self._cells[x, y])
                except:
                    raise

    def ascii_map(self):
        ret = []
        if self._cells:
            for y in xrange(8):
                ret += [ '%s' * 8 % tuple([self._cells[x, y].ch for x in xrange(8)])]
        elif self.children:
            # get the return value of all children and concat it to a big ret
            for y in xrange(8):
                lines = ['' for i in xrange(8)]
                for x in xrange(8):
                    child = self.children.get((x, y), NullMapArea)
                    child_map = child.ascii_map()
                    for y2 in xrange(8):
                        lines[y2] += child_map[y2]
                ret += [lines]
        return ret

    def get_cells(self):
        if self._cells:
            return self._cells
        else:
            return CellReader(self)

    def neighbour(self, dir=None):
        if dir:
            x, y = dir
            # now look up if this neighbour is my parents'
            rx, ry = self.myzero[0] + x, self.myzero[1] + y
            # check for my parent
            if not self.parent:
                # parents are created here if neccessary.
                return NullMapArea
            if (rx >= 0) and (ry >= 0) and (rx < 8) and (ry < 8):
                # if yes, its done, just ask my parent for it.
                pass
            else:
                # if this neighbour is not even my parents job, i ask my parent for a neighbour to deliver it.
                # 
                pass
        # or i just return nullmaps.
        return NullMapArea

class _NullMapArea(MapArea):
    def __init__(self, parent=None):
        self._cells = {}
        for y in xrange(8):
            for x in xrange(8):
                self._cells[x, y] = NullMapCell

NullMapArea = _NullMapArea()

if __name__ == '__main__':
    x = 660
    y = 1027
    my_map = map.MapCacheSingular('/home/g4b/Spiele/Alathair/map0.ala')
    print my_map.get_block(x / 8, y / 8)
    maparea = initiliaze_area(UOLoader(my_map), (x, y), (x + 63, y + 63))

    for i in maparea.ascii_map():
        if isinstance(i, list):
            for z in i:
                print z
        else:
            print i


