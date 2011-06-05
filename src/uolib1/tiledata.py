# -*- coding: utf-8 -*-

from const import tiledata_flags
from struct import pack, unpack

def clean_up_name(td):
    name = td.name.split('\x00')[0]
    if len(name) < 20:
        name += '\x00' * (20 - len(name))
    elif len(name) > 20:
        name = name[:20]
    return name

def flags_list(td):
    ret = []
    for i in tiledata_flags.keys():
        if i & td.flags:
            ret += [ tiledata_flags[i] ]
    return ret

def clear_unknowns(td):
    """
        clears the unknown paramaters in a tiledata.
    """
    td.unknown = 0
    td.unknown1 = 0
    td.unknown2 = 0
    # td.unknown3 = 0 # light orientation.
    
class TileDataEntry( object ):
    flags = 0
    id = 0
    name = ""
    
    def __init__(self, *args):
        if len(args) == 3:
            self.flags = args[0]
            self.id = args[1]
            self.name = args[2]
        else:
            self.flags = 0
            self.id = 0
            self.name = ""

class LandTileData( TileDataEntry ):
    """
        512 blocks of 32 entries (0x4000 entries)
        L flags
        H Texture ID
        s[20] tile name
    """
    data_length = 26
    pack_format = "LH20s"
    
    def unpack(self, data):
        (self.flags, self.id, self.name) = unpack("<" + self.pack_format, data)
    
    def pack(self):
        return pack( "<" + self.pack_format, self.flags, self.id, self.name )
    
    def __eq__(self, other):
        if isinstance(other, LandTileData):
            if other.flags == self.flags and other.id == self.id and other.name == self.name:
                return True
        return False
    
    def __list__(self):
        return [ self.flags, self.id, self.name ]

class StaticTileData( TileDataEntry ):
    """
        L Flags
        b Weight
        b Quality
        H Unknown
        b Unknown1
        b Quantity
        H AnimID
        b Unknown2
        b Hue
        H Unknown3 # lightsource.
        b Height
        s[20] Name
    """
    pack_format = "LBBHBBHBBHB20s"
    data_length = 37
    weight = 0
    quality = 0
    quantity = 0
    hue = 0
    height = 0
    unknown = 0
    unknown1 = 0
    unknown2 = 0
    unknown3 = 0
    
    def __init__(self, *args):
        if len(args) == 12:
            self.flags = args[0]
            self.id = args[6]
            self.name = args[11]
            self.weight = args[1]
            self.quality = args[2]
            self.quantity = args[5]
            self.hue = args[8]
            self.height = args[10]
            self.unknown = args[3]
            self.unknown1 = args[4]
            self.unknown2 = args[7]
            self.unknown3 = args[9]
        else:
            TileDataEntry.__init__(self)
            self.weight = 0
            self.quality = 0
            self.quantity = 0
            self.hue = 0
            self.height = 0
            self.unknown = 0
            self.unknown1 = 0
            self.unknown2 = 0
            self.unknown3 = 0
    
    def unpack(self, data):
        (self.flags, self.weight, self.quality, self.unknown, 
         self.unknown1, self.quantity, self.id, self.unknown2, 
         self.hue, self.unknown3, self.height, self.name) = unpack("<" + self.pack_format, data)
    
    def pack(self):
        return pack( "<" + self.pack_format, self.flags, self.weight, self.quality, self.unknown,
                     self.unknown1, self.quantity, self.id, self.unknown2, self.hue, self.unknown3,
                     self.height, self.name )
    
    def __eq__(self, other):
        if isinstance(other, StaticTileData):
            if (other.flags == self.flags and other.id == self.id and other.name == self.name and
            other.weight == self.weight and other.quality == self.quality and other.quantity == self.quantity and
            other.hue == self.hue and other.height == self.height and other.unknown == self.unknown and
            other.unknown1 == self.unknown1 and other.unknown2 == self.unknown2 and other.unknown3 == self.unknown3):
                return True
        return False
    
    def __list__(self):
        return [ self.flags, self.weight, self.quality, self.unknown,
                     self.unknown1, self.quantity, self.id, self.unknown2, self.hue, self.unknown3,
                     self.height, self.name ]

