# -*- coding: utf-8 -*-

import re, os
from struct import unpack, pack, calcsize
from common import MapRelated
import binary

errors = []

class Parsable(object):
    size = 0
    def __init__(self):
        pass

    def parse(self, buffer=None):
        pass

    def parse_callback(self, step=0):
        print step

    def binarize(self):
        return ""

class MapBlock(MapRelated):
    __slots__ = MapRelated.__slots__ + ['unknown', 'cells']
    size = 64 * 3 + 4

    def __init__(self, cells=None, unknown=None):
        self.unknown = []
        self.cells = []
        if cells:
            self.cells = cells
            self.unknown = unknown

    def get_cells_from_buffer_serial(self, buffer):
        # skip unknown:
        unknown = buffer[:4]
        cell_buffer = buffer[4:self.size]
        offset = 0
        self.cells = []
        unpack_data = unpack("<" + "Hb" * 64, cell_buffer)
        while offset < 128:
            self.cells += [ unpack_data[offset : offset + 2] ]
            offset += 2
        self.unknown = unknown

    def get_cells_from_buffer_regex(self, buffer):
        # seems slower, but may be more performant on some systems.
        # skip unknown:
        unknown = buffer[:4]
        cell_buffer = buffer[4:self.size]
        r = re.compile("(..)(.)" , re.DOTALL)
        self.cells = []
        packed = r.findall(cell_buffer)
        data = map(lambda x: (binary.word(x[0]), binary.byte(x[1])), packed)
        for cell in data:
            self.cells += [cell]
        self.unknown = unknown

    def get_cells_from_buffer(self, buffer):
        return self.get_cells_from_buffer_serial(buffer)

    def parse(self, buffer=None):
        if buffer is not None:
            if len(buffer) < self.size:
                errors += ["MapBlock has not enough data."]
            self.get_cells_from_buffer(buffer[ : self.size ])

    def binarize(self):
        ret = self.unknown
        for cell in self.cells:
            ret += pack("<Hb", cell[0], cell[1])
        return ret

    def get_cell(self, x, y):
        if x > 8:
            x = x % 8
        if y > 8:
            y = y % 8
        return self.cells[ y * 8 + x ]

    def set_cell(self, x, y, cell):
        if x > 8:
            x = x % 8
        if y > 8:
            y = y % 8
        if len(self.cells) < y * 8 + x:
            self.cells[y * 8 + x] = cell

    def __str__(self):
        ret = ""
        for cell in self.cells:
            ret += "(%s)" % str(cell)
        return ret

class MapHandler(MapRelated):
    """
    Abstract base class for map file handlers.
    Every function here has to be implemented to interoperate with other classes.
    """
    file_name = None
    size = MapRelated.map_x * MapRelated.map_y * MapBlock.size
    def __init__(self, file_name=None):
        self.file_name = file_name
    def load(self, file_name=None):
        """supposed to load the map, should be called by init."""
        return False
    def save(self, to_file=None):
        """supposed to save the map to a file. to_file is mandatory"""
        return False
    def new(self):
        """supposed to create an empty map"""
        pass
    def get_cell(self, cell_x, cell_y):
        """supposed to get an individual cell of the map."""
        pass
    def get_block(self, block_x, block_y):
        """supposed to get a whole block of the map"""
        pass
    def get_block_raw(self, block_x, block_y):
        """supposed to get a whole block of the map in raw byte string"""
        pass
    def get_blockx_raw(self, x):
        """returns a whole x block in raw."""
        pass
    def set_block(self, x, y, block):
        """supposed to set a whole block of the map"""
        pass
    def set_cell(self, x, y, cell, alt=None):
        """supposed to set a cell in the map"""
        pass

