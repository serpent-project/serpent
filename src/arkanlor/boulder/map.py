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

SHAPE_X = 8
SHAPE_Y = 8
FSHAPE_X = float(SHAPE_X)
FSHAPE_Y = float(SHAPE_Y)
BLOCK_SHAPE = (SHAPE_X, SHAPE_Y)

class MapBlock:
    # defines a walkable grid
    def __init__(self, parent, offset_x=0, offset_y=0,):
        self.parent = parent
        if not offset_x % SHAPE_X:
            offset_x = offset_x - offset_x % SHAPE_X
        if not offset_y % SHAPE_Y:
            offset_y = offset_y - offset_y % SHAPE_Y
        self.offset_x, self.offset_y = offset_x, offset_y
        self.matrix = numpy.zeros(BLOCK_SHAPE, dtype=int) # flag matrix
        self.items = [None for x in xrange(64)] # 8x8


class Map:
    def __init__(self, width, height):
        self.blocks_x, self.blocks_y = numpy.ceil(width / FSHAPE_X), numpy.ceil(height / FSHAPE_Y)
        self.blocks = {}

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
        try:
            return self.blocks[bx, by]
        except IndexError:
            block = MapBlock(self, x, y)
            self.blocks[bx, by] = block
            return block

    def walkable(self, x, y):
        return self.block(x, y).matrix[self._rel(x, y)] == 0x0



