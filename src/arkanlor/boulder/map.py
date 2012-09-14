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


class MapBlock:
    # defines a walkable grid
    def __init__(self, parent,
                 offset_x=0, # bx * 8
                 offset_y=0, # by * 8
                 header=0):
        self.parent = parent
        if not offset_x % SHAPE_X:
            offset_x = offset_x - offset_x % SHAPE_X
        if not offset_y % SHAPE_Y:
            offset_y = offset_y - offset_y % SHAPE_Y
        self.header = header or 0
        self.offset_x, self.offset_y = offset_x, offset_y
        self.bx, self.by = self.offset_x / SHAPE_X, self.offset_y / SHAPE_Y
        self.flags = numpy.zeros(BLOCK_SHAPE, dtype=int) # flag matrix
        self.tiles = numpy.zeros(BLOCK_SHAPE, dtype=int) # tile matrix.
        self.heights = numpy.zeros(BLOCK_SHAPE, dtype=int) # heightmap
        self.items = [[] for x in xrange(64)] # 8x8
        self._synced = None
        self.sync()

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
        return [ {'tile': self.tiles[x, y], 'z': self.heights[x, y]}
                 for y in xrange(SHAPE_Y) for x in xrange(SHAPE_X)
                 ]

    def get_statics(self):
        ret = []
        for cell in self.items:
            ret += cell
        return ret

    def packet_info(self):
        return {
                'bx': self.bx,
                'by': self.by,
                'cells': self.get_cells(),
                'statics': self.get_statics()
                }


class Map(object):
    def __init__(self, parent, size, sync=None):
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
        except IndexError:
            block = MapBlock(self, bx * SHAPE_X, by * SHAPE_Y)
            self.blocks[bx, by] = block
            return block

    def walkable(self, x, y):
        return self.block(x, y).matrix[self._rel(x, y)] == 0x0

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


