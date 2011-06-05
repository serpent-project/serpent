# -*- coding: utf-8 -*-

import re, os
from struct import unpack, pack, calcsize
import binary
from map import *

class MapFileWholistic( MapHandler ):
    """just in case you really want to have everything in objects...
    but it needs a lot of time to load and a lot of memory."""
    map_blocks = None
    map_load = True
    
    def __init__(self, file_name = None):
        MapHandler.__init__(self)
        self.file_name = file_name
        self.map_blocks = None
        if self.file_name and self.map_load:
            self.load()
    
    def load(self):
        if os.path.exists(self.file_name):
            f = open(self.file_name, 'r')
            buffer = f.read()
            f.close()
            return self.parse(buffer)
    
    def parse(self, buffer = None):
        if len(buffer) != self.size:
            errors += [ "MapFile: The size should be %s but is %s" % ( self.size, len(buffer) ) ]
        if buffer is not None:
            # allocate everything, or it will be slow as hell.
            self.map_blocks = [ MapBlock() for i in xrange(self.map_y * self.map_x) ]
            offset = 0
            for y in xrange( self.map_y ):
                self.parse_callback(y)
                for x in xrange( self.map_x ):
                    self.map_blocks[y * self.map_x + x].parse( buffer[offset:offset+MapBlock.size] )
                    offset += MapBlock.size
    
    def parse_callback(self, step = 0):
        if not step % 100:
            print "map loaded %s/%s" % ( step / 100, self.map_y / 100 )
        elif step == self.map_y -1:
            print "map load complete."
    
    def binarize(self):
        buffer = ""
        for y in xrange( self.map_y ):
            for x in xrange( self.map_x):
                buffer += self.map_blocks[y*self.map_x+x].binarize()
        return buffer
    
    def save_serial(self, to_file = None):
        if to_file:
            f = open(to_file, 'w')
            for y in xrange( self.map_y ):
                for x in xrange( self.map_x):
                    f.write(self.map_blocks[y*self.map_x+x].binarize())
            f.close()
    
    def save_buffer(self, to_file = None):
        if to_file:
            f = open(to_file, 'w')
            f.write(self.binarize())
            f.close()
    
    def save(self, to_file = None):
        self.save_serial(to_file)
    
    def get_block(self, x, y):
        return self.map_blocks[y * self.map_x + x]
    
    def get_cell(self, x, y):
        return self.get_block(x / 8, y / 8).get_cell( x % 8, y % 8 )
