# -*- coding: utf-8 -*-
import numpy

def select_tile(tile_list, f):
    """
        selects a tile from tile_list * 2 to make placement more even.
        however this method would destroy linear order in your tile_list.
    """
    tile_list = tile_list + tile_list
    l = len(tile_list) # total number of tiles.
    if not l:
        return 0x1
    if f >= 1.0:
        f = 0.99
    return tile_list[ int(numpy.floor(l * f)) ]

def select_tile_linear(tile_list, f):
    """
        selects a tile from tile_list. opts more for lower due to math.
        e.g. for 3 choices, the loser is third.
        ideal for linear choices where order is important.
    """
    l = len(tile_list) # total number of tiles.
    if not l:
        return 0x1
    if f >= 1.0:
        f = 0.99
    return tile_list[ int(numpy.floor(l * f)) ]
