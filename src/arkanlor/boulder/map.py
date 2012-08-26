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

BLOCK_SHAPE = (64, 64)
X = 0
Y = 1

class MapBlock:
    # loads boundaries around a 64x64 block.
    # defines a walkable grid
    def __init__(self, parent, offset_x=0, offset_y=0,):
        self.parent = parent
        if not offset_x % BLOCK_SHAPE[X]:
            offset_x = offset_x - offset_x % BLOCK_SHAPE[X]
        if not offset_y % BLOCK_SHAPE[Y]:
            offset_y = offset_y - offset_y % BLOCK_SHAPE[Y]
        self.offset_x, self.offset_y = offset_x, offset_y
        self.matrix = numpy.zeros(BLOCK_SHAPE, dtype=int) # flag matrix


class Map:
    def __init__(self, width, height):
        self.blocks_x, self.blocks_y = numpy.ceil(width / 64.0), numpy.ceil(height / 64.0)
        self.blocks = {}

    def load_block(self, x, y):
        bx, by = numpy.floor(x / 64.0), numpy.floor(y / 64.0)
        if (bx, by) not in self.blocks.keys():
            self.blocks[bx, by] = MapBlock(self, x, y)
        return self.blocks[bx, by]




