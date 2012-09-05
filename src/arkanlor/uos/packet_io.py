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
SBYTE = 6
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
    0xFFFF, 0xFFFF, 0xFFFF, 0x0018, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, # 0xF0
    0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0x0003, # 0xF8
]

def packet_list(*packets):
    ret = {}
    for packet in packets:
        ret[packet.p_id] = packet
    return ret

class SubPackets(object):
    __slots__ = ['packets', 'identifier']
    def __init__(self, identifier, *packets):
        self.packets = packet_list(*packets)
        self.identifier = identifier

    def packet_read(self, values, data):
        """
            reads a subpacket with p_id from data into values.
            returns values, data
        """
        # read our identifier
        if not self.identifier:
            raise Exception('Subpackets without identifier')
        else:
            p_id = values.get(self.identifier, None)
        if not p_id:
            return values, data
        packet_class = self.packets.get(p_id, None)
        if packet_class is None:
            print "read: subpacket id %s not understood." % hex(p_id)
        else:
            # instanciate the packet class
            # set data and values
            # write out packet
            # return our updated values and the rest of the data
            p = packet_class(values)
            p._data = data
            p.unpack()
            values.update(p.values)
            data = p._data
        return values, data

    def packet_write(self, values, data):
        """
            writes a subpacket with p_id from values into data.
            returns values, data
        """
        if not self.identifier:
            raise Exception('Subpackets without identifier')
        else:
            p_id = values.get(self.identifier, None)
        if not p_id:
            return values, data
        packet_class = self.packets.get(p_id, None)
        if packet_class is None:
            print "write: subpacket id %s not understood." % hex(p_id)
        else:

            # instanciate the packet class
            # set data and values
            p = packet_class(data)
            p.values = values
            # write out packet
            p._serialize()
            # return our updated values and the rest of the data
            values.update(p.values)
            data = p._data
        return values, data

