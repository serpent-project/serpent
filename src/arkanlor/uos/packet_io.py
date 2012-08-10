# -*- coding: utf-8 -*-
"""
    PacketIO Library for binary packetformats used in UO Protocol.
    Packet tries to define a new-style object packet with complete read/write built in.
    Theoretically this approach should be even optimal,
    however the creation of a dictionary in the packet still needs a bit of horsepower.
    
    The old static approach worked well too, however this packet class allows
    the definition of a standard datagram, enabling most packets to be defined
    with _datagram = [ ( identifier, type ), ( 'name', FIXSTRING, 30 ), ... ]
    
"""
import struct, string #@UnresolvedImport

BOOLEAN = 0
BYTE = 1
USHORT = 2
UINT = 4
IPV4 = 5
#IPV6 = 6
FIXSTRING = 30
CSTRING = 40
UCSTRING = 41
PSTRING = 50
RAW = 255 # read rest of packet. write out directly.

packet_lengths = [
    0x0068, 0x0005, 0x0007, 0x0000, 0x0002, 0x0005, 0x0005, 0x0007, # 0x00
    0x000e, 0x0005, 0x0007, 0x0007, 0x0000, 0x0003, 0x0000, 0x003d, # 0x08
    0x00d7, 0x0000, 0x0000, 0x000a, 0x0006, 0x0009, 0x0001, 0x0000, # 0x10
    0x0000, 0x0000, 0x0000, 0x0025, 0x0000, 0x0005, 0x0004, 0x0008, # 0x18
    0x0013, 0x0008, 0x0003, 0x001a, 0x0007, 0x0014, 0x0005, 0x0002, # 0x20
    0x0005, 0x0001, 0x0005, 0x0002, 0x0002, 0x0011, 0x000f, 0x000a, # 0x28
    0x0005, 0x0001, 0x0002, 0x0002, 0x000a, 0x028d, 0x0000, 0x0008, # 0x30
    0x0007, 0x0009, 0x0000, 0x0000, 0x0000, 0x0002, 0x0025, 0x0000, # 0x38
    0x00c9, 0x0000, 0x0000, 0x0229, 0x02c9, 0x0005, 0x0000, 0x000b, # 0x40
    0x0049, 0x005d, 0x0005, 0x0009, 0x0000, 0x0000, 0x0006, 0x0002, # 0x48
    0x0000, 0x0000, 0x0000, 0x0002, 0x000c, 0x0001, 0x000b, 0x006e, # 0x50
    0x006a, 0x0000, 0x0000, 0x0004, 0x0002, 0x0049, 0x0000, 0x0031, # 0x58
    0x0005, 0x0009, 0x000f, 0x000d, 0x0001, 0x0004, 0x0000, 0x0015, # 0x60
    0x0000, 0x0000, 0x0003, 0x0009, 0x0013, 0x0003, 0x000e, 0x0000, # 0x68
    0x001c, 0x0000, 0x0005, 0x0002, 0x0000, 0x0023, 0x0010, 0x0011, # 0x70
    0x0000, 0x0009, 0x0000, 0x0002, 0x0000, 0x000d, 0x0002, 0x0000, # 0x78
    0x003e, 0x0000, 0x0002, 0x0027, 0x0045, 0x0002, 0x0000, 0x0000, # 0x80
    0x0042, 0x0000, 0x0000, 0x0000, 0x000b, 0x0000, 0x0000, 0x0000, # 0x88
    0x0013, 0x0041, 0x0000, 0x0063, 0x0000, 0x0009, 0x0000, 0x0002, # 0x90
    0x0000, 0x001a, 0x0000, 0x0102, 0x0135, 0x0033, 0x0000, 0x0000, # 0x98
    0x0003, 0x0009, 0x0009, 0x0009, 0x0095, 0x0000, 0x0000, 0x0004, # 0xA0
    0x0000, 0x0000, 0x0005, 0x0000, 0x0000, 0x0000, 0x0000, 0x000d, # 0xA8
    0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0040, 0x0009, 0x0000, # 0xB0
    0x0000, 0x0003, 0x0006, 0x0009, 0x0003, 0x0000, 0x0000, 0x0000, # 0xB8
    0x0024, 0x0000, 0x0000, 0x0000, 0x0006, 0x00cb, 0x0001, 0x0031, # 0xC0
    0x0002, 0x0006, 0x0006, 0x0007, 0x0000, 0x0001, 0x0000, 0x004e, # 0xC8
    0x0000, 0x0002, 0x0019, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, # 0xD0
    0x0000, 0x010C, 0xFFFF, 0xFFFF, 0x0009, 0x0000, 0xFFFF, 0xFFFF, # 0xD8
    0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, # 0xE0
    0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, # 0xE8
    0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, # 0xF0
    0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0x0003, # 0xF8
]

