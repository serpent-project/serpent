# -*- coding: utf-8 -*-
"""
    Statics handling.
    Use the Statics class to load staidx and statics at the same time.
    
    Statics( idxfile, mulfile)
        cache
        auto_sort
        use_cache - prepares cache automatically.
    
    A Static Entry:
        [ uid, xoffset, yoffset, altitude, color ]
"""


import re
from struct import unpack, pack, calcsize
from common import MapRelated, NOT_SET
import binary

class StaidxHandler( MapRelated ):
    size_idx_entry = 12
    file_name = None
    def load(self, file_name): pass
    def save(self, file_name): pass
    def new(self, file_name): pass
    def get_position(self, pos): pass
    def set_position(self, pos, start, length): pass
    def get_statics(self, pos): pass
    def set_statics(self, pos, data): pass

class StaticHandler( MapRelated ):
    file_name = None
    def __init__(self, file_name):
        if file_name:
            self.load(file_name)
    def load(self, file_name): pass
    def save(self, file_name): pass
    def new(self, file_name): pass
    def get_block_statics(self, pos, length): pass
    def set_block_statics(self, pos, block): pass
    def sort_statics(self, static_list): pass

class StaidxCache( StaidxHandler ):
    cache = None
    staidx = None    
    def __init__(self, file_name = None):
        if file_name:
            self.load(file_name)
    
    def load(self, file_name = None):
        self.file_name = file_name
        f = open(file_name, 'rb')
        self.staidx = f.read()
        f.close()        
    
    def save(self, file_name = None):
        f = open(file_name, 'wb')
        for index in xrange( map_x * map_y ):
            if self.cache and self.cache[index]:
                f.write( pack("<LLL", self.cache[index][0], self.cache[index][1], NOT_SET ))                
            elif self.staidx:
                f.write( self.staidx[ index * self.size_idx_entry: index+1 * self.size_idx_entry ] )
            else:
                raise Exception("Not enough data.")
        f.close()
    
    def get_position(self, pos):
        index = pos
        if isinstance(pos, tuple):
            block_x, block_y = pos
            index = ( block_x * self.map_y + block_y )
        if self.cache: # look in writecache.
            if self.cache[ index ]:
                return self.cache[ index ]
        sindex = index * self.size_idx_entry
        start, length = unpack( "<LL", self.staidx[ sindex: sindex + 8 ] )
        if self.cache and start != NOT_SET:
            self.cache[ index ] = (start, length)
        return (start, length)
    
    def set_position(self, pos, start, length):
        index = None
        if isinstance(pos, tuple):
            block_x, block_y = pos
            index = ( block_x * self.map_y + block_y ) * self.size_idx_entry
        else:
            index = pos * self.size_idx_entry
        if not self.cache:
            self.prepare_cache()
        self.cache[index] = (start, length)
    
    def prepare_cache(self):
        self.cache = [ None for i in xrange(self.map_x * self.map_y) ]
    
    def fill_cache(self):
        if not self.cache:
            self.prepare_cache()
        if not self.staidx:
            return
        for index in ( self.map_x * self.map_y ):
            self.get_position( index ) 
        self.staidx = None

class StaticFile( StaticHandler):
    """intended for mainly read only purposes, staticfile always works in a file"""
    handle = None
    def load(self, file_name):
        self.handle = open(file_name, 'rb')
        
    def save(self, file_name): pass
    def new(self, file_name): pass
    
    def get_block_statics(self, pos, length):
        self.handle.seek(pos)
        return self.handle.read(length)
        
    def set_block_statics(self, pos, block): pass
    def sort_statics(self, static_list): pass

class StaticStringCache( StaticHandler ):
    """StaticCache reads statics and remembers them in a cache."""
    buffer = None
    def __init__(self, file_name):
        if file_name:
            self.load(file_name)
            
    def load(self, file_name):
        self.file_name = file_name
        f = open(file_name, 'rb')
        self.buffer = f.read()
        f.close()
        
    def save(self, file_name):
        f = open(file_name, 'wb')
        f.write(self.buffer)
        f.close()
        
    def new(self, file_name):
        self.buffer = ""
        
    def get_block_statics_raw(self, pos, length):
        if pos < len(self.buffer):
            return self.buffer[ pos: pos+length ]
        
    def set_block_statics_raw(self, pos, block):
        self.buffer = self.buffer[ : pos ] + block + self.buffer[ self.pos + len(block) : ]
    
    def get_block_statics(self, pos, length):
        data = self.get_block_statics_raw(pos, length)
        ret = []
        if data:
            offset = 0
            while offset < len(data):
                id, x, y, z, c = unpack("<HBBbH", data[offset:offset + 7])
                ret += [ [ id, x, y, z, c ] ]
                offset += 7
        return ret
    
    def set_block_statics(self, pos, block):
        if isinstance(block, str):
            return self.set_block_statics_raw(pos, block)
        data = ""
        for entry in block:
            data += pack("<HBBbH", entry)
        return self.set_block_statics_raw(pos, data)