class Packet(object):
    # see euclid.py for further optimizations.
    __slots__ = [ 'p_id', 'p_type', 'p_length', '_datagram', '_data', 'values',
                  ]
    p_id = None
    p_type = None
    p_length = None

    _data = None
    _datagram = []
    values = None

    def get_flow(self):
        return '>'
    flow = property(get_flow)

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

    def __repr__(self):
        try:
            return self.__unicode__()
        except:
            return self.__class__.__name__

    def read_data(self, length):
        if len(self._data) < length:
            raise Exception("Packet is too short P_ID: %s, values %s" % (
                                            hex(self.p_id),
                                            self.values
                                            ))
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

    def read_datagram(self, datagram, values=None):
        if values is None:
            values = self.values
        for item in datagram:
            if isinstance(item, SubPackets):
                # subpacket read
                values, self._data = item.packet_read(values,
                                                      self._data)
                continue
            l, key, t, item = None, item[0], item[1], item[2:]
            if item: # optional argument length
                l = item[0]
            if not t:
                values[key] = self.r_boolean()
            elif t == BYTE:
                values[key] = self.r_byte()
            elif t == SBYTE:
                values[key] = self.r_sbyte()
            elif t == USHORT:
                values[key] = self.r_ushort()
            elif t == UINT:
                values[key] = self.r_uint()
            elif t == IPV4:
                values[key] = self.r_ipv4()
            elif t == FIXSTRING:
                values[key] = self.r_fixstring(l)
            elif t == CSTRING:
                values[key] = self.r_cstring()
            elif t == UCSTRING:
                values[key] = self.r_ucstring()
            elif t == PSTRING:
                values[key] = self.r_pstring()
            elif t == RAW:
                # thats tricky.
                # we read until nothing is left, actually
                values[key], self._data = self._data, ''
            else:
                if l:
                    values[key] = self.read_data(l)
                else:
                    raise Exception('Unknown Packet in Datagram')

    def write_datagram(self, datagram, values=None):
        if values is None:
            values = self.values
        for item in datagram:
            if isinstance(item, SubPackets):
                # subpacket write.
                values, self._data = item.packet_write(values, self._data)
                continue
            _d, l, key, t, item = None, None, item[0], item[1], item[2:]
            if item: # optional argument length
                l, item = item[0], item[1:]
            if item:
                _d = item[0]
            d = values.get(key, None)
            if d is None:
                if _d:
                    d = _d
                elif t < FIXSTRING:
                    d = 0
                else:
                    d = ''
            try:
                if not t:
                    self.w_boolean(d)
                elif t == BYTE:
                    self.w_byte(d)
                elif t == SBYTE:
                    self.w_sbyte(d)
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
                elif t == UCSTRING:
                    self.w_ucstring(d)
                elif t == PSTRING:
                    self.w_boolean(d)
                elif t == RAW:
                    self.write_data(d)
                else:
                    raise Exception('Unknown Packet in Datagram')
            except Exception, e:
                print "="*80
                print "datagram write exception"
                print e
                print "-"*80
                print "type(d): %s, d=%s" % (type(d), str(d))
                print "type(t): %s, t=%s" % (type(t), str(t))
                print "="*80
                raise

    def _unpack(self):
        return self

    def unpack(self):
        if self._datagram:
            self.read_datagram(self._datagram)
        return self._unpack()

    def _serialize(self):
        if self._datagram:
            self.write_datagram(self._datagram)

    def serialize(self):
        self.begin()
        self._serialize()
        return self.finish(self._data)

    def begin(self):
        self._data = ''
        self.w_byte(self.p_id)

    def finish(self, data=None):
        if data is None:
            data = self._data
        if self.p_length == 0:
            if len(data) > 0xf000:
                raise Exception, "Packet too large"
            data = data[0] + struct.pack('%sH' % self.flow, len(data) + 2) + data[1:]
        else:
            if len(data) != self.p_length:
                print 'pid: %s, expected: %s, got: %s, data: %s' % (
                                        hex(self.p_id), self.p_length,
                                        len(data), repr(data))
                raise Exception, "Invalid packet length"
        return data

    def r_uint(self):
        """ 4 bytes unsigned integer """
        return struct.unpack('%sI' % self.flow, self.read_data(4))[0]

    def r_ushort(self):
        """ 2 bytes unsigned integer """
        return struct.unpack('%sH' % self.flow, self.read_data(2))[0]

    def r_byte(self):
        """ 1 byte """
        return struct.unpack('%sB' % self.flow, self.read_data(1))[0]

    def r_sbyte(self):
        """ 1 byte signed """
        return struct.unpack('%sb' % self.flow, self.read_data(1))[0]

    def r_boolean(self):
        """ 1 byte != 0 """
        return self.r_byte() != 0

    def r_fixstring(self, length):
        return self.read_data(length).replace('\0', '')

    def r_cstring(self):
        i = self._data.index('\0')
        x, self._data = self._data[:i], self._data[i + 1:]
        return x

    def r_ucstring(self):
        s = ''
        x = None
        while not x or x != '\0\0':
            if x:
                s += x
            x = self.r_fixstring(2)
        return s.decode('utf-16')


    def r_pstring(self):
        return self.r_fixstring(self.r_byte())

    def r_ipv4(self):
        return string.join(map(str, struct.unpack('4B', self.read_data(4))), '.')

    ### Writing

    def w_uint(self, x):
        self.write_data(struct.pack('%sI' % self.flow, x))

    def w_ushort(self, x):
        assert x >= 0 and x < 65536
        self.write_data(struct.pack('%sH' % self.flow, x))

    def w_sshort(self, x):
        assert x >= -32768 and x < 32768
        self.write_data(struct.pack('%sh' % self.flow, x))

    def w_byte(self, x):
        assert x >= 0 and x < 256
        self.write_data(struct.pack('%sB' % self.flow, x))

    def w_sbyte(self, x):
        assert x >= -128 and x < 128
        self.write_data(struct.pack('%sb' % self.flow, x))

    def w_boolean(self, x):
        if x:
            self.w_byte(1)
        else:
            self.w_byte(0)

    def w_fixstring(self, x, length):
        if len(x) > length:
            x = x[:length]
        # ensure str
        x = str(x)
        self.write_data(x)
        self.write_data('\0' * (length - len(x)))

    def w_cstring(self, x):
        self.write_data(x)
        self.w_byte(0)

    def w_ucstring(self, x):
        s = x.encode('utf-16')
        self.w_fixstring(s, len(s))
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

class UOPacket(Packet):
    # see euclid.py for further optimizations.
    __slots__ = [ 'p_id', 'p_type', 'p_length', '_datagram', '_data', 'values' ]
    p_id = None
    p_length = None

    def __init__(self, packet_or_values=None):
        super(UOPacket, self).__init__(packet_or_values)
        if self.p_id:
            self.p_length = packet_lengths[self.p_id]