class Packet(object):
    # see euclid.py for further optimizations.
    __slots__ = [ 'p_id', 'p_type', 'p_length', '_datagram', '_data', 'values' ]
    p_id = None
    p_type = None
    p_length = None
    _data = None
    _datagram = []
    values = None

    def __init__(self, packet_or_values=None):
        if isinstance(packet_or_values, basestring):
            self._data = packet_or_values
            self.values = {}
        elif isinstance(packet_or_values, dict):
            self.values = packet_or_values
            self._data = ''
        elif packet_or_values is None:
            self.values = {}
            self._data = ''
        if self.p_id:
            self.p_length = packet_lengths[self.p_id]

    def __repr__(self):
        try:
            return self.__unicode__()
        except:
            return self.__class__.__name__

    def read_data(self, length):
        if len(self._data) < length:
            raise Exception("Packet is too short")
        x, self._data = self._data[:length], self._data[length:]
        return x

    def write_data(self, data):
        self._data += data

    def updated(self, **kwargs):
        """ updates values with kwargs and returns self """
        if not self.values:
            self.values = {}
        for key in kwargs.keys():
            self.values[key] = kwargs[key]
        return self

    def unpack(self):
        if self._datagram:
            for item in self._datagram:
                l, key, t, item = None, item[0], item[1], item[2:]
                if item: # optional argument length
                    l = item[0]
                if not t:
                    self.values[key] = self.r_boolean()
                elif t == BYTE:
                    self.values[key] = self.r_byte()
                elif t == USHORT:
                    self.values[key] = self.r_ushort()
                elif t == UINT:
                    self.values[key] = self.r_uint()
                elif t == IPV4:
                    self.values[key] = self.r_ipv4()
                elif t == FIXSTRING:
                    self.values[key] = self.r_fixstring(l)
                elif t == CSTRING:
                    self.values[key] = self.r_cstring()
                elif t == PSTRING:
                    self.values[key] = self.r_pstring()
                elif t == RAW:
                    # thats tricky.
                    # we read until nothing is left, actually
                    self.values[key], self._data = self._data, ''
                else:
                    if l:
                        self.values[key] = self.read_data(l)
                    else:
                        raise Exception('Unknown Packet in Datagram')
        return self

    def serialize(self):
        self.begin()
        if self._datagram:
            for item in self._datagram:
                l, key, t, item = None, item[0], item[1], item[2:]
                if item: # optional argument length
                    l = item[0]
                d = self.values.get(key, None)
                if d is None:
                    if t < FIXSTRING:
                        d = 0
                    else:
                        d = ''
                if not t:
                    self.w_boolean(d)
                elif t == BYTE:
                    self.w_byte(d)
                elif t == USHORT:
                    self.w_ushort(d)
                elif t == UINT:
                    self.w_uint(d)
                elif t == IPV4:
                    self.w_ipv4(d)
                elif t == FIXSTRING:
                    self.w_fixstring(d, l)
                elif t == CSTRING:
                    self.w_cstring(d)
                elif t == PSTRING:
                    self.w_boolean(d)
                elif t == RAW:
                    self.write_data(d)
                else:
                    raise Exception('Unknown Packet in Datagram')
        return self.finish(self._data)

    def begin(self):
        self._data = ''
        self.w_byte(self.p_id)

    def finish(self, data):
        if self.p_length == 0:
            if len(data) > 0xf000:
                raise Exception, "Packet too large"
            data = data[0] + struct.pack('>H', len(data) + 2) + data[1:]
        else:
            if len(data) != self.p_length:
                print 'pid: %s, expected: %s, got: %s, data: %s' % (
                                        hex(self.p_id), self.p_length,
                                        len(data), repr(data))
                raise Exception, "Invalid packet length"
        return data

    def r_uint(self):
        """ 4 bytes unsigned integer """
        return struct.unpack('>I', self.read_data(4))[0]

    def r_ushort(self):
        """ 2 bytes unsigned integer """
        return struct.unpack('>H', self.read_data(2))[0]

    def r_byte(self):
        """ 1 byte """
        return struct.unpack('>B', self.read_data(1))[0]

    def r_boolean(self):
        """ 1 byte != 0 """
        return self.r_byte() != 0

    def r_fixstring(self, length):
        return self.read_data(length).replace('\0', '')

    def r_cstring(self):
        i = self._data.index('\0')
        x, self._data = self._data[:i], self._data[i + 1:]
        return x

    def r_pstring(self):
        return self.r_fixstring(self.r_byte())

    def r_ipv4(self):
        return string.join(map(str, struct.unpack('4B', self.read_data(4))), '.')

    ### Writing

    def w_uint(self, x):
        self.write_data(struct.pack('>I', x))

    def w_ushort(self, x):
        assert x >= 0 and x < 65536
        self.write_data(struct.pack('>H', x))

    def w_sshort(self, x):
        assert x >= -32768 and x < 32768
        self.write_data(struct.pack('>h', x))

    def w_byte(self, x):
        assert x >= 0 and x < 256
        self.write_data(struct.pack('>B', x))

    def w_sbyte(self, x):
        assert x >= -128 and x < 128
        self.write_data(struct.pack('>b', x))

    def w_boolean(self, x):
        if x:
            self.w_byte(1)
        else:
            self.w_byte(0)

    def w_fixstring(self, x, length):
        if len(x) > length:
            x = x[:length]
        self.write_data(x)
        self.write_data('\0' * (length - len(x)))

    def w_cstring(self, x):
        self.write_data(x)
        self.w_byte(0)

    def w_ucstring(self, x):
        for ch in x:
            self.w_ushort(ord(ch))
            self.w_ushort(0)

    def w_pstring(self, x):
        assert len(x) < 255
        self.w_byte(len(x))
        self.w_fixstring(x, len(x))

    def w_ipv4(self, x):
        if isinstance(x, basestring):
            self.write_data(struct.pack('4B', *map(int, x.split('.'))))
        elif isinstance(x, list):
            self.write_data(struct.pack('4B', *x))
        else:
            raise Exception, "Ipv4 invalid?"
