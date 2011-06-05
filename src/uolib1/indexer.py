# -*- coding: utf-8 -*-

from uo.common import NOT_SET
from struct import pack, unpack

# Indexer: Classes for Index Files.

class IndexHandler( object ):
    standard_size = 0x1
    file_name = None
    def __init__(self, file_name = None):
        if file_name:
            self.load(file_name)
    def load(self, file_name = None):
        self.file_name = file_name
    def save(self, file_name = None) : pass
    def new(self): pass
    def get_position(self, pos): pass
    def set_position(self, pos, start, length, unknown = NOT_SET): pass
    
    def __getitem__(self, index):
        return self.get_position( index )
    
    def __setitem__(self, index, value):
        return self.set_position(index, *value)
    
    def __len__(self):
        return self.standard_size

class IndexCache( IndexHandler ):
    standard_size = 0x1
    uindex = None
    
    def load(self, file_name = None):
        self.file_name = file_name
        f = open(file_name, 'rb')
        data = f.read()
        f.close()
        self.uindex = list( unpack("<" + "LLL" * (len(data) /12), data  ) )
    
    def save(self, file_name = None):
        if file_name:
            data = pack( "<" + "L" * ( len(self.uindex) ), *self.uindex )
            f = open(file_name, 'wb')
            f.write(data)
            f.close()
    
    def new(self, size = 1):
        self.uindex = [ NOT_SET for i in xrange(size * 3)  ]
    
    def get_position(self, index):
        return self.uindex[ index * 3: index*3 + 3 ]
    
    def set_position(self, index, start, length, unknown = NOT_SET):
        self.uindex[ index * 3 ] = start
        self.uindex[ index * 3 + 1 ] = length
        self.uindex[ index * 3 + 2 ] = unknown
    
    def __len__(self):
        return len(self.uindex)/3
    