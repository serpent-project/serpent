# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    SimpleMap

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
import numpy
from uolib1 import map as uomap
from django.conf import settings

SHAPE_X = 8
SHAPE_Y = 8
FSHAPE_X = float(SHAPE_X)
FSHAPE_Y = float(SHAPE_Y)
BLOCK_SHAPE = (SHAPE_X, SHAPE_Y)

class MapSync(object):
    """ object that is capable of loading and saving blocks somehow. """
    def __init__(self, parent):
        self.parent = parent
    def load_block(self, mapblock):
        pass
    def save_block(self, mapblock):
        pass

class RandomGrassSync(MapSync):
    def load_block(self, mapblock):
        for rx in xrange(SHAPE_X):
            for ry in xrange(SHAPE_Y):
                mapblock.tiles[rx, ry] = 0x3 + numpy.random.randint(0, 3)
                mapblock.heights[rx, ry] = 2 + numpy.random.randint(0, 3)

class StaticItem(object):
    __slots__ = ['parent', 'art', 'rx', 'ry', 'z', 'color']
    def __init__(self, parent, art, rx, ry, z=0, color=0):
        self.parent = parent
        self.art = art
        self.rx = rx
        self.ry = ry
        self.z = z
        self.color = color
    def packet_info(self):
        return {'rx': self.rx,
                'ry': self.ry,
                'z': self.z,
                'color': self.color,
                'art': self.art
                }

class MapBlock:
    # defines a walkable grid
    def __init__(self, parent,
                 offset_x=0, # bx * 8
                 offset_y=0, # by * 8
                 header=0):
        # parenting
        self.parent = parent
        # positions
        if not offset_x % SHAPE_X:
            offset_x = offset_x - offset_x % SHAPE_X
        if not offset_y % SHAPE_Y:
            offset_y = offset_y - offset_y % SHAPE_Y
        self.header = header or 0
        self.offset_x, self.offset_y = offset_x, offset_y
        self.bx, self.by = self.offset_x / SHAPE_X, self.offset_y / SHAPE_Y
        # mapdata
        self.flags = numpy.zeros(BLOCK_SHAPE, dtype=int) # flag matrix
        self.tiles = numpy.zeros(BLOCK_SHAPE, dtype=int) # tile matrix.
        self.heights = numpy.zeros(BLOCK_SHAPE, dtype=int) # heightmap
        self.groups = numpy.zeros(BLOCK_SHAPE, dtype=int) # groups
        # noises:
        self.height_map = None
        self.tile_map = None
        # statics
        self.clear_statics()
        # syncing
        self._synced = None
        self.sync()

    def clear_statics(self):
        self.statics = [ [[] for x in xrange(8)] for y in xrange(8)] # 8x8

    def has_static(self, x, y, static=None):
        if static is not None:
            for item in self.statics[x % 8][y % 8]:
                if item.art == static.art:
                    return True
            return False
        else:
            return len(self.statics[x % 8][y % 8]) > 0

    def add_static(self, x, y, static):
        self.statics[x % 8][y % 8] += [static]

    def _sync(self):
        """ Override this to write your custom sync method.
            Note, it does not have to return a new _synced,
            but if it does return None, parent._sync is taken.
            
        """
        self.parent.sync.load_block(self)
        return self.parent._sync

    def sync(self):
        """ syncs this mapblock.
            This might involve reading from the database
            or generating custom terrain
            or loading from a mapfile
            override with _sync
            self.parent is accessed.
        """
        if self._synced != self.parent._sync:
            self._synced = self._sync()
            if not self._synced:
                self._synced = self.parent._sync


    def enum_flag(self, rx, ry):
        """ enumerates the flag at a subtile. """
        pass

    def get_cells(self):
        return [ {'tile': int(self.tiles[x, y]), 'z': int(self.heights[x, y])}
                 for y in xrange(SHAPE_Y) for x in xrange(SHAPE_X)
                 ]

    def get_statics_linear(self):
        ret = []
        for y in xrange(8):
            for x in xrange(8):
                ret += self.statics[x][y]
        return ret

    def _statics_packet_info(self):
        ret = []
        lin = self.get_statics_linear()
        for l in lin:
            ret += [l.packet_info()]
        return ret

    def packet_info(self):
        return {
                'bx': self.bx,
                'by': self.by,
                'cells': self.get_cells(),
                'statics': self._statics_packet_info()
                }