class StaticCache( StaticHandler ):
    def load(self, file_name):
        self.file_name = file_name
        if file_name:
            f = open( file_name, 'rb' )
            buffer = f.read()
            f.close()
            self.cache = list( unpack( '<' + 'HBBbH' * (len(buffer) / 7), buffer ) )
            
    def save(self, file_name): pass
    def new(self, file_name): pass
    
    def get_block_statics(self, pos, length):
        static_items = []
        static_data = self.cache[ (pos/7) * 5 : (pos/7) * 5 + (length/7) * 5 ]
        offset = 0
        while offset < len(static_data):
            static_item = static_data[ offset : offset + 5 ]
            static_items += [ static_item ]
            offset += 5
        return static_items
                
    def set_block_statics(self, pos, block): pass

class Statics( StaidxHandler ):
    cache = None
    auto_sort = False
    use_cache = False
    
    def __init__(self, staidx_file, statics_file):
        """
            Creates a Statics Handler, which can read static data
            @param staidx_file is the staidx.mul to use
            @param statics_file is the statics.mul to use.
        """
        self.staidx = StaidxCache( staidx_file )
        self.statics = StaticCache( statics_file )
        if self.use_cache:
            self.prepare_cache()
    
    def prepare_cache(self):
        """
            for faster reading of statics files, you should prepare the cache.
        """
        self.cache = [ None for i in xrange( self.map_x * self.map_y ) ]
    
    def set_statics(self, pos, data):
        if isinstance(pos, int):
            if self.cache:
                self.cache[ pos ] = data
            else:
                pass                
        else:
            x, y = pos
            block_x = x / 8
            block_y = y / 8
            x = x % 8
            y = y % 8
            cache_index = block_x * self.map_y + self.block_y
            if self.cache[ cache_index ]:
                # we have already data in cache_index, add them to the right one:
                self.cache[ cache_index ][ x * 8 + y ] = data
            else:
                self.cache[ cache_index ] = [ None for i in xrange(64) ]
                self.cache[ cache_index ][ x * 8 + y ] = data
            
    def get_statics(self, pos):
        x, y = pos
        block_x = x / 8
        block_y = y / 8
        x = x % 8
        y = y % 8
        cache_index = block_x * self.map_y + block_y
        if self.use_cache:
            if self.cache[ cache_index ] is not None:
                entry = self.cache[ cache_index ][ x * 8 + y ]
                if entry is not None:
                    return entry
            else:
                self.cache[ cache_index ] = [ [] for i in xrange(64) ]
        
        # cache-entry did not contain data, or has been created.
        block_idx = self.staidx.get_position( (block_x, block_y) )
        block = self.statics.get_block_statics( block_idx[0], block_idx[1] )
        cache_entry = None
        if self.use_cache:
            cache_entry = self.cache[ cache_index ]
            if not cache_entry: # this is useless i think
                cache_entry = [ [] for i in xrange(64) ]
        ret = []
        highest = None
        for entry in block:
            entry_x = entry[ 1 ]
            entry_y = entry[ 2 ]
            entry_idx = entry_x * 8 + entry_y
            if entry_x == x and entry_y == y:
                if not highest:
                    highest = entry
                elif highest[3] > entry[3]:
                    ret += [ entry ]
                else:
                    ret += [ highest ]
                    highest = entry
            if self.use_cache:
                if cache_entry[ entry_idx ]:
                    cache_entry[ entry_idx ] += [ entry ]
                else:
                    cache_entry[ entry_idx ] = [ entry ]
            
        if highest:
            ret += [ highest ]
        if self.use_cache:
            self.cache[ cache_index ] = cache_entry
        return ret