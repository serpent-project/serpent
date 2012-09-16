# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    Chunk Decoder / Encoder

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
import zlib, numpy
from const import BlockTypes, BiomeClasses

def uncompress(data):
    return zlib.decompress(data)

def compress(data):
    return zlib.compress(data, 9)

def resolve_tile(tilenumber):
    return BlockTypes.Dirt

class Chunk:
    def __init__(self):
        self.biome_layers = numpy.zeros((16), dtype=int)
        self.blocks = numpy.zeros((16, 16, 16), dtype=int)
        self.metadata = numpy.zeros((16, 16, 16), dtype=int)
        self.block_lights = numpy.zeros((16, 16, 16), dtype=int)
        self.sky_lights = numpy.zeros((16, 16, 16), dtype=int)
        self.add_data = numpy.zeros((16, 16, 16), dtype=int)

    def fill_sky(self):
        pass

    def sky_shade(self, brightness=0xf):
        """
            sky shade this block.
        """
        if not brightness:
            return 0x0
        return brightness

    def w_biomes(self):
        ret = ''
        for z in xrange(16):
            ret += chr(self.biome_layers[z])
        return ret

    def r_biomes(self, data):
        for z in xrange(16):
            self.biome_layers[z] = ord(data[z])

    def w_bytes(self, chunk_block):
        # returns a string containing byte information about the given array
        ret = ''
        for y in xrange(16):
            for z in xrange(16):
                for x in xrange(16):
                    ret += chr(chunk_block[x, y, z])
        return ret

    def w_half_bytes(self, chunk_block):
        # returns a string containing 1/2byte information about the given array
        ret = ''
        b = None
        for y in xrange(16):
            for z in xrange(16):
                for x in xrange(16):
                    cb = chunk_block[x, y, z]
                    if b == None:
                        # new byte
                        b = cb << 4
                    else:
                        b |= cb & 0x0f
                        ret += chr(b)
                        b = None
        return ret

    def r_bytes(self, chunk_block, data):
        for y in xrange(16):
            for z in xrange(16):
                for x in xrange(16):
                    c, data = data[0], data[1:]
                    chunk_block[x, y, z] = ord(c)
        return chunk_block

    def r_half_bytes(self, chunk_block, data):
        for y in xrange(16):
            for z in xrange(16):
                for x in range(0, 16, 2):
                    c, data = data[0], data[1:]
                    c = ord(c)
                    n1 = c & 0xf0 >> 4
                    n2 = c & 0x0f
                    chunk_block[x, y, z] = n1
                    chunk_block[x + 1, y, z] = n2
        return chunk_block

    def lay_ground(self, item_type=BlockTypes.Bedrock):
        for z in xrange(16):
            for x in xrange(16):
                self.blocks[x, 0, z] = item_type


def _chunkify(mb1, mb2, mb3, mb4, continuous=False):
    """
    # creates chunks out of 4 mapblocks.
    # gets the height of each block, determines, where it starts and where it ends.
    # creates higher chunks first
    # returns chunks, bitmask, add_bitmask
    """
    chunks = []
    bitmask = 0x0
    add_bitmask = 0x0
    # first create the heightmap
    height_map = numpy.zeros((16, 16), dtype=int)
    # now create the tile map
    tile_map = numpy.zeros((16, 16), dtype=int)
    #####
    if mb1 is not None:
        height_map[0:8, 0:8] = mb1.heights.copy()
        tile_map[0:8, 0:8] = mb1.tiles.copy()
    if mb2 is not None:
        height_map[8:16, 0:8] = mb2.heights.copy()
        tile_map[8:16, 0:8] = mb2.tiles.copy()
    if mb3 is not None:
        height_map[0:8, 8:16] = mb3.heights.copy()
        tile_map[0:8, 8:16] = mb3.tiles.copy()
    if mb4 is not None:
        height_map[8:16, 8:16] = mb4.heights.copy()
        tile_map[8:16, 8:16] = mb4.tiles.copy()
    #####
    lowest_height = height_map.min()
    highest_height = height_map.max()
    for layer in xrange(16):
        chunk = None
        # see if i have still items at this height
        # or already?
        height = layer * 16
        if height < lowest_height or height > highest_height:
            # we do nothing.
            pass
        else:
            chunk = Chunk()
            if layer == 0:
                chunk.lay_ground(BlockTypes.Bedrock)
            for y in xrange(16):
                for z in xrange(16):
                    for x in xrange(16):
                        rx = z
                        ry = x
                        # read the cell height
                        cell_height = height_map[rx, ry]
                        if height + y < cell_height:
                            cell_tile = tile_map[rx, ry]
                            chunk.blocks[x, y, z] = resolve_tile(cell_tile)
        # after chunk has been built or not:
        if chunk is not None:
            chunks += [chunk]
            bitmask |= (1 << layer)
        else:
            if continuous:
                chunk = Chunk()
                chunk.fill_sky()
    return chunks, bitmask, add_bitmask

def chunkify(mb1, mb2, mb3, mb4, continuous=False):
    """ uses _chunkify to create chunks.
        it then serializes it to data
        returns data blob.
    """
    data = ''
    chunks, bitmask, add_bitmask = _chunkify(mb1, mb2, mb3, mb4, continuous)
    # blockdata
    for chunk in chunks:
        data += chunk.w_bytes(chunk.blocks)
    # metadata:
    for chunk in chunks:
        data += chunk.w_half_bytes(chunk.metadata)
    # light array:
    for chunk in chunks:
        data += chunk.w_half_bytes(chunk.block_lights)
    for chunk in chunks:
        data += chunk.w_half_bytes(chunk.sky_lights)
    # add data:
    for chunk in chunks:
        data += chunk.w_half_bytes(chunk.add_data)
    # biome array if continuous
    if continuous:
        for chunk in chunks:
            data += chunk.w_biomes()
    return data, bitmask, add_bitmask

def chunkify_compressed(mb1, mb2, mb3, mb4, continuous=False):
    chunkdata, bitmask, add_bitmask = chunkify(mb1, mb2, mb3, mb4, continuous)
    return compress(chunkdata), bitmask, add_bitmask
