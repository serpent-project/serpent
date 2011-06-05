# -*- coding: utf-8 -*-

import re
from struct import unpack, pack, calcsize
import binary

class StaticsEntry(object):
    objid = None # short
    xoffset = None # ubyte
    yoffset = None # ubyte 
    alt = None # sbyte
    color = None # short
    def __init__(self, objid, xoffset, yoffset, alt, color):
        self.objid = objid
        self.xoffset = xoffset
        self.yoffset = yoffset
        self.alt = alt
        self.color = color
    
    def radarcol(self):
        if self.objid:
            return 16384 + self.objid
        else:
            return 0
    
    def __str__(self):
        return "Object: %s, X=%s,Y=%s,Z=%s c=%s" % (self.objid, self.xoffset, self.yoffset, self.alt, self.color)
    
    def __repr__(self):
        return str(self)

class StaidxEntry(object):
    start = None # dword
    length = None # dword
    unknown = None # dword
    data = None
    def __init__(self, start = None, length = None, unknown = None):
        self.start = start
        self.length = length
        self.unknown = unknown
        self.data = None
    
    def __str__(self):
        if self.length:
            return "<staidx start %s length %s>" % (self.start, self.length)
        else:
            return "<staidx without data>"
    
    def get_data(self):
        return data
    
    def set_data(self, data):
        self.data = data
    
    def get_statics_regexp(self, staticsfile):
        ret = []
        if self.length:
            # seek in the file to position we need
            staticsfile.seek( self.start )
            raw_data = staticsfile.read( self.length )
            r = re.compile("(..)(.)(.)(.)(..)" , re.DOTALL)
            packed = r.findall(raw_data)
            raw_data = map(lambda x: (binary.word(x[0]), binary.ubyte(x[1]), binary.ubyte(x[2]), binary.byte(x[3]), binary.word(x[4])), packed)
            for entry in raw_data:
                ret += [ StaticsEntry( entry[0], entry[1], entry[2], entry[3], entry[4] ) ]
            self.data= ret
            return ret
        return None
    
    def get_statics_serial(self, staticsfile):
        ret = []
        if self.length:
            staticsfile.seek( self.start )
            raw_data = staticsfile.read( self.length )
            offset = 0
            while offset < len(raw_data):
                entry = raw_data[offset:offset + 7]
                id, ox, oy, z, c = unpack("<HBBbH", entry)
                ret += [ StaticsEntry( id, ox, oy, z, c ) ]
                offset += 7
            self.data = ret
            return ret
        return None
    
    def get_statics(self, staticsfile):
        return self.get_statics_serial(staticsfile)
    
    def write_statics(self, staticsfile):
        if self.data:
            self.start = staticsfile.tell()
            self.length = len(self.data) * 7
            for entry in self.data:
                buffer = pack("<HBBbH", entry.objid, entry.xoffset, entry.yoffset, entry.alt, entry.color)
                staticsfile.write(buffer)
    
    def add_static(self, entry):
        if isinstance(entry, StaticsEntry):
            if self.data:
                self.data += [ entry ]
            else:
                self.data = [ entry ]
    
    def remove_static(self, entry):
        if entry in self.data:
            self.data.remove(entry)
    
    def sort_statics(self):
        if self.data:
            pass
    
## the file handlers.