class MapCache(MapHandler):
    """uses a list of string as cache to save the file, and operates on it
    like working on chromosomes in a cell works.
    specialities: its superb for writing speed and minimizes file io."""
    map_blocks = None
    map_data = None
    def __init__(self, file_name=None):
        # self.map_blocks = [ None ] * self.map_x * self.map_y
        self.map_data = None
        if file_name:
            self.load(file_name)

    def load(self, file_name):
        if os.path.exists(file_name):
            f = open(file_name, 'rb')
            self.map_data = []
            for x in xrange(self.map_x): # read y blocks of strings.
                self.map_data += [ f.read(self.map_y * MapBlock.size) ]
            f.close()
            return True
        return False

    def save(self, file_name):
        if self.map_data:
            f = open(file_name, 'wb')
            for block in self.map_data:
                f.write(block)
            f.close()
            return True
        return False

    def new(self):
        self.map_data = []
        for x in xrange(self.map_x):
            self.map_data += [ chr(0) * MapBlock.size * self.map_y ]

    def get_block(self, x, y):
        s = self.get_block_raw(x, y)
        mb = MapBlock()
        mb.parse(s)
        return mb

    def get_block_raw(self, x, y):
        start = y * MapBlock.size
        return self.map_data[x][ start : start + MapBlock.size ]

    def get_blockx_raw(self, x):
        return self.map_data[x]

    def get_cell(self, x, y):
        block = self.get_block(x / 8, y / 8)
        return block.get_cell(x % 8, y % 8)

    def set_block(self, x, y, block=None):
        data = block
        if isinstance(block, MapBlock):
            data = block.binarize()
        elif isinstance(block, list):
            if len(list) == 64:
                data = chr(0) * 4
                for cell in block:
                    data += pack("<Hb", cell[0], cell[1])
        if data:
            start = y * MapBlock.size
            self.map_data[x] = self.map_data[x][ : start ] + data + self.map_data[x][ start + len(data) : ]
            return True
        return False

    def set_cell(self, x, y, cell=None, alt=None):
        # if alt is given, cell must be an integer.
        celldata = None
        if alt:
            celldata = pack("<Hb", cell, alt)
        else:
            celldata = pack("<Hb", cell[0], cell[1])
        if celldata:
            block_x = x / 8
            block_y = y / 8
            x = x % 8
            y = y % 8
            start = (block_y * MapBlock.size) + ((y * 8 + x % 8) * 3) + 4
            self.map_data[block_x] = self.map_data[block_x][:start] + celldata + self.map_data[block_x][ start + len(celldata): ]
            return True
        return False

class MapCacheSingular(MapCache):
    """uses a single string to save data.
    specialities: very fast in reading data, very efficient for saves without changes"""
    def __init__(self, file_name):
        super(MapCacheSingular, self).__init__(file_name)

    def load(self, file_name):
        if os.path.exists(file_name):
            f = open(file_name, 'rb')
            self.map_data = f.read()
            f.close()
            return True
        return False

    def save(self, file_name):
        if self.map_data:
            f = open(file_name, 'wb')
            f.write(self.map_data)
            f.close()
            return True
        return False

    def new(self):
        self.map_data = chr(0) * self.size

    def get_block_raw(self, x, y):
        start = ((x * self.map_y) + y) * MapBlock.size
        return self.map_data[ start : start + MapBlock.size ]

    def get_blockx_raw(self, x):
        start = (x * self.map_y) * MapBlock.size
        return self.map_data[start : start + MapBlock.size * self.map_y]

    def set_block(self, x, y, block=None):
        data = block
        if isinstance(block, MapBlock):
            data = block.binarize()
        elif isinstance(block, list):
            if len(list) == 64:
                data = chr(0) * 4
                for cell in block:
                    data += pack("<Hb", cell[0], cell[1])
        if data:
            start = ((x * self.map_y) + y) * MapBlock.size
            self.map_data = self.map_data[ : start ] + data + self.map_data[ start + len(data) : ]
            return True
        return False

    def set_cell(self, x, y, cell=None, alt=None):
        # if alt is given, cell must be an integer.
        celldata = None
        if alt:
            celldata = pack("<Hb", cell, alt)
        else:
            celldata = pack("<Hb", cell[0], cell[1])
        if celldata:
            block_x = x / 8
            block_y = y / 8
            x = x % 8
            y = y % 8
            start = ((block_x * self.map_y) + block_y) * MapBlock.size + ((y * 8 + x % 8) * 3) + 4
            self.map_data = self.map_data[:start] + celldata + self.map_data[ start + len(celldata): ]
            return True
        return False