class Map(object):
    def __init__(self, parent, size=settings.DEFAULT_MAP0_SIZE, sync=None):
        self.parent = parent
        self.width, self.height = size
        self.blocks_x, self.blocks_y = numpy.ceil(self.width / FSHAPE_X), numpy.ceil(self.height / FSHAPE_Y)
        self.blocks = {}
        self._sync = 0
        self.sync = sync or RandomGrassSync(self)

    def _bi(self, x, y):
        """ block index """
        return (numpy.floor(x / FSHAPE_X), numpy.floor(y / FSHAPE_Y))

    def _rel(self, x, y):
        """ relative block coordinates """
        return (x % SHAPE_X, y % SHAPE_Y)

    def get_neighbours(self, block):
        # returns the neighbours (diamond)
        # ensw
        east, north, south, west = None, None, None, None
        bx, by = block.bx, block.by
        # east
        if bx < self.blocks_x - 1:
            east = self.get_block_or_none(bx + 1, by)
        if by > 0:
            north = self.get_block_or_none(bx, by - 1)
        if by < self.blocks_y - 1:
            south = self.get_block_or_none(bx, by + 1)
        if bx > 0:
            west = self.get_block_or_none(bx - 1, by)
        return (east, north, south, west)

    def get_blocks16(self, x, y):
        b16x = (x - x % 16) / 16
        b16y = (y - y % 16) / 16
        bx = b16x * 2
        by = b16y * 2
        # need to verify constraints here!
        mb1 = self.get_block(bx, by)
        mb2 = self.get_block(bx + 1, by)
        mb3 = self.get_block(bx, by)
        mb4 = self.get_block(bx + 1, by + 1)
        return (mb1, mb2, mb3, mb4)

    def block(self, x, y):
        """
            access the block at x and y. 
        """
        bx, by = self._bi(x, y)
        return self.get_block(bx, by)

    def get_block(self, bx, by):
        """
            access the block at Bx By
        """
        try:
            return self.blocks[bx, by]
        except KeyError:
            block = MapBlock(self, bx * SHAPE_X, by * SHAPE_Y)
            self.blocks[bx, by] = block
            return block

    def get_block_or_none(self, bx, by):
        try:
            return self.blocks[bx, by]
        except KeyError:
            return None

    def walkable(self, x, y):
        return self.block(x, y).matrix[self._rel(x, y)] == 0x0

    def block_size(self):
        # returns map size in blocks
        return (self.blocks_x, self.blocks_y)
    def size(self):
        return (self.width, self.height)
    def bounds(self):
        return (0, 0, self.width, self.height)
    def info(self):
        return "Map (width=%s, height=%s)" % self.size()

class UOMapSync(MapSync):
    """
        syncs a uo map.
    """
    def load_block(self, mapblock):
        uoblock = self.parent.mapmul.get_block(mapblock.bx, mapblock.by)
        for x in xrange(SHAPE_X):
            for y in xrange(SHAPE_Y):
                c = uoblock.get_cell(x, y)
                mapblock.tiles[x, y] = c[0]
                mapblock.heights[x, y] = c[1]

    def save_block(self, mapblock):
        pass

class UOMap(Map):
    def __init__(self, parent,
                 size=settings.DEFAULT_MAP0_SIZE,
                 sync=None,
                 mapmul=settings.DEFAULT_MAP0):
        if not mapmul:
            raise Exception, "You need to specify a map.mul for UOMap"
        self.mapmul = uomap.MapCacheSingular(mapmul)
        if not sync:
            sync = UOMapSync(self)
        super(UOMap, self).__init__(parent, size, sync)


