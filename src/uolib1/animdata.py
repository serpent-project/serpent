# -*- coding: utf-8 -*-

from struct import unpack, pack

class AnimDataEntry(object):
    """
        class capable of interpreting animation data.
    """
    def __init__(self, udata = None, data = None, id = None):
        if udata:
            self.animations = list( udata[0] )
            self.unknown = udata[1]
            self.frame_count = udata[2]
            self.interval = udata[3]
            self.frame_start = udata[4]
        self.id = id
    
    def __list__(self):
        return [ self.animations, self.unknown, self.frame_count, self.interval, self.frame_start ]
    
    def __len__(self):
        return self.frame_count
    
    def __setitem__(self, index, value):
        self.animations[index] = value
    
    def __getitem__(self, index):
        return self.animations[index]
    
class AnimData(object):
    """
        AnimData is for managing animdata.mul - animations for arts.
        read animdata[object_id] if it has flag Animated in tiledata.
        each entry is a 64-tuple followed by 4 bytes (unknown, framecount, interval, framestart)
    """
    frame_format = "64bBBBB"
    frame_size = 64 + 4
    entries = None
    load_unknowns = True
    
    def __init__(self, file_name):
        self.open(file_name)
    
    def __getitem__(self, index):
        if self.entries:
            if index >= 0:
                return self.entries[index]
            else:
                return AnimDataEntry( udata=self.entries[abs(index)-1] , id = abs(index)-1 )
        
    
    def __setitem__(self, index, value):
        if self.entries:
            if isinstance(value, AnimDataEntry):
                self.entries[index] = value.__list__()
            else:
                self.entries[index] = value
    
    def __len__(self):
        if self.entries:
            return len(self.entries)
        
    def open(self, file_name = None):
        if file_name:
            self.file_name = file_name
        if self.file_name:
            f = open(self.file_name, 'rb')
            buffer = f.read()
            f.close()
            self.load_all(buffer)
            
    def load(self, file_name = None):
        self.open(file_name)
    
    def load_all(self, buffer):
        self.entries = []
        if self.load_unknowns:
            self.unknowns = []
        else:
            self.clear_unknowns()
        while len(buffer) >= self.frame_size:
            if self.load_unknowns:
                self.unknowns += [ unpack("<L", buffer[:4]) ]
            buffer = buffer[4:]
            block = self.read_block(buffer)
            buffer = buffer[self.frame_size * 8:]
            self.entries += block
            
    def read_block(self, data):
        if len(data) >= (self.frame_size * 8):
            ublock = unpack( "<" + self.frame_format * 8, data[ : self.frame_size * 8 ] )
            return [ [ ublock[68*i:68*i+64], ublock[68 * i + 64], ublock[68 * i + 65], ublock[68 * i + 66], ublock[68 * i + 67] ] for i in xrange(8) ]
    
    def create_data_stream(self, datastream = ""):
        for i in xrange( len( self.entries ) / 8 ):
            data = pack( "<L" + self.frame_format * 8, 0, *self.entries[ i * 8: i * 8 + 8 ] )
            if isinstance(datastream, file):
                datastream.write(data)
            else:
                datastream += data
    
    def save(self, file_name):
        if file_name:
            f = open(file_name, 'wb')
            self.create_data_stream(f)
            f.close()
    
    def clear_unknowns(self):
        self.unknowns = [ 0 for i in xrange(0x4000 / 8) ]
        
    def new(self):
        self.clear_unknowns()
        self.entries =  [ [ ( 0 for i in xrange(64) ), 0, 0, 0, 0 ] for j in xrange(0x4000) ]
