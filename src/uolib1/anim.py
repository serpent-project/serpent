# -*- coding: utf-8 -*-

from struct import unpack, pack
from common import NOT_SET, rgb_rgb555, rgb555_rgb, StandardSurface
from indexer import IndexCache

class AnimIdxCache(IndexCache):
    pass

class AnimGroup( object ):
    def __init__(self, data, *args):
        if len(args) == 257:
            self.palette = args[:256]
            self.num_offsets = args[256]
            self.offsets = unpack( "<" + "L" * self.num_offsets, data[ : self.num_offsets * 4 ] )
            framedata_size = len( data ) - self.num_offsets * 4
            self.framedata = unpack( "<" + "H" *  (framedata_size / 2), data[ self.num_offsets * 4 : ])
        
class AnimHandler( object ):
    
    def load_all(self, index):
        pass
    
    def read_anim_group(self, data):
        header_format = "<" + "H" * 256 + "L"
        group = AnimGroup( data[512 + 4:], *unpack( header_format, data[:512 + 4]) ) 
        
        
        

class AnimFile( AnimHandler ):
    pass
