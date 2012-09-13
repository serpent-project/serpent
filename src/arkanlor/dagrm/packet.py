# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    Unit Description

@author: g4b

LICENSE AND COPYRIGHT NOTICE:

Copyright (C) 2012 by  Gabor Guzmics, <gab(at)g4b(dot)org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""
from arkanlor.dagrm.const import *
import struct, string #@UnresolvedImport

def packet_list(*packets):
    ret = {}
    for packet in packets:
        ret[packet.p_id] = packet
    return ret

class ReadWriteDatagram:
    def __init__(self, r_d, w_d):
        self.r_d = r_d
        self.w_d = w_d

    def get_read_datagram(self):
        return self.r_d
    def get_write_datagram(self):
        return self.w_d

class DatagramManipulator(object):
    """
        A datagram manipulator can manipulate the flow of packetreading
        Mainly it is used for Subpackets.
         
    """
    __slots__ = []
    def packet_read(self, values, data, instance=None):
        # only use instance to read and write data
        return values, data
    def packet_write(self, values, data, instance=None):
        # only use instance to read and write data
        return values, data

class SubPackets(DatagramManipulator):
    __slots__ = ['packets', 'identifier']
    def __init__(self, identifier, *packets):
        self.packets = packet_list(*packets)
        self.identifier = identifier

    def packet_read(self, values, data, instance=None):
        """
            reads a subpacket with p_id from data into values.
            returns values, data
        """
        # read our identifier
        if not self.identifier:
            raise DatagramException('Subpackets without identifier')
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

    def packet_write(self, values, data, instance=None):
        """
            writes a subpacket with p_id from values into data.
            returns values, data
        """
        if not self.identifier:
            raise DatagramException('Subpackets without identifier')
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
        else:
            self.values = {}
            self._data = ''
            self.set_initial_arg(packet_or_values)

    def set_initial_arg(self, arg):
        pass

    def __repr__(self):
        try:
            return self.__unicode__()
        except:
            return self.__class__.__name__

    def read_data(self, length):
        if len(self._data) < length:
            raise DatagramException("Packet is too short P_ID: %s, values %s" % (
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
        if isinstance(datagram, ReadWriteDatagram):
            datagram = datagram.get_read_datagram()
        if values is None:
            values = self.values
        for item in datagram:
            if isinstance(item, DatagramManipulator):
                # subpacket read
                values, self._data = item.packet_read(values,
                                                      self._data,
                                                      self)
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
            elif t == SHORT:
                values[key] = self.r_short()
            elif t == UINT:
                values[key] = self.r_uint()
            elif t == INT:
                values[key] = self.r_int()
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
                    raise DatagramException('Unknown Packet in Datagram')

    def write_datagram(self, datagram, values=None):
        if isinstance(datagram, ReadWriteDatagram):
            datagram = datagram.get_write_datagram()
        if values is None:
            values = self.values
        for item in datagram:
            if isinstance(item, DatagramManipulator):
                # subpacket write.
                values, self._data = item.packet_write(values, self._data,
                                                       self)
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
                elif t == SHORT:
                    self.w_short(d)
                elif t == UINT:
                    self.w_uint(d)
                elif t == INT:
                    self.w_int(d)
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
                    raise DatagramException('Unknown Packet in Datagram')
            except DatagramException, e:
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
        try:
            self._datagram
        except AttributeError, e:
            raise DatagramException('Packet %s has no datagram.' % self)
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
                raise DatagramException, "Packet too large"
            data = data[0] + struct.pack('%sH' % self.flow, len(data) + 2) + data[1:]
        else:
            if len(data) != self.p_length:
                print 'pid: %s, expected: %s, got: %s, data: %s' % (
                                        hex(self.p_id), self.p_length,
                                        len(data), repr(data))
                raise DatagramException, "Invalid packet length"
        return data

    def r_uint(self):
        """ 4 bytes unsigned integer """
        return struct.unpack('%sI' % self.flow, self.read_data(4))[0]

    def r_int(self):
        """ 4 bytes signed integer """
        return struct.unpack('%si' % self.flow, self.read_data(4))[0]

    def r_ushort(self):
        """ 2 bytes unsigned integer """
        return struct.unpack('%sH' % self.flow, self.read_data(2))[0]

    def r_short(self):
        """ 2 bytes signed integer """
        return struct.unpack('%sh' % self.flow, self.read_data(2))[0]

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
        return string.join(map(str, struct.unpack('%s4B' % self.flow, self.read_data(4))), '.')

    ### Writing

    def w_uint(self, x):
        self.write_data(struct.pack('%sI' % self.flow, x))

    def w_int(self, x):
        self.write_data(struct.pack('%si' % self.flow, x))

    def w_ushort(self, x):
        assert x >= 0 and x < 65536
        self.write_data(struct.pack('%sH' % self.flow, x))

    def w_short(self, x):
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
        x = str(x)
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
            self.write_data(struct.pack('%s4B' % self.flow, *map(int, x.split('.'))))
        elif isinstance(x, list):
            self.write_data(struct.pack('%s4B' % self.flow, *x))
        else:
            raise DatagramException, "Ipv4 invalid?"

class PacketReader(object):
    """
        Use a PacketReader to initialize your packets from your protocol.
    """
    __slots__ = ['packet_set', 'minimal_packet_size', 'dataflow',
                 'lengthtype', 'maximal_packet_size']
    minimal_packet_size = 3 # byte + ushort len
    maximal_packet_size = None
    dataflow = '>' # ux
    lengthtype = 'H' # ushort

    class UnknownPacketException(DatagramException):
        pass
    class MalformedPacketException(DatagramException):
        pass

    def __init__(self, packet_set):
        self.packet_set = packet_set

    def check_length(self, cmd, length=None):
        """
            check a length of a packet for any secondary lookups.
        """
        return length or 0

    def read_from_buffer(self, buffer):
        """
            returns:
            None (not enough data) OR
            rest-of-buffer, cmd, packet-data 
        """
        if buffer == '':
            return None
        cmd = ord(buffer[0])
        p = self.packet_set.get(cmd, None)
        if not p:
            raise PacketReader.UnknownPacketException('Unknown Packet Type %s' % cmd)
        try:
            l = int(p.p_length)
        except:
            l = None
        l = self.check_length(cmd, l)
        if l == 0: # dynamic packet.
            if len(buffer) < self.minimal_packet_size: return None
            l = struct.unpack('%s%s' % (self.dataflow, self.lengthtype),
                              buffer[1:self.minimal_packet_size])[0]
            if l < self.minimal_packet_size or (self.maximal_packet_size and\
                                                l > self.maximal_packet_size):
                raise PacketReader.MalformedPacketException(
                      "Malformed packet %s" % hex(cmd))
            if len(buffer) < l: return None
            packet_data, buffer = buffer[self.minimal_packet_size:l], buffer[l:]
        else: # fixed size packet.
            if len(buffer) < l: return None
            packet_data, buffer = buffer[1:l], buffer[l:]
        return (buffer, cmd, packet_data)

    def init_packet(self, cmd, packet_data):
        """
            creates packet out of cmd and data and calls it to parse itself.
            length is already removed.
        """
        packet_class = self.packet_set.get(cmd, None)
        if packet_class is None:
            raise PacketReader.UnknownPacketException('Packet not in Parsing list: %s' % cmd)
        else:
            packet = packet_class(packet_data)
        packet = packet.unpack()
        return packet