class MapFile(MapHandler):
    """writes everything directly to the file.
    specialities: low memory consumption, ideal on fast file systems and for small changes"""
    def __init__(self, file_name=None):
        if file_name:
            self.load(file_name)

    def load(self, file_name=None):
        """just opens the read-write handle, actually"""
        self.file_name = file_name
        self.handle = open(file_name, 'rwb')

    def save(self, file_name=None):
        """
        well, we read and save the whole file.
        we do it in smaller blocks, to minimize memory consumption
        since this handler might me used by low-mem operations only.
        """
        if self.file_name == file_name:
            # we dont need to save in the same file.
            return True
        elif self.handle is None:
            return False
        self.handle.seek(0)
        nf = open(file_name, 'wb')
        for y in xrange(self.map_y):
            nf.write(self.handle.read(MapBlock.size * self.map_x))
        nf.close()
        return True

    def get_block(self, x, y):
        # load the mapblock
        self.handle.seek((x * self.map_y + y) * MapBlock.size)
        block = MapBlock()
        block.parse(self.handle.read(MapBlock.size))
        return block

    def get_block_raw(self, x, y):
        self.handle.seek((x * self.map_y + y) * MapBlock.size)
        return self.handle.read(MapBlock.size)

    def get_blockx_raw(self, x):
        self.handle.seek((x * self.map_y) * MapBlock.size)
        return self.handle.read(MapBlock.size * self.map_y)

    def get_cell(self, x, y):
        block = self.get_block(x / 8, y / 8)
        return block.get_cell(x % 8, y % 8)

    def new(self):
        raise Exception("You cant define a new map with MapFile Handler!")

    def set_block(self, x, y, block):
        """writes a whole block into the file.
        the block may be a list of length 64, a MapBlock object, or a raw string"""
        data = block
        if isinstance(block, MapBlock):
            data = block.binarize()
        elif isinstance(block, list):
            if len(list) == 64:
                data = chr(0) * 4
                for cell in block:
                    data += pack("<Hb", cell[0], cell[1])
        if data:
            self.handle.seek((x * self.map_y + y) * MapBlock.size)
            self.handle.write(data)
            return True
        return False

    def set_cell(self, x, y, cell, alt=None):
        """very inperformant, writes a three byte cell into the map"""
        celldata = None
        if alt:
            celldata = pack("<Hb", cell, alt)
        else:
            celldata = pack("<Hb", cell[0], cell[1])
        if celldata:
            block_x = x / 8
            block_y = y / 8
            x = x % 8
            y = y % 8
            self.handle.seek((block_x * self.map_y + block_y) * MapBlock.size + ((y * 8 + x) * 3) + 4)
            self.handle.write(celldata)
            return True
        return False

class Map(MapHandler):
    """
    The Map Object allows Map Operations
    It tries to execute optimized operations with a custom MapHandler
    It can use a writer and a reader instance, to optimize performance.
    """
    map_writer = None
    map_reader = None
    use_write_cache = True
    def __init__(self, file_name=None, InputClass=MapCache, OutputClass=None):
        self.file_name = file_name
        if InputClass is not None:
            class Input(InputClass):
                map_x = self.map_x
                map_y = self.map_y
            self.map_reader = Input(file_name)
        else:
            raise Exception("You need an InputClass in Map")
        if OutputClass is not None:
            class Output(OutputClass):
                map_x = self.map_x
                map_y = self.map_y
            self.map_writer = Output(file_name)
        else:
            self.map_writer = self.map_reader

    def get_block(self, block_x, block_y):
        return self.map_reader.get_block(block_x, block_y)

    def get_block_raw(self, block_x, block_y):
        return self.map_reader.get_block_raw(block_x, block_y)

    def set_block(self, block_x, block_y, block):
        return self.map_writer.set_block(block_x, block_y, block)

    def get_cell(self, cell_x, cell_y):
        return self.map_reader.get_cell(cell_x, cell_y)

    def set_cell(self, cell_x, cell_y, cell):
        return self.map_writer.set_cell(cell_x, cell_y, cell)

    def new(self):
        self.map_reader.new()
        if self.map_writer != self.map_reader:
            self.map_writer.new()

    def load(self, file_name):
        self.file_name = file_name
        self.map_reader.load(file_name)

    def save(self, file_name):
        self.map_writer.save(file_name)
