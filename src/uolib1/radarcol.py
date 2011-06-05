# -*- coding: utf-8 -*-

import re, os
from struct import unpack, pack, calcsize
from common import rgb555_rgb, StandardSurface
from map import *

class Radarcol( object ):
    data = None
    size = 65536
    cache = None
    def __init__(self, file_name = None):
        self.cache = None
        if file_name:
            self.load(file_name)
    
    def load(self, file_name):
        self.file_name = file_name
        f = open(file_name, 'rb')
        data = f.read()
        f.close()
        self.data = unpack("<" + "H" * ( len(data) / 2 ), data )
    
    def get_rgb(self, num):
        """returns a trip-tuple with (r,g,b)"""
        if self.cache:
            return self.cache[num]
        rgb = self.data[ num : num + 1 ][0]
        return rgb555_rgb(rgb)
    
    def get_rgbhex(self, num):
        if isinstance(num, int):
            return self.get_rgbhex(self.get_rgb(num))
        else:
            return "%02X%02X%02X" % num
    
    def rgb_list(self):
        """@deprecated: """
        if self.cache:
            return self.cache
        ret = []
        for i in xrange(self.size):
            ret += [ self.get_rgb(i) ]
        self.cache = ret
        self.data = None
        return ret
    
    def get_radar_map(self, map = None, statics = None, scale = 1, upper_left = (0,0), lower_right = None, image = None, height_map = False, tile_map = True ):
        scale = int(scale)
        if not scale:
            # stupid?
            scale = 1
        if not lower_right:
            if map:
                lower_right = ( map.map_x * 8, map.map_y * 8 )
            else:
                lower_right = ( Map.map_x * 8, Map.map_y * 8 )
        if not image:
            image = StandardSurface()
            image.new( (lower_right[0] / scale, lower_right[1] / scale) )
        block_x = 0
        block_y = 0
        block = None
        static = None
        old_block_y = None
        old_block_x = None
        for x in range( upper_left[0] / scale, lower_right[0] / scale ):
            block_x = x * scale / 8
            if block_x != old_block_x:
                if map:
                    block = map.get_blockx_raw(block_x)
                old_block_x = block_x
            cell_x = x * scale % 8
            for y in range( upper_left[1] / scale, lower_right[1] / scale ):
                block_y = y * scale / 8
                cell_y = y * scale % 8
                if statics:
                    s = statics.get_statics( (x * scale, y * scale) )
                    if len(s) > 0:
                        s = s[0] # normally we would search the highest.
                        image.dot( (x - upper_left[0], y - upper_left[1]), self.get_rgb( s[0] + 16384 ))
                        continue
                if block_y != old_block_y:
                    if block:
                        b = block[ block_y * 196 : block_y * 196 + 196 ]
                    old_block_y = block_y
                if block:
                    # calculate the point we want to get information from in the block:
                    start = (cell_y * 8 + cell_x) * 3 + 4
                    if height_map and not tile_map:
                        a = unpack("<b", b[ start+2:start+3 ])[0]
                        a += 127
                        rgb = ( a, a, a )
                        image.dot( (x - upper_left[0], y - upper_left[1]), rgb )
                    elif not height_map and tile_map:
                        c = unpack("<H", b[ start: start + 2 ])[0]
                        image.dot( (x - upper_left[0], y - upper_left[1]), self.get_rgb(c))
                    else:
                        c, a = unpack("<Hb", b[ start: start + 3 ])
                        rgb = self.get_rgb(c)                        
                        rgb = (rgb[0] + a,rgb[1] + a, rgb[2] + a, ) 
                        image.dot( (x - upper_left[0], y - upper_left[1]), rgb)
        return image