class StaidxFile(object):
    staidx_objects = None
    filename = None
    blocks_x = 768
    blocks_y = 512
    NOT_SET = 0xffffffff
    __blocks = None
    
    def __init__(self, filename = None):
        self.staidx_objects = []
        self.__blocks = None
        self.open(filename)
        
    def write(self, filehandle):
        if self.staidx_objects:
            for x in xrange(self.blocks_x):
                for y in xrange(self.blocks_y):
                    index = (x * self.blocks_y) + y
                    idx = self.staidx_objects[index]
                    buffer = None
                    if idx:
                        buffer = pack("LLL", idx.start, idx.length, idx.unknown )
                    else:
                        buffer = pack("LLL", self.NOT_SET, self.NOT_SET, self.NOT_SET)
                    filehandle.write( buffer )
                    
                    
    def write_statics_very_correct(self, filehandle):
        """writes the statics in the correct manner."""
        if self.staidx_objects:
            for x in xrange(self.blocks_x):
                for y in xrange(self.blocks_y):
                    index = (x * self.blocks_y) + y
                    idx = self.staidx_objects[index]
                    if idx:
                        idx.write_statics(filehandle)
    
    def write_statics_serial(self, filehandle):
        """serialized writing should be a bit faster"""
        if self.staidx_objects:
            for idx in self.staidx_objects:
                if idx:
                    idx.write_statics(filehandle)
    
    def write_statics(self, filehandle):
        return self.write_statics_serial(filehandle)
    
    def read_regexp(self):
        """"""
        # read the whole file in your blob
        # parse the blob afterwards. this method uses a regexpression,
        # which is short.
        errors = 0
        warnings = 0
        f = open(self.filename, 'r')
        blob = f.read()
        f.close()
        r = re.compile("(....)(....)(....)" , re.DOTALL)
        packed = r.findall(blob)
        data = map(lambda x: (binary.dword(x[0]), binary.dword(x[1]), binary.dword(x[2])), packed)
        self.staidx_objects = []
        self.__blocks = None
        count = 0
        for idx in data:
            if idx[0] < self.NOT_SET:
                self.staidx_objects += [ StaidxEntry(idx[0], idx[1], idx[2]) ]
                count += 1
            else:
                if idx[1] > 0 and idx[1] < self.NOT_SET:
                    errors += 1
                if idx[2] > 0 and idx[2] < self.NOT_SET:
                    warnings += 1
                self.staidx_objects += [ None ]
        return (count, errors, warnings)
    
    def read_serial(self):
        errors = 0
        warnings = 0
        f = open(self.filename, 'r')
        blob = f.read()
        f.close()
        self.staidx_objects = []
        self.__blocks = None
        count = 0
        offset = 0
        while offset < len(blob):
            entry = blob[offset:offset+12]
            start, length, u = unpack("LLL", entry)
            if start < self.NOT_SET:
                self.staidx_objects += [ StaidxEntry(start, length, u) ]
            else:
                self.staidx_objects += [ None ]
            offset += 12
        return (count, errors, warnings)
    
    def read(self):
        return self.read_serial()
    
    def open(self, filename = None):
        if filename:
            self.filename = filename
        self.read()
    
    def blocks(self):
        """creates a list of where data begins and ends in statics.
        used for enumerating the size of the whole file, and so on."""
        # run thru all staidx objects
        # add all starts and ends to a list
        # sort them. now every end should be followed by a next start.
        blocks = []
        #indexes_checked = []
        if self.__blocks:
            return self.__blocks[:]
        if self.staidx_objects:
            # read y, x.
            for x in xrange(self.blocks_x):
                for y in xrange(self.blocks_y):
                    index = (x * self.blocks_y) + y
                    #indexes_checked += [ index ]
                    idx = self.staidx_objects[index]
                    if idx:
                        blocks += [ idx.start ]
                        blocks += [ idx.start + idx.length ]
        #indexes_checked.sort()
        #if differ(indexes_checked, xrange(self.blocks_x * self.blocks_y)):
        #    print "differ!?"
        self.__blocks = blocks
        return self.__blocks[:]
    
    def check_gaps(self):
        """checks for gaps"""
        blocks = self.blocks()
        blocks.sort()
        frags = []
        if len(blocks) > 2:
            for i in xrange(len(blocks)-2):
                if i < len(blocks) - 2 and i % 2:
                    block1 = blocks[i]
                    block2 = blocks[i+1]
                    if block1 != block2:
                        frags += [ i ]
        return frags
    
    def check_fragmentation(self):
        """checks for data fragmentation"""
        blocks = self.blocks()
        unsorted_blocks = self.blocks()
        blocks.sort()
        if binary.differ(blocks, unsorted_blocks):
            return False
        return True
    
    def check_incorrect_data(self, statics_size = 0xfffffffe):
        """checks data for corrupt entries"""
        size_count = 0
        zero_length_count = 0
        wrong_length_count = 0
        out_of_bounds_count = 0
        if self.staidx_objects:
            for idx in self.staidx_objects:
                if idx:
                    if idx.length == 0:
                        zero_length_count += 1
                    if idx.length % 7:
                        wrong_length_count += 1
                    if idx.start > statics_size:
                        size_count += 1
                    if idx.start + idx.length > statics_size:
                        out_of_bounds_count += 1
        return (zero_length_count, wrong_length_count, size_count, out_of_bounds_count)
    
    def get_idx_raw(self, x, y):
        """returns an indexentry at block x, y - if there is any. or None."""
        if self.staidx_objects:
            index = (x * self.blocks_y) + y
            if index < len(self.staidx_objects):
                return self.staidx_objects[index]                 
        return None
    
    def get_idx(self, x, y):
        """returns indexentry which cell x y belongs to"""
        return self.get_idx_raw( x/8, y/8 )
    
    def total(self):
        """returns a tuple, first entry is the size of the staticsmul, 
        the second is the resulting items count."""
        if self.staidx_objects:
            blocks = self.blocks()
            blocks.sort()
            last = len(blocks) - 1
            if blocks[last]:
                total = blocks[last]
                return (total, total / 7)
        return (0, 0)

class Statics( object ):
    staidx = None
    statics = None
    file_staidx = None
    file_statics = None
    statics_open = False
    
    def __init__(self, staidxfilename, staticsfilename):
        self.file_staidx = staidxfilename
        self.file_statics = staticsfilename
        self.staidx = StaidxFile( self.file_staidx )
        self.index_stats = self.staidx.read()
        self.statics_open = False
        self.statics = None
    
    def open_statics(self, staticsfilename):
        self.statics = open(staticsfilename, 'r')
        self.statics_open = True
    
    def close_statics(self):
        self.statics.close()
        self.statics_open = False
    
    def write_idx(self, filename):
        f = open(filename, 'w')
        self.staidx.write(f)
        f.close()
    
    def write_statics(self, filename):
        f = open(filename, 'w')
        self.staidx.write_statics(f)
        f.close()
    
    def read_static_sector(self, cell_x, cell_y):
        idx = self.staidx.get_idx(cell_x, cell_y)
        if not self.statics_open:
            self.open_statics(self.file_statics)
        if idx:
            return idx.get_statics( self.statics )
    
    def get_statics(self, cell_x, cell_y):
        sector = self.read_static_sector(cell_x, cell_y)
        cell_x = cell_x % 8
        cell_y = cell_y % 8
        ret = []
        if not sector:
            return ret
        for static in sector:
            if static.xoffset == cell_x and static.yoffset == cell_y:
                ret += [ static ]
        return ret
    
    def load_statics(self):
        for x in xrange(self.staidx.blocks_x):
            for y in xrange(self.staidx.blocks_y):
                self.read_static_sector(x * 8, y * 8)