class TileData( object ):
    static_tiledata = []
    land_tiledata = []
    unknown_data = []
    def __init__(self, file_name = None):
        self.file_name = file_name
        if self.file_name:
            self.load()
            
    def __getitem__(self, index):
        return self.get_entry(index)
    
    def __setitem__(self, index, value):
        if isinstance(value, StaticTileData):
            if index > 0x4000:
                self.static_tiledata[index - 0x4000] = value
            else:
                self.static_tiledata[index] = value
        elif isinstance(value, LandTileData):
            if index > 0x4000:
                self.land_tiledata[index - 0x4000] = value
            else:
                self.land_tiledata[index] = value
        else:
            raise Exception("Incorrect Data Assigned.")
    
    def __len__(self):
        return len(self.land_tiledata) + len(self.static_tiledata)
    
    def __eq__(self, to_what):
        if isinstance(to_what, TileData):
            mine = self.get_entry()
            his = to_what.get_entry()
            if len(mine) != len(his) or len(mine) == 0:
                return False
            for id in xrange(len(mine)):
                try:
                    if not his[id] == mine[id]:
                        return False
                except:
                    return False
            return True
        elif isinstance(to_what, str):
            try:
                obj = TileData(to_what)
                if obj:
                    return self.__eq__(obj)
            except:
                return False
            return False
        else:
            return False
            
    def load(self, file_name = None):
        if file_name:
            self.file_name = file_name
        if self.file_name:
            f = open(self.file_name, 'rb')
            buffer = f.read()
            f.close()
            if len(buffer) > 1034240:
                f = open('/home/g4b/dump', 'wb')
                f.write(buffer[1034240:])
                f.close()
            self.create_cache(buffer)
            return True
    
    def save(self, file_name):
        if file_name:
            f = open(file_name, 'wb')
            self.create_data_stream(f)
            f.close()
        
    def create_cache(self, buffer):
        self.land_tiledata = []
        self.static_tiledata = []
        self.unknown_data = []
        # first read the buffer to 0x4000 and create the landtiledata.
        for i in xrange(512):
            # read 32 blocks of land tile data
            self.unknown_data += [ unpack("<L", buffer[ i * 836: i * 836 + 4])[0] ]
            ltb = buffer[ 4 + i * 836: 4 + i * 836 + 32 * 26 ]
            for j in xrange(32):
                self.land_tiledata += [ LandTileData( *unpack("<" + LandTileData.pack_format, ltb[ j * 26: (j+1) * 26 ] ) ) ]
        skip = (32 * 26 + 4) * 512
        for i in xrange(512):
            # read 32 blocks of static tile data
            self.unknown_data += [ unpack("<L", buffer[ skip + i * 1188: skip + i * 1188 + 4])[0] ]
            stb = buffer[ skip + 4 + i * 1188: skip + 4 + i * 1188 + 32 * 37 ]
            for j in xrange(32):
                self.static_tiledata += [ StaticTileData( *unpack("<" + StaticTileData.pack_format, stb[ j * 37: (j+1) * 37 ] ) ) ]
    
    def create_data_stream(self, datastream = ""):
        if self.land_tiledata and self.static_tiledata:
            for i in xrange(512):
                group = pack("<L", self.unknown_data[ i ] )
                for j in xrange(32):
                    group += self.land_tiledata[ i * 32 + j ].pack()
                if isinstance(datastream, file):
                    datastream.write(group)
                else:
                    datastream += group
            for i in xrange(512):
                group = pack("<L", self.unknown_data[ i + 512 ] )
                for j in xrange(32):
                    group += self.static_tiledata[ i * 32 + j ].pack()
                if isinstance(datastream, file):
                    datastream.write(group)
                else:
                    datastream += group
        return datastream
        
    def get_entry(self, index = None):
        """
            returns a tiledata entry. 
            0x0-0x3FFF are landtiledata
            above are static tiledata
            if no index is given, it returns the whole tiledata.
        """
        if self.land_tiledata and index and index < 0x4000:
            return self.land_tiledata[index]
        elif self.static_tiledata and index:
            return self.static_tiledata[index]
        else:
            return self.land_tiledata + self.static_tiledata
    
    def set_unknowns(self, to_what = 0):
        for i in xrange(len(self.unknown_data)):
            self.unknown_data[i] = to_what


def test(file_name, file_name2):
    tiledata = TileData(  )
    tiledata.load(file_name)
    tiledata.set_unknowns(0)
    for i in xrange(len(tiledata.static_tiledata)):
        if i in [0x1cd9, 0x1cda, 0x1cdb, 0x1cdc ]:
            tiledata.static_tiledata[i].flags |= 0x00000008
            tiledata.static_tiledata[i].flags |= 0x00000004
        # clear_unknowns(tiledata.static_tiledata[i])
        
        #entries[i].flags = 0x0
    f = open(file_name2, 'wb')
    tiledata.create_data_stream(f)
    f.close()
    
def test_two(file_name, file_name2):
    tiledata = TileData(  )
    tiledata.load(file_name)
    tiledata2 = TileData()
    tiledata2.load(file_name2)
    entries1 = tiledata.get_entry()
    entries2 = tiledata2.get_entry()
    ok = 0
    d = 0
    for i in xrange(len(entries1)):
        entries1[i].name = clean_up_name(entries1[i])
        entries2[i].name = clean_up_name(entries2[i])
        if entries1[i].__list__() != entries2[i].__list__():
            print hex(i), hex(i- 0x4000), entries1[i].__list__(), entries2[i].__list__()
            d += 1
        else:
            ok += 1
    print "%s waren ok. %s verschieden." % (ok, d)

# test_two('/home/g4b/Spiele/Alathair/tiledata.mul', '/home/g4b/Spiele/Alathair.backup/tiledata.mul')
# test('/home/g4b/Spiele/Alathair/tiledata.ala', '/home/g4b/Spiele/Alathair/tiledata.mul')
